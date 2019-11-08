import boto3
import json
import time
import datetime
import os.path
import urllib
import ipaddress
from prettytable import PrettyTable


def convert_timestamp(item_date_object):
    # This function is for dealing with date/time values in JSON docs returned from AWS
    # From: https://www.kisphp.com/python/tutorials/convert-python-dictionaries-with-dates-into-json-format
    if isinstance(item_date_object, (datetime.date, datetime.datetime)):
        return item_date_object.timestamp()


def MakeCustomerGW(client):
    # Gather Customer GW Info:
    cgwName = input("Enter a name for the Customer Gateway: ")

    # Get BGP ASN, and make sure it's valid.
    asNumber = 0
    while asNumber == 0 or asNumber > 65534:
        try:
            asNumber = int(input("Enter your 16-bit BGP ASN (If you do not have your own ASN, use a private one [64512-65534]): "))
            if asNumber == 0 or asNumber > 65534:
                print("ASN input was out of range, please input a number between 1 and 65534 (inclusive).")
        except:
            print("You didn't enter a number; please input a number between 1 and 65534 (inclusive).")

    # Get a valid IP address
    while True:
        try:
            publicIP = input("Enter your public IP address: ")
            #test for a valid IP:
            ipaddress.ip_address(publicIP)
        except:
            print("That isn't a valid IPv4 address.  Please try again.")
            continue
        break

    pause = input("pause")

    # Create the Customer GW
    response = client.create_customer_gateway(
        BgpAsn =asNumber,
        PublicIp = publicIP,
        Type = 'ipsec.1',
        DryRun = True
    )
    # Tag the Customer GW
    responseDict = json.loads(json.dumps(response))
    customerGWID = responseDict['CustomerGateway']['CustomerGatewayId']
    client.create_tags(Resources=[customerGWID], Tags=[{'Key': 'Name', 'Value': cgwName}])

    return customerGWID


def MakeVPNGateway(client):
    # Gather Customer GW Info:
    vpgName = input("Enter a name for the Vitual Private Gateway: ")

    # Create VPN Gateway
    response = client.create_vpn_gateway(
        Type='ipsec.1',
        DryRun=False
    )

    # Tag the VPN GW
    responseDict = json.loads(json.dumps(response))
    vpnGWID = responseDict['VpnGateway']['VpnGatewayId']
    client.create_tags(Resources=[vpnGWID], Tags=[{'Key': 'Name', 'Value': vpgName}])

    # And figure out which VPC to attach it to
    ec2 = boto3.resource('ec2')
    vpcs = list(ec2.vpcs.all())
    counter = 0
    vpcsDict = {}
    for vpc in vpcs:
        response = client.describe_vpcs(
            VpcIds=[
                vpc.id,
            ]
        )
        responseDict = json.loads(json.dumps(response, sort_keys=True, indent=4))
        vpcCIDR = responseDict['Vpcs'][0]['CidrBlock']
        vpcID = responseDict['Vpcs'][0]['VpcId']
        vpcName = responseDict['Vpcs'][0]['Tags'][0]['Value']
        vpcsDict[counter] = {
            "VPCName": responseDict['Vpcs'][0]['Tags'][0]['Value'],
            "VPCID": responseDict['Vpcs'][0]['VpcId'],
            "VPCCIDR": responseDict['Vpcs'][0]['CidrBlock']
        }
        counter += 1

    table1 = PrettyTable()

    # Header
    table1.field_names = ['Index', 'VPC Name', 'VPC ID', 'VPC CIDR']

    for index in vpcsDict:
        table1.add_row([index, vpcsDict[index]['VPCName'], vpcsDict[index]['VPCID'], vpcsDict[index]['VPCCIDR']])
    print(table1)

    vpcSelection = int(input("Select an index number for the VPC to attach to the VPN Gateway: "))

    # And then attach the VPG to the VPC
    client.attach_vpn_gateway(
        VpcId=vpcsDict[vpcSelection]['VPCID'],
        VpnGatewayId=vpnGWID,
        DryRun=False
    )

    print("Pausing for 20 seconds while the Virtual Private Gateway is attached to the VPC...")
    time.sleep(20)

    return vpnGWID, vpcID


def MakeVPN(client, customerGWID, vpnGWID):
    # Gather Site-to-Site VPN Info
    vpnName = input("Enter a name for the VPN connection (no spaces): ")

    # Create Site-to-Site VPN Info
    response = client.create_vpn_connection(
        CustomerGatewayId=customerGWID,
        Type='ipsec.1',
        VpnGatewayId=vpnGWID,
        DryRun=False,
        Options={
            'StaticRoutesOnly': False
        },
    )

    # Tag the VPN
    responseDict = json.loads(json.dumps(response))
    vpnID = responseDict['VpnConnection']['VpnConnectionId']
    client.create_tags(Resources=[vpnID], Tags=[{'Key': 'Name', 'Value': vpnName}])

    return vpnID


def EnableRouteTableProp(vpnGWID, vpcID):
    # First, get the associated route table ID
    response = client.describe_route_tables(
        Filters=[
            {
                'Name': 'vpc-id',
                'Values': [
                    vpcID,
                ]
            },
        ]
    )
    responseDict = json.loads(json.dumps(response))
    routeTableID = responseDict['RouteTables'][0]['Associations'][0]['RouteTableId']

    # Enable route propagation
    response = client.enable_vgw_route_propagation(
        GatewayId=vpnGWID,
        RouteTableId=routeTableID
    )


def MakeConfigFiles(vpnID):
    # Note: This entire method is HEAVILY derived, with most parts directly copied, from Anderson Santos'
    # aws_vpn_config (https://github.com/asantos2000/aws_vpn_config)
    import xmltodict as xd
    import lxml.etree as ET

    if not os.path.isfile('customer-gateway-config-formats.xml'):
        xml_file = urllib.request.URLopener()
        xml_file.retrieve("http://ec2-downloads.s3.amazonaws.com/2009-07-15/customer-gateway-config-formats.xml",
                          "customer-gateway-config-formats.xml")

    with open('customer-gateway-config-formats.xml', 'r') as f:
        cf = xd.parse(f.read())

    table2 = PrettyTable()

    # Header
    table2.field_names = ['index', 'Vendor', 'Platform', 'Software', 'Filename']

    for index, item in enumerate(cf['CustomerGatewayConfigFormats']['Format']):
        table2.add_row([index, item['Vendor'], item['Platform'], item['Software'], item['Filename']])
    print(table2)

    converter_id = int(input("Enter an index number for the config you wish to download: "))

    client = boto3.client('ec2')  # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html

    # VPN Config as XML
    response = client.describe_vpn_connections(
        VpnConnectionIds=[
            vpnID,
        ],
        DryRun=False
    )

    with open(f'{vpnID}.xml', 'w') as fs:
        fs.write(response['VpnConnections'][0]['CustomerGatewayConfiguration'])

    # Import XSLT from http://ec2-downloads.s3.amazonaws.com/2009-07-15/customer-gateway-config-formats.xml
    filename_parser = cf['CustomerGatewayConfigFormats']['Format'][converter_id]['Filename']
    if not os.path.isfile(filename_parser):
        xlst_file = urllib.request.URLopener()
        xlst_file.retrieve(f"http://ec2-downloads.s3.amazonaws.com/2009-07-15/{filename_parser}", filename_parser)

    # Parse Config as FortiOS config file
    dom = ET.parse(f'{vpnID}.xml')
    xslt = ET.parse(filename_parser)
    transform = ET.XSLT(xslt)
    config = transform(dom)

    with open(f'{vpnID}.txt', 'w') as fs:
        fs.write(str(config))

    print(f'Files created and placed in the current directory: {filename_parser}, {vpnID}.xml and {vpnID}.txt')


client = boto3.client('ec2')
print("\n---===AWS Site-to-Site VPN Configurator===---\n")
print("\nStep 1.  Create the Customer Gateway.\n")
customerGWID = MakeCustomerGW(client)
print("\nStep 2.  Create the VPN Gateway and Attach it to a VPC.\n")
vpnGWID, vpcID = MakeVPNGateway(client)
print("\nStep 3.  Create the VPN.\n")
vpnID = MakeVPN(client, customerGWID, vpnGWID)
print("\nStep 4.  Enable Route Table Propagation...Complete.\n")
EnableRouteTableProp(vpnGWID, vpcID)
print("\nStep 5. Create On-Prem Device Configuration Files.\n")
MakeConfigFiles(vpnID)
print("\nAll done.  Enjoy your new VPN!\n")
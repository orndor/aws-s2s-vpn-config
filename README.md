# AWS Site-to-Site VPN Configurator

This script will perform the following:

1. Create all the components required in AWS for a Site-to-Site VPN with default settings (default meaning AWS generated pre-shared keys, inside IPs, DH algorithms, AWS-side private BGP AS, etc.), in your default region (as per your AWS CLI config).  These components are:
  
  * Customer Gateway
  * Virtual Private Gateway
  * Virtual Private Network
  * Enable Route Table Propagation

2. Generate on-prem side configuration templates for various types of equipment.

## To Install

```bash
$ git clone https://github.com/orndor/aws-s2s-vpn-config.git

$ cd aws-s2s-vpn-config

$ python setup.py build

$ python setup.py install
```

## To Use

```bash
python3 aws-s2s-vpn-config.py
```

Follow the prompts, as show below in the example output.

## Example Application Walk-Through & Output

```bash
---===AWS Site-to-Site VPN Configurator===---


Step 1.  Create the Customer Gateway.

Enter a name for the Customer Gateway: TestCGW
Enter your BGP ASN (If you do not have your own ASN, use a private one [64512-65534]): 65000
Enter your public IP address: 4.3.2.1

Step 2.  Create the VPN Gateway and Attach it to a VPC.

Enter a name for the Vitual Private Gateway: TestVPG
+-------+----------+--------------+---------------+
| Index | VPC Name |    VPC ID    |    VPC CIDR   |
+-------+----------+--------------+---------------+
|   0   | default  | vpc-f269cf99 | 172.31.0.0/16 |
+-------+----------+--------------+---------------+
Select an index number for the VPC to attach to the VPN Gateway: 0
Pausing for 20 seconds while the Virtual Private Gateway is attached to the VPC...

Step 3.  Create the VPN.

Enter a name for the VPN connection (no spaces): TestVPN

Step 4.  Enable Route Table Propagation...Complete.


Step 5. Create On-Prem Device Configuration Files.

+-------+------------------------+----------------------------+------------------------+--------------------------------------------+
| index |         Vendor         |          Platform          |        Software        |                  Filename                  |
+-------+------------------------+----------------------------+------------------------+--------------------------------------------+
|   0   |  Cisco Systems, Inc.   |     ISR Series Routers     |       IOS 12.4+        |    customer-gateway-cisco-ios-isr.xslt     |
|   1   | Juniper Networks, Inc. |      J-Series Routers      |       JunOS 9.5+       |   customer-gateway-juniper-junos-j.xslt    |
|   2   |        Generic         |            None            |    Vendor Agnostic     |       customer-gateway-generic.xslt        |
|   3   | Juniper Networks, Inc. | SSG and ISG Series Routers |     ScreenOS 6.2+      | customer-gateway-juniper-screenos-6.2.xslt |
|   4   | Juniper Networks, Inc. | SSG and ISG Series Routers |      ScreenOS 6.1      | customer-gateway-juniper-screenos-6.1.xslt |
|   5   |         Yamaha         |        RTX Routers         |     Rev.10.01.16+      |      customer-gateway-yamaha-rtx.xslt      |
|   6   |         Sophos         |            UTM             |           V9           |        customer-gateway-astaro.xslt        |
|   7   |         Sophos         |            ASG             |        V8.300+         |        customer-gateway-astaro.xslt        |
|   8   |  Cisco Systems, Inc.   |      ASA 5500 Series       |        ASA 8.2+        |      customer-gateway-cisco-asa.xslt       |
|   9   |        Fortinet        |    Fortigate 40+ Series    |   FortiOS 4.0+ (GUI)   |    customer-gateway-fortigate-gui.xslt     |
|   10  |        Fortinet        |    Fortigate 40+ Series    |      FortiOS 4.0+      |      customer-gateway-fortigate.xslt       |
|   11  |   Palo Alto Networks   |         PA Series          |   PANOS 4.1.2+ (GUI)   |     customer-gateway-paloalto-gui.xslt     |
|   12  |   Palo Alto Networks   |         PA Series          |      PANOS 4.1.2+      |       customer-gateway-paloalto.xslt       |
|   13  |         Vyatta         |     Vyatta Network OS      | Vyatta Network OS 6.5+ |        customer-gateway-vyatta.xslt        |
|   14  |       Microsoft        |       Windows Server       |        2008 R2         | customer-gateway-windows-server-2008.xslt  |
|   15  |          IIJ           |    SEIL/X1 and SEIL/X2     |      SEIL/X 3.70+      |       customer-gateway-iij-seil.xslt       |
|   16  |          IIJ           |          SEIL/B1           |     SEIL/B1 3.70+      |       customer-gateway-iij-seil.xslt       |
|   17  |          IIJ           |          SEIL/x86          |     SEIL/x86 2.30+     |       customer-gateway-iij-seil.xslt       |
+-------+------------------------+----------------------------+------------------------+--------------------------------------------+
Enter an index number for the config you wish to download: 0
Files created and placed in the current directory: customer-gateway-cisco-ios-isr.xslt, vpn-00ae4f687bb231d7c.xml and vpn-00ae4f687bb231d7c.txt

All done.  Enjoy your new VPN!
```

from setuptools import setup

setup(
    name='aws_s2s_vpn_config',
    version='0.1.0',
    packages=['aws_s2s_vpn_config'],
    url='https://github.com/orndor/aws-s2s-vpn-config',
    install_requires=[
        'boto3',
        'datetime',
        'lxml',
        'xmltodict',
        'prettytable'
    ],
    license='Apache',
    author='Rob Orndoff',
    author_email='rorndoff@gmail.com',
    description='Build site-to-site VPNs in AWS (with default settings) and download vendor config files'
)

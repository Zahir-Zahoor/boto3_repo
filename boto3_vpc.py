import boto3

# Initialize EC2 client
ec2 = boto3.client('ec2', region_name="ap-south-1")

# =========================
# 1. Create VPC
# =========================
vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16')
vpc_id = vpc['Vpc']['VpcId']

# Enable DNS
ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={'Value': True})
ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={'Value': True})

ec2.create_tags(Resources=[vpc_id], Tags=[{'Key': 'Name', 'Value': 'MyVPC'}])
print(f"✅ VPC created: {vpc_id}")

# =========================
# 2. Create Subnets
# =========================
subnet_pub1 = ec2.create_subnet(VpcId=vpc_id, CidrBlock='10.0.1.0/24', AvailabilityZone='ap-south-1a')
subnet_pub2 = ec2.create_subnet(VpcId=vpc_id, CidrBlock='10.0.2.0/24', AvailabilityZone='ap-south-1b')
subnet_priv1 = ec2.create_subnet(VpcId=vpc_id, CidrBlock='10.0.3.0/24', AvailabilityZone='ap-south-1a')
subnet_priv2 = ec2.create_subnet(VpcId=vpc_id, CidrBlock='10.0.4.0/24', AvailabilityZone='ap-south-1b')
subnet_db1 = ec2.create_subnet(VpcId=vpc_id, CidrBlock='10.0.5.0/24', AvailabilityZone='ap-south-1a')
subnet_db2 = ec2.create_subnet(VpcId=vpc_id, CidrBlock='10.0.6.0/24', AvailabilityZone='ap-south-1b')

# Tag subnets
ec2.create_tags(Resources=[subnet_pub1['Subnet']['SubnetId']], Tags=[{'Key': 'Name', 'Value': 'Public-Subnet-1'}])
ec2.create_tags(Resources=[subnet_pub2['Subnet']['SubnetId']], Tags=[{'Key': 'Name', 'Value': 'Public-Subnet-2'}])
ec2.create_tags(Resources=[subnet_priv1['Subnet']['SubnetId']], Tags=[{'Key': 'Name', 'Value': 'Private-Subnet-1'}])
ec2.create_tags(Resources=[subnet_priv2['Subnet']['SubnetId']], Tags=[{'Key': 'Name', 'Value': 'Private-Subnet-2'}])
ec2.create_tags(Resources=[subnet_db1['Subnet']['SubnetId']], Tags=[{'Key': 'Name', 'Value': 'DB-Subnet-1'}])
ec2.create_tags(Resources=[subnet_db2['Subnet']['SubnetId']], Tags=[{'Key': 'Name', 'Value': 'DB-Subnet-2'}])

print("✅ Subnets created & tagged")

# =========================
# 3. Internet Gateway
# =========================
igw = ec2.create_internet_gateway()
igw_id = igw['InternetGateway']['InternetGatewayId']
ec2.attach_internet_gateway(VpcId=vpc_id, InternetGatewayId=igw_id)
ec2.create_tags(Resources=[igw_id], Tags=[{'Key': 'Name', 'Value': 'My-IGW'}])
print(f"✅ Internet Gateway: {igw_id}")

# =========================
# 4. Elastic IP (for NAT)
# =========================
eip = ec2.allocate_address(Domain='vpc')
eip_id = eip['AllocationId']
ec2.create_tags(Resources=[eip_id], Tags=[{'Key': 'Name', 'Value': 'My-EIP'}])
print(f"✅ Elastic IP: {eip_id}")

# =========================
# 5. NAT Gateway
# =========================
nat_gw = ec2.create_nat_gateway(
    SubnetId=subnet_pub1['Subnet']['SubnetId'],
    AllocationId=eip_id
)
nat_id = nat_gw['NatGateway']['NatGatewayId']
ec2.create_tags(Resources=[nat_id], Tags=[{'Key': 'Name', 'Value': 'My-NAT-GW'}])
print(f"✅ NAT Gateway: {nat_id}")

# Wait until NAT is available
waiter = ec2.get_waiter('nat_gateway_available')
waiter.wait(NatGatewayIds=[nat_id])

# =========================
# 6. Route Tables
# =========================
rtb_public = ec2.create_route_table(VpcId=vpc_id)['RouteTable']['RouteTableId']
rtb_private = ec2.create_route_table(VpcId=vpc_id)['RouteTable']['RouteTableId']
rtb_db = ec2.create_route_table(VpcId=vpc_id)['RouteTable']['RouteTableId']

# Tag route tables
ec2.create_tags(Resources=[rtb_public], Tags=[{'Key': 'Name', 'Value': 'Public-RTB'}])
ec2.create_tags(Resources=[rtb_private], Tags=[{'Key': 'Name', 'Value': 'Private-RTB'}])
ec2.create_tags(Resources=[rtb_db], Tags=[{'Key': 'Name', 'Value': 'DB-RTB'}])

# Routes
ec2.create_route(RouteTableId=rtb_public, DestinationCidrBlock='0.0.0.0/0', GatewayId=igw_id)
ec2.create_route(RouteTableId=rtb_private, DestinationCidrBlock='0.0.0.0/0', NatGatewayId=nat_id)

# Associate subnets
ec2.associate_route_table(RouteTableId=rtb_public, SubnetId=subnet_pub1['Subnet']['SubnetId'])
ec2.associate_route_table(RouteTableId=rtb_public, SubnetId=subnet_pub2['Subnet']['SubnetId'])
ec2.associate_route_table(RouteTableId=rtb_private, SubnetId=subnet_priv1['Subnet']['SubnetId'])
ec2.associate_route_table(RouteTableId=rtb_private, SubnetId=subnet_priv2['Subnet']['SubnetId'])
ec2.associate_route_table(RouteTableId=rtb_db, SubnetId=subnet_db1['Subnet']['SubnetId'])
ec2.associate_route_table(RouteTableId=rtb_db, SubnetId=subnet_db2['Subnet']['SubnetId'])

print("✅ Route tables created, tagged & associated")

# =========================
# 7. Security Group
# =========================
sg = ec2.create_security_group(
    GroupName="my-sg",
    Description="My Security Group",
    VpcId=vpc_id
)
sg_id = sg['GroupId']
ec2.create_tags(Resources=[sg_id], Tags=[{'Key': 'Name', 'Value': 'My-SG'}])

# Allow SSH inbound
ec2.authorize_security_group_ingress(
    GroupId=sg_id,
    IpPermissions=[{
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22,
        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
    }]
)
print(f"✅ Security Group created: {sg_id}")

# =========================
# 8. Network ACL
# =========================
nacl = ec2.create_network_acl(VpcId=vpc_id)['NetworkAcl']['NetworkAclId']
ec2.create_tags(Resources=[nacl], Tags=[{'Key': 'Name', 'Value': 'My-NACL'}])

# Add inbound/outbound rules (allow all)
ec2.create_network_acl_entry(
    NetworkAclId=nacl, RuleNumber=100, Protocol='-1',
    RuleAction='allow', Egress=False, CidrBlock='0.0.0.0/0'
)
ec2.create_network_acl_entry(
    NetworkAclId=nacl, RuleNumber=100, Protocol='-1',
    RuleAction='allow', Egress=True, CidrBlock='0.0.0.0/0'
)
print(f"✅ NACL created: {nacl}")

# =========================
# 9. DHCP Options Set
# =========================
dhcp = ec2.create_dhcp_options(
    DhcpConfigurations=[{'Key': 'domain-name-servers', 'Values': ['AmazonProvidedDNS']}]
)
dhcp_id = dhcp['DhcpOptions']['DhcpOptionsId']
ec2.associate_dhcp_options(DhcpOptionsId=dhcp_id, VpcId=vpc_id)
ec2.create_tags(Resources=[dhcp_id], Tags=[{'Key': 'Name', 'Value': 'My-DHCP'}])
print(f"✅ DHCP Options Set created: {dhcp_id}")

# =========================
# 10. VPC Endpoint (S3)
# =========================
endpoint = ec2.create_vpc_endpoint(
    VpcId=vpc_id,
    ServiceName=f'com.amazonaws.ap-south-1.s3',
    RouteTableIds=[rtb_private, rtb_db],
    VpcEndpointType='Gateway'
)
endpoint_id = endpoint['VpcEndpoint']['VpcEndpointId']
ec2.create_tags(Resources=[endpoint_id], Tags=[{'Key': 'Name', 'Value': 'My-S3-Endpoint'}])
print(f"✅ VPC Endpoint created: {endpoint_id}")

print("\n🎉 All resources created & tagged successfully!")

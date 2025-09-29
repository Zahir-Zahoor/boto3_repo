import boto3

ec2 = boto3.client('ec2', region_name="ap-south-1")
# =========================
# 2. Define User Data (runs at boot)
# =========================
user_data_script = """#!/bin/bash
yum update -y
yum install -y httpd
systemctl enable httpd
systemctl start httpd
echo "<h1>Hello from EC2 in VPC</h1>" > /var/www/html/index.html
"""

# =========================
# 3. Launch EC2 Instance
# =========================
# Replace with IDs from previous script
subnet_id = "subnet-xxxxxx"  # Use one of the public subnets
sg_id = "sg-xxxxxx"          # Security group created earlier

ec2_instance = ec2.run_instances(
    ImageId="ami-0f5ee92e2d63afc18",   # Amazon Linux 2 AMI (region-specific, update if needed)
    InstanceType="t3.micro",
    KeyName="my-keypair",              # Replace with your key pair name
    MinCount=1,
    MaxCount=1,
    NetworkInterfaces=[{
        'DeviceIndex': 0,
        'SubnetId': subnet_id,
        'AssociatePublicIpAddress': True,
        'Groups': [sg_id]
    }],
    UserData=user_data_script,
    TagSpecifications=[{
        'ResourceType': 'instance',
        'Tags': [
            {'Key': 'Name', 'Value': 'MyWebServer'},
            {'Key': 'Project', 'Value': 'DemoVPC'},
            {'Key': 'Owner', 'Value': 'Aafaq'}
        ]
    }]
)

instance_id = ec2_instance['Instances'][0]['InstanceId']
print(f"✅ EC2 Instance launched: {instance_id}")

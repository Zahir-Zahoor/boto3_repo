import boto3

ec2 = boto3.client('ec2', region_name="ap-south-1")
iam = boto3.client('iam')

# =========================
# 1. Create IAM Role for EC2
# =========================
role_name = "EC2S3AccessRole"
instance_profile_name = "EC2S3AccessProfile"

# Trust policy (EC2 can assume this role)
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "ec2.amazonaws.com"},
        "Action": "sts:AssumeRole"
    }]
}

# Create role
try:
    role = iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=str(trust_policy)
    )
    print(f"✅ IAM Role created: {role_name}")
except iam.exceptions.EntityAlreadyExistsException:
    print(f"ℹ️ Role {role_name} already exists")

# Attach policy (e.g. S3 full access for demo)
iam.attach_role_policy(
    RoleName=role_name,
    PolicyArn="arn:aws:iam::aws:policy/AmazonS3FullAccess"
)

# Create instance profile and add role
try:
    iam.create_instance_profile(InstanceProfileName=instance_profile_name)
    iam.add_role_to_instance_profile(
        InstanceProfileName=instance_profile_name,
        RoleName=role_name
    )
    print(f"✅ Instance Profile created: {instance_profile_name}")
except iam.exceptions.EntityAlreadyExistsException:
    print(f"ℹ️ Instance Profile {instance_profile_name} already exists")

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
instance_profile_arn = f"arn:aws:iam::YOUR_ACCOUNT_ID:instance-profile/{instance_profile_name}"

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
    IamInstanceProfile={'Arn': instance_profile_arn},
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

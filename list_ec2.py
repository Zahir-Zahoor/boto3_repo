import boto3

aws_management_console = boto3.session.Session(region_name = "us-east-1")

ec2_console = aws_management_console.client(service_name = "ec2")

result =ec2_console.describe_instances()

for each_instance in result['Reservations']:
    for value in each_instance['Instances']:
        print(value['InstanceId'])


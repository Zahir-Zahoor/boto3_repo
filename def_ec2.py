import boto3

aws_console = boto3.session.Session(region_name="us-east-1")
ec2_console = aws_console.client("ec2")

def instance_details():
    result = ec2_console.describe_instances()

    instances = [
        (
            value['InstanceId'], 
            value['InstanceType'],
            value['PrivateIpAddress']
        )
        for each_instance in result['Reservations']
        for value in each_instance['Instances']
    ]

    print(instances)

instance_details()

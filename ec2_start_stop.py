import boto3

def lambda_handler(event, context):
    action = event.get('action')
    tag_key = '......'
    tag_value = '.....'
    region = 'us-east-1'

    ec2 = boto3.client('ec2', region_name=region)

    filters = [
        {'Name': f'tag:{tag_key}', 'Values': [tag_value]},
    ]

    response = ec2.describe_instances(Filters=filters)

    instances = [
        i['InstanceId']
        for r in response['Reservations']
        for i in r['Instances']
    ]

    if not instances:
        return {'status': 'no matching instances found'}

    if action == 'start':
        ec2.start_instances(InstanceIds=instances)
        return {'status': 'started', 'instances': instances}
    
    elif action == 'stop':
        ec2.stop_instances(InstanceIds=instances)
        return {'status': 'stopped', 'instances': instances}
    
    else:
        return {'status': 'error', 'message': f'Invalid action: {action}'}

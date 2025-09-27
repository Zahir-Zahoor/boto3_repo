import boto3

aws_management_console = boto3.session.Session()

iam = aws_management_console.resource("iam")

for each_user in iam.users.all():
    print(each_user.name)

import boto3

# Configuration
repository_name = "my-simple-repo"
region = "ap-south-1"

# Create ECR client
ecr = boto3.client('ecr', region_name=region)

# Create the repository
response = ecr.create_repository(repositoryName=repository_name)

# Print the repository URI
print("Repository created!")
print("URI:", response['repository']['repositoryUri'])

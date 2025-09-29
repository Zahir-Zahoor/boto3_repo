import boto3

# Create S3 client
s3 = boto3.client('s3')

# Bucket name (must be unique globally)
bucket_name = "my-versioned-bucket-123456"
region = "us-east-1"

# 1. Create the bucket
s3.create_bucket(Bucket=bucket_name)

print(f"✅ Bucket '{bucket_name}' created")

# 2. Enable versioning
s3.put_bucket_versioning(
    Bucket=bucket_name,
    VersioningConfiguration={
        'Status': 'Enabled'
    }
)
print("✅ Versioning enabled")

# 3. Add tags
s3.put_bucket_tagging(
    Bucket=bucket_name,
    Tagging={
        'TagSet': [
            {'Key': 'Project', 'Value': 'Demo'},
            {'Key': 'Owner', 'Value': 'Zahir'}
        ]
    }
)
print("✅ Tags added")

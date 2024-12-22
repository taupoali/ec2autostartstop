import boto3
from datetime import datetime, timedelta, timezone

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    # Fetch all instances with the 'autostart' tag set to 'true'
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:autostart', 'Values': ['true']},
            {'Name': 'instance-state-name', 'Values': ['stopped']}
        ]
    )
    
    instances_to_start = []
    now = datetime.now(timezone.utc)  # Use timezone-aware UTC time
    time_window = timedelta(minutes=15)  # Define the time window
    
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            # Get tags
            tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
            start_time = tags.get('start-time')
            
            if start_time:
                # Convert start_time to datetime
                start_datetime = datetime.strptime(start_time, '%H:%M').replace(
                    year=now.year, month=now.month, day=now.day, tzinfo=timezone.utc
                )
                
                # Check if current time is within the window
                if start_datetime <= now <= start_datetime + time_window:
                    instances_to_start.append(instance['InstanceId'])
    
    # Start instances if applicable
    if instances_to_start:
        print(f"Starting instances: {instances_to_start}")
        ec2.start_instances(InstanceIds=instances_to_start)
    else:
        print("No instances to start within the time window.")

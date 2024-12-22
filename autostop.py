import boto3
from datetime import datetime, timedelta, timezone

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    # Fetch all instances with the 'autoshutdown' tag set to 'true'
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:autoshutdown', 'Values': ['true']},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    
    instances_to_stop = []
    now = datetime.now(timezone.utc)  # Use timezone-aware UTC time
    time_window = timedelta(minutes=15)  # Define the time window
    
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            # Get tags
            tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
            shutdown_time = tags.get('shutdown-time')
            
            if shutdown_time:
                # Convert shutdown_time to datetime
                shutdown_datetime = datetime.strptime(shutdown_time, '%H:%M').replace(
                    year=now.year, month=now.month, day=now.day, tzinfo=timezone.utc
                )
                
                # Check if current time is within the window
                if shutdown_datetime <= now <= shutdown_datetime + time_window:
                    instances_to_stop.append(instance['InstanceId'])
    
    # Stop instances if applicable
    if instances_to_stop:
        print(f"Stopping instances: {instances_to_stop}")
        ec2.stop_instances(InstanceIds=instances_to_stop)
    else:
        print("No instances to stop within the time window.")

# adapted from http://db.geeksinsight.com/2017/08/10/aws-rds-stop-start-script/

import boto3
import botocore.session
import sys
import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='botocore.client')

load_dotenv()

AWS_PROFILE = os.getenv('AWS_PROFILE', None)

if AWS_PROFILE is None:
    print("ERROR: .env file missing required AWS_PROFILE")
    sys.exit(1)

# Create an empty botocore session directly
session = botocore.session.Session()

# Get config of desired profile. full_config is a standard python dictionary.
profiles_config = session.full_config.get("profiles", {})
AWS_REGION = profiles_config[AWS_PROFILE]['region']
if not AWS_REGION:
      print("ERROR: AWS_REGION not found in AWS_PROFILE")
      sys.exit(1)

rds_client = boto3.client('rds', region_name=AWS_REGION)

db_instance_info = rds_client.describe_db_instances()
num_db_instances = len(db_instance_info['DBInstances'])
print(f"processing {num_db_instances} db_instances")

for each_db in db_instance_info['DBInstances']:
    response = rds_client.list_tags_for_resource(ResourceName=each_db['DBInstanceArn'])

    taglist = response['TagList']
    if sys.argv[1] == each_db['DBInstanceIdentifier'] and sys.argv[2] == 'stop':
     for tag in taglist:
        if tag['Key'] == 'AutoOff' and tag['Value'] == 'True' and each_db['DBInstanceStatus'] == 'available':
              db=each_db['DBInstanceIdentifier']
              status=each_db['DBInstanceStatus']
              print(db +':'+ status)
              response = rds_client.stop_db_instance(DBInstanceIdentifier=db)

    elif sys.argv[1] == each_db['DBInstanceIdentifier'] and sys.argv[2] == 'start':
     for tag in taglist:
        if tag['Key'] == 'AutoOff' and tag['Value'] == 'True' and each_db['DBInstanceStatus'] == 'available':
              db=each_db['DBInstanceIdentifier']
              status=each_db['DBInstanceStatus']
              print( db +':'+ status )
              response = rds_client.start_db_instance(DBInstanceIdentifier=db)

    elif sys.argv[1] == each_db['DBInstanceIdentifier'] and sys.argv[2] == 'status':
     for tag in taglist:
        if tag['Key'] == 'AutoOff' and tag['Value'] == 'True':
              db=each_db['DBInstanceIdentifier']
              status=each_db['DBInstanceStatus']
              print( db +':'+ status )

    elif sys.argv[1] == 'stop' and sys.argv[:2]:
     for tag in taglist:
        if tag['Key'] == 'AutoOff' and tag['Value'] == 'True' and each_db['DBInstanceStatus'] == 'available':
              db=each_db['DBInstanceIdentifier']
              status=each_db['DBInstanceStatus']
              print( db +':'+ status )
              response = rds_client.stop_db_instance(DBInstanceIdentifier=db)

    elif sys.argv[1] == 'start' and sys.argv[:2]:
     for tag in taglist:
        if tag['Key'] == 'AutoOff' and tag['Value'] == 'True' and each_db['DBInstanceStatus'] == 'stopped':
              db=each_db['DBInstanceIdentifier']
              status=each_db['DBInstanceStatus']
              print( db +':'+ status )
              response = rds_client.start_db_instance(DBInstanceIdentifier=db)

    elif sys.argv[1] == 'status' and sys.argv[:2]:
     for tag in taglist:
        if tag['Key'] == 'AutoOff' and tag['Value'] == 'True':
              db=each_db['DBInstanceIdentifier']
              status=each_db['DBInstanceStatus']
              print( db +':'+ status )

# Sample Run To check the status, start and stop

# root@wash-i-xx-restore ~ $ python rdsmanage.py status
#  c92base:stopped
#  cs89upg:stopped
#  cs92dev:stopped
#  csdmo:stopped
#  dp4adwe8ind3oy:stopped
#  rp19a3160yh53k3:stopped
#  sitecore:stopped

# root@wash-i-xx-restore ~ $ python rdsmanage.py start
#  c92base:starting
#  cs89upg:starting
#  cs92dev:starting
#  csdmo:starting
#  dp4adwe8ind3oy:starting
#  rp19a3160yh53k3:starting
#  sitecore:starting

# root@wash-i-xx-restore ~ $ python rdsmanage.py stop
#  c92base:stopping
#  cs89upg:stopping
#  cs92dev:stopping
#  csdmo:stopping
#  dp4adwe8ind3oy:stopping
#  rp19a3160yh53k3:stopping
#  sitecore:stopping
# You can also stop the instance specifically by providing the instance name and then action.

# root@ /scripts/db_reconfiguration $ python /scripts/rdsmanage.py xxx stop
# ipfx2:available
# root@  /scripts/db_reconfiguration $ python /scripts/rdsmanage.py xxx status
# ipfx2:stopping

# You can schedule this script using cron or lambda, for example we want stop databases at night 7PM and start them at 7AM. The cron looks like follows

# 00 19 * * * python /scripts/rdsmanage.py stop
# 00 07 * * * python /scripts/rdsmanage.py start
# 00 19 * * * python /scripts/rdsmanage.py ipfx stop
# 00 07 * * * python /scripts/rdsmanage.py ipfx start

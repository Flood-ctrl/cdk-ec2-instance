import boto3
import os
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logger.setLevel(os.environ.get('LOGLEVEL')),
                    format='[%(levelname)s] : %(name)s : %(asctime)s : %(message)s',)

def handler(event, context):
    logger.debug(event)
    logger.info('Start executing handler')
    ssm_client = boto3.client('ssm')
    logger.info('ssm_client.send_command')
    ssm_command_response = ssm_client.send_command(
                Targets=[
                    {
                        'Key': 'tag:'+ os.environ['EC2_TAG_KEY'],
                        'Values': [os.environ['EC2_TAG_VALUE']]
                        }
                    ],
                #OutputS3BucketName=[os.environ['S3Output']],
                DocumentName='AWS-RunAnsiblePlaybook',
                Parameters={
                    'playbookurl': [os.environ['PLAYBOOK_URL']],
                    }, 
        )
    logger.debug(ssm_command_response)
    logger.info('context.aws_request_id')
    command_id = context.aws_request_id
    print(ssm_command_response)
    print(event) #CHANGEME

    ec2 = boto3.client('ec2')
    if 'detail-type' in event.keys():
        if event['detail-type'] == 'EC2 Instance State-change Notification' and event['detail']['state'] == 'running':
            print('YES')
            ec2_instance_id = event['detail']['instance-id']
            ec2_event_response = ec2.describe_instances(
                Filters=[
                {
                    'Name': 'tag:'+ os.environ['EC2_TAG_KEY'],
                    'Values':
                        [os.environ['EC2_TAG_VALUE']],
                },
            ],
                InstanceIds=[
                       ec2_instance_id,
                       ],)
            #if ec2_event_response['Reservations']
            print('PRINT RESERVATION')
            if not ec2_event_response['Reservations']:
                print('RESERVATION IS EMPTY')
            else:
                print(ec2_event_response['Reservations'])
                print('RESERVATIOn TYPE')
                print(type(ec2_event_response['Reservations']))

    else:
        print('THE OTHER TRIGGER')




    logger.info('Returning status code')
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Done {}\n'.format(event)
    }


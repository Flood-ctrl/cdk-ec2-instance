import boto3
import os
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logger.setLevel(os.environ.get('LOGLEVEL')),
                    format='[%(levelname)s] : %(name)s : %(asctime)s : %(message)s',)

def handler(event, context):
    logger.debug(event)
    logger.info('Start executing handler')
    cw_event_tag_validator(event, context)
    logger.info('Returning status code')
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Done {}\n'.format(event)
    }


def ssm_run_command_run_ansible_playbook(context):
    ssm_client = boto3.client('ssm')
    logger.info('AWS-RunAnsiblePlaybook')
    ssm_command_response = ssm_client.send_command(
        Targets=[
            {
                'Key': 'tag:'+ os.environ['EC2_TAG_KEY'],
                'Values': [os.environ['EC2_TAG_VALUE']]
                }
            ],
        DocumentName='AWS-RunAnsiblePlaybook',
        Parameters={
            'playbookurl': [os.environ['PLAYBOOK_URL']],
            }, 
        )
    logger.debug(ssm_command_response)
    command_id = context.aws_request_id
    logger.debug(command_id)

def ssm_run_command_run_ansible_playbook_instance(context, ec2_instance_id):
    ssm_client = boto3.client('ssm')
    logger.info('AWS-RunAnsiblePlaybook2')
    logger.debug(ec2_instance_id)
    ssm_command_response = ssm_client.send_command(
        InstanceIds=[
            ec2_instance_id,
        ],
        DocumentName='AWS-RunAnsiblePlaybook',
        Parameters={
            'playbookurl': [os.environ['PLAYBOOK_URL']],
            }, 
        )
    logger.debug(ssm_command_response)
    command_id = context.aws_request_id
    logger.debug(command_id)


def cw_event_tag_validator(event, context):
    logger.info('cw_event_tag_validator')
    if 'detail-type' in event.keys():
        if event['detail-type'] == 'EC2 Instance State-change Notification' \
                                 and event['detail']['state'] == 'running':
            logger.info('EC2 Instance State-change Notification')
            ec2_instance_id = event['detail']['instance-id']
            logger.debug(ec2_instance_id)
            ec2 = boto3.client('ec2')
            ec2_event_response = ec2.describe_instances(
                Filters=[
                    {
                        'Name': 'tag:'+ os.environ['EC2_TAG_KEY'],
                        'Values': [os.environ['EC2_TAG_VALUE']],
                    },
                ],
                InstanceIds=[
                    ec2_instance_id,
                ],
            )
            logger.debug(ec2_event_response)
            if ec2_event_response['Reservations'] != []:
                ssm_run_command_run_ansible_playbook_instance(context,ec2_instance_id)
    else:
        ssm_run_command_run_ansible_playbook(context)
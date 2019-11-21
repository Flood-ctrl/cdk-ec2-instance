import boto3
import os
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logger.setLevel(os.environ.get('LOGLEVEL')),
                    format='[%(levelname)s] : %(name)s : %(asctime)s : %(message)s',)


def handler(event, context):
    logger.debug(event)
    logger.info('Start executing handler')
    cw_event_tags_validator(event, context)
    logger.info('Returning status code')
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Done {}\n'.format(event)
    }


def get_ec2_target(event):
    '''Gets value for ec2_target variable for passing it to target_value var.
       The value is taking from event and parsing it to playbook file name
       witout extension (before dot and three charactes defining extension in MS Windows systems).
       Palybook S3 path is taking from event also.
    '''

    logger.info('get_ec2_target')
    global playbook_path
    playbook_path = event['Records'][0]['s3']['object']['key']
    logger.debug(playbook_path)
    ec2_target = playbook_path.split("/")
    logger.debug(ec2_target)
    try:
        ec2_target = ec2_target[1].split(".")
        logger.debug(ec2_target)
    except IndexError:
        logger.debug('IndexError exeption')
        ec2_target = ec2_target[0].split(".")
        logger.debug(ec2_target)
    ec2_target = ec2_target[0].lower()
    logger.debug(ec2_target)
    return ec2_target


def ssm_run_command_ansible_playbook(context, target_key, target_value):
    ssm_client = boto3.client('ssm')
    logger.info('SMM Document name: ' + os.environ['SSM_DOCUMENT_NAME'])
    logger.info('Ansible Playbook: ' +
                os.environ['PLAYBOOK_URL'] + playbook_path)
    logger.debug('target_key: ' + target_key)
    logger.debug('target_value: ' + target_value)
    ssm_command_response = ssm_client.send_command(
        Targets=[
            {
                'Key': target_key,
                'Values': [target_value]
            }
        ],
        DocumentName=os.environ['SSM_DOCUMENT_NAME'],
        Parameters={
            'playbookurl': [os.environ['PLAYBOOK_URL'] + playbook_path],
        },
    )
    logger.debug(ssm_command_response)
    command_id = context.aws_request_id
    logger.debug(command_id)


def cw_event_tags_validator(event, context):
    '''
    Cloud Watch tags validator checks for Cloud Watch event by triggered by created EC2 instance 
    for appropriate tags, if true it's running command on this EC2 instance.
    If it dosen't look like Cloud Watch event it assumes S3 bucket object was created 
    and running command on instances with appropriate tags.
    '''
    logger.info('cw_event_tags_validator')
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
                        'Name': 'tag:' + os.environ['EC2_TAG_KEY'],
                        'Values': [os.environ['EC2_TAG_VALUE']],
                    },
                ],
                InstanceIds=[
                    ec2_instance_id,
                ],
            )
            logger.debug(ec2_event_response)
            if ec2_event_response['Reservations'] != []:
                target_key = 'InstanceIds'
                target_value = ec2_instance_id
                ssm_run_command_ansible_playbook(
                    context, target_key, target_value)
    else:
        target_key = 'tag:' + os.environ['EC2_TAG_KEY']
        if os.environ['EC2_TAG_VALUE'] != 'None':
            target_value = os.environ['EC2_TAG_VALUE']
        else:
            target_value = get_ec2_target(event)
        ssm_run_command_ansible_playbook(context, target_key, target_value)

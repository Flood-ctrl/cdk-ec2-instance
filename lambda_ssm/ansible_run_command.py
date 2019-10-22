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
    response = ssm_client.send_command(
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
    logger.debug(response)
    logger.info('context.aws_request_id')
    command_id = context.aws_request_id
    print(response)
    logger.info('Returning status code')
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Done {}\n'.format(event)
    }
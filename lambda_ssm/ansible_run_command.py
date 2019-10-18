import boto3
import os
import logging

def handler(event, context):
    ssm_client = boto3.client('ssm')
    logs = logging
    logs.debug(event)
    response = ssm_client.send_command(
                Targets=[
                    {
                        'Key': 'tag:'+ os.environ['ec2_tag_key'],
                        'Values': [os.environ['ec2_tag_value']]
                        }
                    ],
                DocumentName='AWS-RunAnsiblePlaybook',
                Parameters={
                    'playbookurl': [os.environ['playbook_url']],
                    }, 
        )
    
    command_id = context.aws_request_id
    print(response)
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Done {}\n'.format(event)
    }
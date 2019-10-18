import boto3
import json

def handler(event, context, ec2_tag_key: str, ec2_tag_value: str,):
    ssm_client = boto3.client('ssm')
    response = ssm_client.send_command(
                Targets=[
                    {
                        'Key': f'tag:{ec2_tag_key}',
                        'Values': [f'{ec2_tag_value}']
                    }
                ],
                DocumentName='AWS-RunAnsiblePlaybook',
                Parameters={'commands': ['start ecs']}, )
    
    command_id = context.aws_request_id
    output = ssm_client.get_command_invocation(
          CommandId=command_id,
          InstanceId='i-03######',
        )
    print(output)
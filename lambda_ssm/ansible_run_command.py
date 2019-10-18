import boto3


def handler(event, context, ec2_tag_key: str, ec2_tag_value: str, 
            playbook_url: list,):
    ssm_client = boto3.client('ssm')
    response = ssm_client.send_command(
                Targets=[
                    {
                        'Key': f'tag:{ec2_tag_key}',
                        'Values': ec2_tag_value
                        }
                    ],
                DocumentName='AWS-RunAnsiblePlaybook',
                Parameters={
                    'playbookurl':[playbook_url],
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
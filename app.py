#!/usr/bin/env python3

import os
from aws_cdk import core

from ec2_instance.ec2_instance_stack import EC2Instance
from lambda_ssm.lambda_ssm_construct import LambdaSsmConstruct

app = core.App()
EC2Instance(app, "ec2-instance-1",
            #vpc_name='shared_vpc',
            env={
                'account': os.environ['CDK_ACCOUNT'],
                'region': 'us-east-1'
            }, 
            ec2_tag_key="CDK-Type",
            ec2_tag_value="EC2Instance",
            instances_count=2,
            #playbook_url="s3://s3-testbucketruanspl1/playbook.yml",
            playbook_file_name="playbook.yml",
            #ssm_policy=True,
            #log_level='DEBUG',
            )

app.synth()
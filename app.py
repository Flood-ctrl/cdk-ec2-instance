#!/usr/bin/env python3

from aws_cdk import core

from ec2_instance.ec2_instance_stack import EC2Instance
from lambda_ssm.lambda_ssm_construct import LambdaSsmConstruct

app = core.App()
EC2Instance(app, "ec2-instance-1", env={'region': 'us-east-1'}, 
            ec2_tag_key="CDK-Type",
            ec2_tag_value="EC2Instance",
            instances_count=1,
            playbook_url="s3://test-ansible-pl-hw/playbook.yml",
            ssm_policy=True,
            log_level='DEBUG',
            )

app.synth()
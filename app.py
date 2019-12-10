#!/usr/bin/env python3

import os
from aws_cdk import core

from ec2_instance.ec2_instance_stack import EC2Instance

app = core.App()
EC2Instance(app, "ec2-instance-1",
            description='Test EC2 stack',
            env={
                'account': os.environ['CDK_AWS_ACCOUNT'],
                'region': 'us-east-1'
            },
            )

app.synth()
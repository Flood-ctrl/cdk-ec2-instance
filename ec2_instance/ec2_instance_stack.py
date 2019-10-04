from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_logs as logs,
)

aws_region = "us-east-1"

class EC2Instance(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(
            self, "MyEC2Vpc",
            max_azs=2
        )

        ec2_instance = ec2.Instance(
            self, "EC2Ubuntu",
            vpc=vpc,
            instance_type=ec2.InstanceType(
                instance_type_identifier="t2.micro",
            ),

            machine_image=ec2.GenericLinuxImage(
                ami_map={aws_region: "ami-01d9d5f6cecc31f85"},
            ),

        )

        core.CfnOutput(
        self, "InstanceIP",
        value=ec2_instance.instance_public_ip
        )

        #aws ec2 describe-images --region us-east-1 --owners 099720109477 --filters 'Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-????????' 'Name=state,Values=available' | head -n50

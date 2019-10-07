from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_logs as logs,
)

from variables import *


class EC2Instance(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(
            self, "MyEC2Vpc",
            max_azs=2,
            nat_gateways=0,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            subnet_configuration=[ec2.SubnetConfiguration(
                name="EC2PublicSubnet",
                subnet_type= ec2.SubnetType.PUBLIC,
                cidr_mask= 28,
            ),
            ],
        )

        security_group = ec2.SecurityGroup(
            self, "SecurityGroup",
            vpc=vpc,
            allow_all_outbound=True,
        )

        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22),
            description="Allow all traffic"
        )

        ec2_instance = ec2.Instance(
            self, "EC2Ubuntu",
            vpc=vpc,
            security_group=security_group,
            key_name=ssh_key_name,
            instance_type=ec2.InstanceType(
                instance_type_identifier="t2.micro",
            ),
            machine_image=ec2.GenericLinuxImage(
                ami_map={aws_region: ami_id},
            ),
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC,
            ),
        )

        ec2_tags = core.Tag.add(
            self,
            key="CDK-Type",
            value="EC2Instance",
        )

        core.CfnOutput(
        self, "InstanceIP",
        value=ec2_instance.instance_public_ip
        )

        #aws ec2 describe-images --region us-east-1 --owners 099720109477 --filters 'Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-????????' 'Name=state,Values=available' | head -n50

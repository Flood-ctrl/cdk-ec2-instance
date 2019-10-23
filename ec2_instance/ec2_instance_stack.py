from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_ssm as ssm,
    aws_iam as iam,
    aws_logs as logs,
)

from variables import *

from s3_buckets_construct import S3BucketsConstruct
from ssm_association_construct import SSMAssociationConstruct
from lambda_ssm.lambda_ssm_construct import LambdaSsmConstruct


class EC2Instance(core.Stack):

    def __init__(self, scope: core.Construct, id: str, 
                 ec2_tag_key="cdk", ec2_tag_value=["instance"], playbook_url=None,
                 playbook_file_name=None,
                 instances_count=1, ssm_policy=None, log_level='INFO',
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        parameter_store = ssm.StringParameter(
            self, "SsmAmiId",
            parameter_name="AmiId",
            string_value=ami_id,
            type=ssm.ParameterType.STRING,
            description="AMI ID for EC2 instance",
        )

        ami_id_parameter_store = ssm.StringParameter.from_string_parameter_name(
            self, "ExistingSsmAmidID",
            string_parameter_name=ssm_ami_id_name,
        )

        if use_ami_id_from_ssm:
            ami_map_value = {aws_region: ami_id_parameter_store.string_value}
        else:
            ami_map_value = {aws_region: parameter_store.string_value}

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

        ec2_user_data = ec2.UserData.for_linux()
        ec2_user_data.add_commands(
            '''
                sudo systemctl start amazon-ssm-agent;
                sudo amazon-linux-extras install -y epel && sudo yum -y install ansible;
            '''
          )

        for i in range(0, instances_count):
            ec2_instance = ec2.Instance(
                self, f"EC2Instance{i}",
                vpc=vpc,
                security_group=security_group,
                key_name=ssh_key_name,
                instance_type=ec2.InstanceType(
                    instance_type_identifier="t2.micro",
                ),
                machine_image=ec2.GenericLinuxImage(
                    ami_map=ami_map_value,
                ),
                vpc_subnets=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PUBLIC,
                ),
                user_data=ec2_user_data,
            )

            if ssm_policy is not None:
                ec2_instance.add_to_role_policy(
                statement=iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                    "ssm:DescribeAssociation",
                    "ssm:GetDeployablePatchSnapshotForInstance",
                    "ssm:GetDocument",
                    "ssm:DescribeDocument",
                    "ssm:GetManifest",
                    "ssm:GetParameter",
                    "ssm:GetParameters",
                    "ssm:ListAssociations",
                    "ssm:ListInstanceAssociations",
                    "ssm:PutInventory",
                    "ssm:PutComplianceItems",
                    "ssm:PutConfigurePackageResult",
                    "ssm:UpdateAssociationStatus",
                    "ssm:UpdateInstanceAssociationStatus",
                    "ssm:UpdateInstanceInformation",
                    "ssmmessages:CreateControlChannel",
                    "ssmmessages:CreateDataChannel",
                    "ssmmessages:OpenControlChannel",
                    "ssmmessages:OpenDataChannel",
                    "ec2messages:AcknowledgeMessage",
                    "ec2messages:DeleteMessage",
                    "ec2messages:FailMessage",
                    "ec2messages:GetEndpoint",
                    "ec2messages:GetMessages",
                    "ec2messages:SendReply",
                    ],
                    resources=["*"],
                    )
                )
                ec2_instance.add_to_role_policy(
                    statement=iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=[
                            "s3:GetObject",
                            "s3:GetBucketLocation"
                        ],
                        resources=["arn:aws:s3:::*"],
                    )
                )
    
            core.CfnOutput(
            self, f"InstanceIP{i}",
            value=f"ssh -i \"{ssh_key_name}.pem\" ec2-user@{ec2_instance.instance_public_ip}"
            )

        ec2_tags = core.Tag.add(
            self,
            key=ec2_tag_key,
            value=ec2_tag_value,
            include_resource_types=["AWS::EC2::Instance"],
        )

        # s3buckets = S3BucketsConstruct(self, "S3Bucket", num_buckets=0)

        lambda_ssm = LambdaSsmConstruct(self, "LambdaSsm", 
                                        ec2_tag_key=ec2_tag_key,
                                        ec2_tag_value=ec2_tag_value, 
                                        playbook_url=playbook_url,
                                        log_level=log_level,
                                        playbook_file_name=playbook_file_name)

#aws ec2 describe-images --region us-east-1 --owners 099720109477 --filters 'Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-????????' 'Name=state,Values=available' | head -n50
#aws ec2 describe-images --region us-east-1 --owners amazon --filters 'Name=name,Values=amzn2-ami-hvm-2.0.????????-x86_64-gp2' 'Name=state,Values=available' --query 'reverse(sort_by(Images, &CreationDate))[:1].ImageId' --output text
#arn:aws:iam::846580235911:instance-profile/AmazonSSMRoleForInstancesQuickSetup
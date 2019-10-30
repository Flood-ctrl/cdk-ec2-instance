from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_ssm as ssm,
    aws_iam as iam,
    aws_logs as logs,
)

from s3_buckets_construct import S3BucketsConstruct
from ssm_association_construct import SSMAssociationConstruct
from lambda_ssm.lambda_ssm_construct import LambdaSsmConstruct
from shared_vpc.shared_vpc_construct import SharedVpcConstruct


class EC2Instance(core.Stack):

    def __init__(self, scope: core.Construct, id: str,
                 env: dict,
                 ec2_tag_key="cdk", 
                 ec2_tag_value=["instance"], 
                 playbook_url=None,
                 playbook_file_name=None,
                 vpc_id: str =None,
                 vpc_name: str =None,
                 private_subnet_names: list =None,
                 instances_count=1,
                 ssm_policy=None,
                 log_level='INFO',
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        aws_region = env['region']

        ami_id_parameter_store = ssm.StringParameter.from_string_parameter_name(
            self, "ExistingSsmAmidID",
            string_parameter_name="centos-ami-id",
        )

        ami_map_value = {aws_region: ami_id_parameter_store.string_value}

        # if use_ami_id_from_ssm:
            
        # else:
        #     ami_map_value = {aws_region: "ami-01d9d5f6cecc31f85"}

        
        shared_subnet_1_id = ssm.StringParameter.from_string_parameter_name(
            self, "shared_subnet_1_id",
            string_parameter_name="shared_subnet_1"
        )

        shared_subnet_2_id = ssm.StringParameter.from_string_parameter_name(
            self, "shared_subnet_2_id",
            string_parameter_name="shared_subnet_2"
        )


        def ec2_cfn_nginx_instance(id, subnet_id, 
                                   nginx_type: str='ec2-instance', 
                                   instance_type: str='t2.micro') -> ec2.CfnInstance:

            ec2_cfn_nginx_instance = ec2.CfnInstance(
                self, id,
                image_id=ami_map_value[aws_region],
                instance_type=instance_type,
                subnet_id=subnet_id,
                tags=[
                    core.CfnTag(
                        key = 'Name',
                        value = f'{nginx_type}-nginx'
                    ),
                ],
            )

        ec2_cfn_nginx_instance(
            id = "EC2NginxInternal",
            subnet_id = shared_subnet_1_id.string_value,
            nginx_type = "internal",
        )

        ec2_cfn_nginx_instance(
            id = "EC2NginxInternal2",
            subnet_id = shared_subnet_2_id.string_value,
            nginx_type = "external",
        )

        ec2_tags = core.Tag.add(
            self,
            key=ec2_tag_key,
            value=ec2_tag_value,
            include_resource_types=["AWS::EC2::Instance"],
        )

#aws ec2 describe-images --region us-east-1 --owners 099720109477 --filters 'Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-????????' 'Name=state,Values=available' | head -n50
#aws ec2 describe-images --region us-east-1 --owners amazon --filters 'Name=name,Values=amzn2-ami-hvm-2.0.????????-x86_64-gp2' 'Name=state,Values=available' --query 'reverse(sort_by(Images, &CreationDate))[:1].ImageId' --output text
#arn:aws:iam::846580235911:instance-profile/AmazonSSMRoleForInstancesQuickSetup
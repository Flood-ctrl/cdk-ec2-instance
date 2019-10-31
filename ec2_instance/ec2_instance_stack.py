from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_ssm as ssm,
    aws_iam as iam,
    aws_logs as logs,
)


class EC2Instance(core.Stack):

    def __init__(self, scope: core.Construct, id: str,
                 env: dict=None,
                 ami_id: str=None,
                 ec2_tag_key: str=None, 
                 ec2_tag_value: str=None,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        aws_region = env['region']

        ami_id_parameter_store = ssm.StringParameter.from_string_parameter_name(
            self, "ExistingSsmAmidID",
            string_parameter_name="centos-ami-id",
        )

        ami_id = ami_id_parameter_store.string_value

        ami_id_value = {aws_region: ami_id}

        
        shared_subnet_1_id = ssm.StringParameter.from_string_parameter_name(
            self, "shared_subnet_1_id",
            string_parameter_name="shared_subnet_1"
        )

        shared_subnet_2_id = ssm.StringParameter.from_string_parameter_name(
            self, "shared_subnet_2_id",
            string_parameter_name="shared_subnet_2"
        )

        def ec2_cfn_instance(id, 
                             key_name: str=None,
                             subnet_id: str=None,
                             user_data: str=None,
                             instance_name: str='ec2-instance', 
                             instance_type: str='t2.micro') -> ec2.CfnInstance:

            ec2_cfn_instance = ec2.CfnInstance(
                self, id,
                key_name=key_name,
                user_data=user_data,
                image_id=ami_id_value[aws_region],
                instance_type=instance_type,
                subnet_id=subnet_id,
                tags=[
                    core.CfnTag(
                        key = 'Name',
                        value = f'{instance_name}'
                    ),
                ],
            )

        ec2_cfn_instance(
            id = "EC2NginxInternal",
            subnet_id = shared_subnet_1_id.string_value,
            instance_name = "internal",
        )

        ec2_cfn_instance(
            id = "TestWithoutSN",
            instance_name = "TEST",
            subnet_id='subnet-014b6cf8b1ccbda7b',
        )

        if ec2_tag_key and ec2_tag_value is not None:
            ec2_instance_tags = core.Tag.add(
                self,
                key=ec2_tag_key,
                value=ec2_tag_value,
                include_resource_types=["AWS::EC2::Instance"],
            )
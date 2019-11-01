from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_ssm as ssm,
)

from ec2_instance_construct import EC2CfnInstanceConstruct


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

    jenkins = EC2CfnInstanceConstruct(self, id="JenkinsInstance", 
                                      image_id='asdadad', 
                                      instance_name="jenkins1")

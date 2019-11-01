import os
import base64
from aws_cdk import (
    core,
    aws_ec2 as ec2,
)

class EC2CfnInstanceConstruct(core.Construct):

    def __init__(self, scope: core.Construct, id: str,
                 ec2_cfn_instance_id: str,
                 image_id: str,
                 key_name: str=None,
                 subnet_id: str=None,
                 user_data: str=None,
                 aws_region: str=None,
                 ec2_tag_key: str=None, 
                 ec2_tag_value: str=None,
                 user_data_file_name: str=None,
                 security_group_ids :list=None,
                 iam_instance_profile :str=None,
                 ssm_quick_setup_role: bool=False,
                 instance_type: str='t2.micro',
                 instance_name: str='cdk-ec2-instance',
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        def caution_message(variable_1, variable_2):
            print(f'{variable_1} and {variable_2} are both defined!')

        if ssm_quick_setup_role:
            assert iam_instance_profile is None, caution_message('iam_instance_profile', 'ssm_quick_setup_role')
            iam_instance_profile = 'AmazonSSMRoleForInstancesQuickSetup'

        if user_data_file_name is not None:
            assert user_data is None, caution_message('user_data', 'user_data_file_name')
            cwd = os.getcwd()
            with open(f'{cwd}/{user_data_file_name}', 'r') as file:
                userdata = file.read()
            user_data = base64.b64encode(userdata.encode("ascii")).decode('ascii')

        ec2_cfn_instance = ec2.CfnInstance(
            self, ec2_cfn_instance_id,
            key_name=key_name,
            user_data=user_data,
            image_id=image_id,
            instance_type=instance_type,
            security_group_ids=security_group_ids,
            iam_instance_profile=iam_instance_profile,
            subnet_id=subnet_id,
            tags=[
                core.CfnTag(
                    key = 'Name',
                    value = f'{instance_name}'
                ),
            ],
        )

        if ec2_tag_key and ec2_tag_value is not None:
            ec2_instance_tags = core.Tag.add(
                self,
                key=ec2_tag_key,
                value=ec2_tag_value,
                include_resource_types=["AWS::EC2::Instance"],
            )
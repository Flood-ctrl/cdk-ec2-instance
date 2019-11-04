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
                 user_data_file: str=None,
                 security_group_ids :list=None,
                 iam_instance_profile :str=None,
                 instances_count: int=1,
                 ssm_quick_setup_role: bool=False,
                 instance_type: str='t2.micro',
                 instance_name: str='cdk-ec2-instance',
                 **kwargs) -> None:
        """Creates EC2 instance by using aws_ec2.CfnInstance.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.
        :param ec2_cfn_instance_id: EC2 resource ID. Must be unique.
        :param user_data: String of userdata.
        :param user_data_file: The name of the file contains userdata. File should be placed on the same level of app.py. The path can be passed if file placed in dir.
        :param ec2_tag_key: The tag key for created EC2 instance.
        :param ec2_tag_value: The value of the tag key.
        :instances_count: Count of instances should be created (default 1).
        :param ssm_quick_setup_role: If True, EC2 role for SSM for Quick-Setup will be attached to instance (default False).
        """
        super().__init__(scope, id, **kwargs)

        def caution_message(variable_1, variable_2):
            print(f'{variable_1} and {variable_2} are both defined!')

        if ssm_quick_setup_role:
            assert iam_instance_profile is None, caution_message('iam_instance_profile', 'ssm_quick_setup_role')
            iam_instance_profile = 'AmazonSSMRoleForInstancesQuickSetup'

        if user_data_file is not None:
            assert user_data is None, caution_message('user_data', 'user_data_file')
            cwd = os.getcwd()
            with open(f'{cwd}/{user_data_file}', 'r') as file:
                userdata = file.read()
            user_data = base64.b64encode(userdata.encode("ascii")).decode('ascii')

        for i in range(0,instances_count):
            if i == 0:
                tag_value = f'{instance_name}'
            else:
                tag_value = f'{instance_name}-{i}'

            ec2_cfn_instance = ec2.CfnInstance(
                self, ec2_cfn_instance_id + f'{i}',
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
                        value = tag_value
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
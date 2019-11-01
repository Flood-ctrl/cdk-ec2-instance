from aws_cdk import (
    core,
    aws_ec2 as ec2,
)

class EC2CfnInstanceConstruct(core.Construct):

    def __init__(self, scope: core.Construct, id: str,
                 ec2_cfn_instance_id: str,
                 image_id: str,
                 aws_region: str=None,
                 ec2_tag_key: str=None, 
                 ec2_tag_value: str=None,
                 key_name: str=None,
                 subnet_id: str=None,
                 user_data: str=None,
                 instance_name: str='ec2-instance',
                 instance_type: str='t2.micro',
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ec2_cfn_instance = ec2.CfnInstance(
            self, ec2_cfn_instance_id,
            key_name=key_name,
            user_data=user_data,
            image_id=image_id,
            instance_type=instance_type,
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
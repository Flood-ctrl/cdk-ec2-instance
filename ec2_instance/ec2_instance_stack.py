from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_ssm as ssm,
)

from ec2_cfn_instance.ec2_cfn_instance_construct import EC2CfnInstanceConstruct


class EC2Instance(core.Stack):

    def __init__(self, scope: core.Construct, id: str,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ssm_subnet_id = ssm.StringParameter.from_string_parameter_name(
            self, "SsmSubnetId1",
            string_parameter_name='semi_default_subnet_id'
        )

        jenkins = EC2CfnInstanceConstruct(self, "JenkinsInstance", 
                                          ec2_cfn_instance_id="Jenkins", 
                                          image_id='ami-0b898040803850657',
                                          user_data_file='user_data.sh',
                                          key_name="cdk-us-east-1",
                                          security_group_ids=['sg-0f0c525ba2aca0a1a',
                                                             ],
                                          subnet_id=ssm_subnet_id.string_value)
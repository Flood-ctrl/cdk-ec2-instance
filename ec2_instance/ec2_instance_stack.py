from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_ssm as ssm,

)
from lambda_ssm.lambda_ssm_construct import LambdaSsmConstruct
from ec2_cfn_instance.ec2_cfn_instance_construct import EC2CfnInstanceConstruct
from ansible_role_ssm_document.ansible_role_ssm_document_construct import AnsibleRoleSsmDocumentConstruct


class EC2Instance(core.Stack):

    def __init__(self, scope: core.Construct, id: str,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ssm_subnet_id = ssm.StringParameter.from_string_parameter_name(
            self, "SsmSubnetId1",
            string_parameter_name='semi_default_subnet_id'
        )

        ansible_role_doc = AnsibleRoleSsmDocumentConstruct(
            self, "AnsibleWithRoleDocument",
        )

        # lambda_smm = LambdaSsmConstruct(self, "JenkinsPlaybook",
        #                                 playbook_url="s3://s3-jenkinsplaybook/jenkins.yml",
        #                                 ec2_tag_key='HostClass',
        #                                 ec2_tag_value=host_class,
        #                                )

        # jenkins = EC2CfnInstanceConstruct(self, "JenkinsInstance", 
        #                                   ec2_cfn_instance_id="Jenkins", 
        #                                   image_id='ami-0b898040803850657',
        #                                   user_data_file='user_data.sh',
        #                                   instances_count=1,
        #                                   ssm_ec2_managed_iam_role=True,
        #                                   subnet_id=ssm_subnet_id.string_value,
        #                                   ec2_tags={
        #                                       'Name': self.stack_name,
        #                                       'CDK-TYPE': 'EC2-Instance',
        #                                       'Provisioned': 'False',
        #                                       'Test-purpose': 'True',
        #                                   }
        #                                   )
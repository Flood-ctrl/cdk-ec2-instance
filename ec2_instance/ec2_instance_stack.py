import os
import json
from aws_cdk import (
    core,
    aws_ec2 as _ec2,
    aws_ssm as _ssm,
)

from lambda_ssm.lambda_ssm_construct import LambdaSsmConstruct
from ec2_cfn_instance.ec2_cfn_instance_construct import EC2CfnInstanceConstruct
from custom_ssm_document.custom_ssm_document_construct import CustomSsmDocumentConstruct


class EC2Instance(core.Stack):

    def __init__(self, scope: core.Construct, id: str,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ssm_subnet_id = _ssm.StringParameter.from_string_parameter_name(
            self, "SsmSubnetId1",
            string_parameter_name='semi_default_subnet_id'
        )

        # vpc = ec2.Vpc.from_lookup(
        #     self, "ImportedVpc",
        #     vpc_name='shared_vpc'
        # )

        jenkins_tcp_ports = [443,80]
        jenkins_source = '0.0.0.0/0'

        def create_jenkins_sg(sg_ingress_ports, sg_ingress_source):

            vpc = _ec2.Vpc.from_vpc_attributes(
                self, "ImportedSharedVpc",
                availability_zones=['use1-az3'],
                vpc_id='vpc-cddd6fb7',
            )
    
            jenkins_sg = _ec2.SecurityGroup(
                self, "JenkinsSG",
                vpc=vpc,
                security_group_name="jenkins_sg",
                description="Security group for accessing the Jenkins from outside",
            )
    
    
            for port in sg_ingress_ports:
                jenkins_sg.add_ingress_rule(
                    peer=_ec2.Peer.ipv4(sg_ingress_source),
                    connection=_ec2.Port.tcp(port),
                )

            return jenkins_sg.security_group_id 

        jenkins_sg_id = create_jenkins_sg(jenkins_tcp_ports, jenkins_source)

        contact_tag = core.Tag.add(
            self,
            key='Contact',
            value='DeVops'
        )

        apllication_tag = core.Tag.add(
            self,
            key='Applicaton',
            value='Jenkins'
        )

        ssm_document = CustomSsmDocumentConstruct(
            self, "AnsibleSSMDocument",
            json_ssm_document_file='custom_ssm_document/run_ansible_playbook_role.json',
        )

        lambda_smm = LambdaSsmConstruct(self, "JenkinsPlaybook",
                                        playbook_url="s3://s3-jenkinsplaybook-test-purpose/jenkins.yml",
                                        ec2_tag_key='HostClass',
                                        ec2_tag_value='CDK',
                                        ssm_document_name=ssm_document.ssm_document_name,
                                        notification_key_filter_prefix='jenkins.yml'
                                       )

        jenkins = EC2CfnInstanceConstruct(self, "JenkinsInstance", 
                                          ec2_cfn_instance_id="Jenkins", 
                                          image_id='ami-0b898040803850657',
                                          user_data_file='user_data.sh',
                                          instances_count=1,
                                          ssm_ec2_managed_iam_role=True,
                                          subnet_id="subnet-014b6cf8b1ccbda7b",
                                          ec2_tags={
                                              'Name': self.stack_name,
                                              'Contact': 'DevOps',
                                              'CDK-TYPE': 'EC2-Instance',
                                              'Provisioned': 'False',
                                              'Test-purpose': 'True',
                                              'HostClass': 'CDK',
                                          },
                                          security_group_ids=[jenkins_sg_id],
                                          )
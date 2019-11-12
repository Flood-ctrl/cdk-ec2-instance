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

        # vpc = ec2.Vpc.from_lookup(
        #     self, "ImportedVpc",
        #     vpc_name='shared_vpc'
        # )

        jenkins_tcp_ports = [8080,80]
        jenkins_source = '10.10.1.4/32'

        def create_jenkins_sg(sg_ingress_ports, sg_ingress_source):

            vpc = ec2.Vpc.from_vpc_attributes(
                self, "ImportedSharedVpc",
                availability_zones=['use1-az3', 'use1-az5'],
                vpc_id='vpc-0b38b12319bf47d79',
            )
    
            jenkins_sg = ec2.SecurityGroup(
                self, "JenkinsSG",
                vpc=vpc,
                security_group_name="jenkins_sg",
                description="Security group for accessing the Jenkins from outside",
            )
    
    
            for port in sg_ingress_ports:
                jenkins_sg.add_ingress_rule(
                    peer=ec2.Peer.ipv4(sg_ingress_source),
                    connection=ec2.Port.tcp(port),
                )

            return jenkins_sg.security_group_id 

        #print(jenkins_sg_id)
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

        # ansible_role_doc = AnsibleRoleSsmDocumentConstruct(
        #     self, "AnsibleWithRoleDocument",
        # )

        # lambda_smm = LambdaSsmConstruct(self, "JenkinsPlaybook",
        #                                 playbook_url="s3://s3-jenkinsplaybook/jenkins.yml",
        #                                 ec2_tag_key='HostClass',
        #                                 ec2_tag_value=host_class,
        #                                )

        jenkins = EC2CfnInstanceConstruct(self, "JenkinsInstance", 
                                          ec2_cfn_instance_id="Jenkins", 
                                          image_id='ami-0b898040803850657',
                                          user_data_file='user_data.sh',
                                          instances_count=1,
                                          ssm_ec2_managed_iam_role=True,
                                          subnet_id="subnet-0830e74b0217be763",
                                          ec2_tags={
                                              'Name': self.stack_name,
                                              'Contact': 'DevOps',
                                              'CDK-TYPE': 'EC2-Instance',
                                              'Provisioned': 'False',
                                              'Test-purpose': 'True',
                                          }
                                          )
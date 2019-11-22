import os
import json
from aws_cdk import (
    core,
    aws_ec2 as _ec2,
    aws_ssm as _ssm,
    aws_elasticloadbalancingv2 as _elbv2,
)

from lambda_ssm.lambda_ssm_construct import LambdaSsmConstruct
from ec2_cfn_instance.ec2_cfn_instance_construct import EC2CfnInstanceConstruct
from custom_ssm_document.custom_ssm_document_construct import CustomSsmDocumentConstruct
from alb.alb_construct import ALBConstruct


class EC2Instance(core.Stack):

    def __init__(self, scope: core.Construct, id: str,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ec2_beyond_alb = True
        sg_ingress_jenkins_ports = [8080]
        sg_ingress_jenkins_source = '0.0.0.0/0'

        ssm_subnet_id = _ssm.StringParameter.from_string_parameter_name(
            self, "SsmSubnetId1",
            string_parameter_name='semi_default_subnet_id'
        )

        ssm_jenkins_ssl_cert = _ssm.StringParameter.from_string_parameter_name(
            self, "JenkinsSSLCertARN",
            string_parameter_name='jenkins-alb-certificate'
        )

        shared_vpc = _ec2.Vpc.from_vpc_attributes(
            self, "ImportedSharedVpc",
            availability_zones=['use1-az3', 'use1-az5'],
            vpc_id='vpc-cddd6fb7',
            public_subnet_ids=['subnet-014b6cf8b1ccbda7b',
                               'subnet-0b378bea9beb9e12c'],
        )

        def create_jenkins_sg(sg_ingress_ports, sg_ingress_source):

            global jenkins_sg

            jenkins_sg = _ec2.SecurityGroup(
                self, "JenkinsSG",
                vpc=shared_vpc,
                security_group_name="jenkins_sg",
                description="Security group for accessing the Jenkins from outside",
            )

            if not ec2_beyond_alb:
                for port in sg_ingress_ports:
                    jenkins_sg.add_ingress_rule(
                        peer=_ec2.Peer.ipv4(sg_ingress_source),
                        connection=_ec2.Port.tcp(port),
                    )

            return jenkins_sg.security_group_id

        jenkins_sg_id = create_jenkins_sg(
            sg_ingress_jenkins_ports, sg_ingress_jenkins_source)

        contact_tag = core.Tag.add(
            self,
            key='Contact',
            value='DeVops'
        )

        apllication_tag = core.Tag.add(
            self,
            key='Applicaton',
            value='jenkins'
        )

        ssm_document = CustomSsmDocumentConstruct(
            self, "AnsibleSSMDocument",
            json_ssm_document_file='custom_ssm_document/run_ansible_playbook_role.json',
        )

        lambda_smm = LambdaSsmConstruct(self, "JenkinsPlaybook",
                                        playbook_url="s3://s3-jenkinsplaybook-test-purpose/",
                                        ec2_tag_key='Application',
                                        log_level='DEBUG',
                                        ssm_document_name=ssm_document.ssm_document_name,
                                        )

        jenkins = EC2CfnInstanceConstruct(self, "JenkinsInstance",
                                          ec2_cfn_instance_id="Jenkins",
                                          image_id='ami-0b898040803850657',
                                          user_data_file='user_data.sh',
                                          instances_count=1,
                                          full_access_iam_role=False,
                                          ssm_ec2_managed_iam_role=True,
                                          subnet_id="subnet-014b6cf8b1ccbda7b",
                                          ec2_tags={
                                              'Name': self.stack_name,
                                              'Application': 'jenkins',
                                              'Contact': 'DevOps',
                                              'CDK-TYPE': 'EC2-Instance',
                                              'Provisioned': 'False',
                                              'Test-purpose': 'True',
                                              'HostClass': 'cdk',
                                          },
                                          security_group_ids=[jenkins_sg_id],
                                          )

        if ec2_beyond_alb:

            alb = ALBConstruct(self, "JenkinsALB",
                               vpc=shared_vpc,
                               ingress_sg_port=443,
                               ingress_sg_peer='0.0.0.0/0',
                               http_to_https_redirect=True,
                               egress_sg_port=sg_ingress_jenkins_ports[0],
                               egress_security_group=jenkins_sg,
                               target_group_targets_ip=jenkins.ec2_instance_private_ip,
                               listener_port=443,
                               app_target_group_port=sg_ingress_jenkins_ports[0],
                               listener_cerificates=[
                                   ssm_jenkins_ssl_cert.string_value],
                               )

            jenkins_sg.connections.allow_from(
                other=alb.alb_sg,
                port_range=_ec2.Port.tcp(8080)
            )

import os
import base64
from aws_cdk import (
    core,
    aws_ec2 as _ec2,
    aws_iam as _iam,
    aws_route53 as _route53,
)


class EC2CfnInstanceConstruct(core.Construct):

    def __init__(self, scope: core.Construct, id: str,
                 ec2_cfn_instance_id: str,
                 image_id: str,
                 subnet_id: str = None,
                 user_data: str = None,
                 aws_region: str = None,
                 ssh_key_name: str = None,
                 r53_zone_name: str = None,
                 user_data_file: str = None,
                 r53_a_record_name: str = None,
                 r53_hosted_zone_id: str = None,
                 security_group_ids: list = None,
                 iam_instance_profile: str = None,
                 ec2_tags: dict = None,
                 instances_count: int = 1,
                 ssm_ec2_managed_iam_role: bool = False,
                 zero_in_postfix_ec2_name: bool = False,
                 full_access_iam_role: bool = False,
                 iam_role_name: str = 'EC2CfnRole',
                 instance_type: str = 't2.micro',
                 instance_name: str = 'cdk-ec2-instance',
                 **kwargs) -> None:
        """Creates EC2 instance by using aws_ec2.CfnInstance.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.
        :param ec2_cfn_instance_id: EC2 resource ID. Must be unique.
        :param user_data: String of userdata.
        :param user_data_file: The name of the file contains userdata. File should be placed on the same level of app.py. The path can be passed if file placed in dir.
        :param ec2_tags: The tags for created EC2 instance.
        :instances_count: Count of instances should be created (default 1).
        :param ssm_ec2_managed_iam_role: If True, IAM role and EC2 instance profile for managing instances by SSM will be created and attached to EC2 instances (default: False).
        :param zero_in_postfix_ec2_name: If true, zero (0) adds to postfix EC2 name (ec2_instace-0, ec2_instance-1 for example), if False (by default) postfix is starting with one (1) (ec2_instance, ec2_instance-1 for example).
        """
        super().__init__(scope, id, **kwargs)

        # Creating IAM role and EC2 instance profile for SSM managment ability
        def create_ec2_ssm_iam_role():

            lambda_ssm_iam_role = _iam.Role(
                self, "EC2CfnRole",
                assumed_by=_iam.ServicePrincipal("ec2.amazonaws.com"),
                inline_policies={
                    'EC2TagsAccess': _iam.PolicyDocument(
                        statements=[_iam.PolicyStatement(
                            effect=_iam.Effect.ALLOW,
                            actions=[
                                "ec2:DescribeTags",
                                "ec2:CreateTags",
                                "ec2:DeleteTags",
                            ],
                            resources=["*"],
                        ),
                        ],
                    )
                },
                managed_policies=[
                    _iam.ManagedPolicy.from_aws_managed_policy_name(
                        'AmazonSSMManagedInstanceCore'
                    ),
                    _iam.ManagedPolicy.from_aws_managed_policy_name(
                        'AmazonS3ReadOnlyAccess'
                    ),
                ],
                role_name=iam_role_name,
            )

            if full_access_iam_role:

                lambda_ssm_iam_role.add_to_policy(
                    statement=_iam.PolicyStatement(
                        effect=_iam.Effect.ALLOW,
                        actions=[
                            "*",
                        ],
                        resources=["*"],
                    ),
                )

            lambda_ssm_iam_role_instance_profile = _iam.CfnInstanceProfile(
                self, 'EC2CfnRoleProfile',
                roles=[lambda_ssm_iam_role.role_name],
                instance_profile_name=f'{lambda_ssm_iam_role.role_name}',
            )
            return lambda_ssm_iam_role_instance_profile.instance_profile_name

        if ec2_tags is not None:
            try:
                instance_name = ec2_tags['Name']
            except KeyError:
                instance_name = instance_name

        def caution_message(variable_1, variable_2):
            print(f'{variable_1} and {variable_2} are both defined!')

        def ec2_instace_name_value(i, instance_name=instance_name, zero_in_postfix_ec2_name=zero_in_postfix_ec2_name):
            if i == 0 and zero_in_postfix_ec2_name is False:
                instance_name = f'{instance_name}'
            else:
                instance_name = f'{instance_name}-{i}'
            return instance_name

        if ssm_ec2_managed_iam_role:
            assert iam_instance_profile is None, caution_message(
                'iam_instance_profile', 'ssm_ec2_managed_iam_role')
            iam_instance_profile = create_ec2_ssm_iam_role()

        if user_data_file is not None:
            assert user_data is None, caution_message(
                'user_data', 'user_data_file')
            cwd = os.getcwd()
            with open(f'{cwd}/{user_data_file}', 'r') as file:
                userdata = file.read()
            user_data = base64.b64encode(
                userdata.encode("ascii")).decode('ascii')

        for i in range(0, instances_count):
            self.ec2_cfn_instance = _ec2.CfnInstance(
                self, ec2_cfn_instance_id + f'{i}',
                key_name=ssh_key_name,
                user_data=user_data,
                image_id=image_id,
                instance_type=instance_type,
                security_group_ids=security_group_ids,
                iam_instance_profile=iam_instance_profile,
                subnet_id=subnet_id,
                tags=[
                    core.CfnTag(
                        key='Name',
                        value=ec2_instace_name_value(i)
                    ),
                ],
            )

            if ec2_tags is not None:
                for ec2_tag_key, ec2_tag_value in ec2_tags.items():
                    if ec2_tag_key == 'Name':
                        continue
                    ec2_instance_tags = core.Tag.add(
                        self,
                        key=ec2_tag_key,
                        value=ec2_tag_value,
                        include_resource_types=["AWS::EC2::Instance"],
                    )

        if r53_hosted_zone_id and r53_zone_name is not None:
            assert r53_a_record_name is not None, print(
                f'{r53_a_record_name} could not be empty.')
            r53_zone = _route53.HostedZone.from_hosted_zone_attributes(
                self, "R53ImportedHZ",
                hosted_zone_id=r53_hosted_zone_id,
                zone_name=r53_zone_name,
            )

            r53_dns_a_record = _route53.ARecord(
                self, "R53ARecord",
                target=_route53.RecordTarget(
                    values=[self.ec2_cfn_instance.attr_private_ip]
                ),
                zone=r53_zone,
                record_name=f'{r53_a_record_name}.{r53_zone.zone_name}',
            )

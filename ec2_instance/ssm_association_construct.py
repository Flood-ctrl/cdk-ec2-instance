from aws_cdk import (
    core,
    aws_iam as iam,
    aws_ssm as ssm,
)

class SSMAssociationConstruct(core.Construct):

    def __init__(self, scope: core.Construct, id: str, 
    ssm_association_name: str,
    ec2_instance_name,
    **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ssm_association = ssm.CfnAssociation(
            self, "SSMAssociation",
            name=ssm_association_name,
            output_location=None,
            ############################################
            #Parameters are not adding to document!!!!!#
            ############################################
            parameters=core.IResolvable.resolve(
                self,
                {
                    "SourceType": ["S3"],
                    "SourceInfo":["{\"path\":\"s3://test-ansible-pl-hw/playbook.yml\"}"],
                    "InstallDependencies":["True"],
                    "PlaybookFile":["playbook.yml"],
                    "ExtraVariables":["SSM=True"],
                    "Check":["False"],
                    "Verbose":["-v"]
                },
            ),
            targets=[
                ssm.CfnAssociation.TargetProperty(
                    key="tag:CDK-Type",
                    values=["EC2Instance"],
                ),
            ],
        )

        ec2_instance_name.add_to_role_policy(
            statement=iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                "ssm:DescribeAssociation",
                "ssm:GetDeployablePatchSnapshotForInstance",
                "ssm:GetDocument",
                "ssm:DescribeDocument",
                "ssm:GetManifest",
                "ssm:GetParameter",
                "ssm:GetParameters",
                "ssm:ListAssociations",
                "ssm:ListInstanceAssociations",
                "ssm:PutInventory",
                "ssm:PutComplianceItems",
                "ssm:PutConfigurePackageResult",
                "ssm:UpdateAssociationStatus",
                "ssm:UpdateInstanceAssociationStatus",
                "ssm:UpdateInstanceInformation",
                "ssmmessages:CreateControlChannel",
                "ssmmessages:CreateDataChannel",
                "ssmmessages:OpenControlChannel",
                "ssmmessages:OpenDataChannel",
                "ec2messages:AcknowledgeMessage",
                "ec2messages:DeleteMessage",
                "ec2messages:FailMessage",
                "ec2messages:GetEndpoint",
                "ec2messages:GetMessages",
                "ec2messages:SendReply",
                ],
                resources=["*"],
            )
        )
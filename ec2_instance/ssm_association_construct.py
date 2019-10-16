from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_ssm as ssm,
)


class SSMAssociationConstruct(core.Construct):

    def __init__(self, scope: core.Construct, id: str, 
                 playbook_url: str,
                 ec2_instance_name,
                 ec2_tag_key: str,
                 ec2_tag_value: str,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        cfn_include = core.CfnInclude(
            self, "CfnInclude",
            template={
                "Resources": {
                    "SSMAssociation": {
                        "Type" : "AWS::SSM::Association",
                        "Properties" : {
                            "AssociationName" : "SSMRunAnsible" ,
                            "Name" : "AWS-RunAnsiblePlaybook",
                            "Parameters" : {
                                "playbookurl":[playbook_url],
                            },
                            "Targets" : [{
                                "Key": f"tag:{ec2_tag_key}",
                                "Values": [f"{ec2_tag_value}"]
                            }]
                          }
                    }
                }
            }
        )

        #cfn_include.

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

        ec2_instance_name.add_to_role_policy(
            statement=iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:GetObject",
                    "s3:GetBucketLocation"
                ],
                resources=["arn:aws:s3:::*"],
            )
        )
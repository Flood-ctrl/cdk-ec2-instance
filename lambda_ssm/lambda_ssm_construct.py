from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_s3 as _s3,
    aws_s3_notifications as _s3_notifications,
    aws_iam as _iam,
)

class LambdaSsmConstruct(core.Construct):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        lambda_ssm = _lambda.Function(
            self, "S3TriggerHandler",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset('lambda_ssm'),
            handler="ansible_run_command.handler",
        )

        lambda_ssm.add_to_role_policy(
            statement=_iam.PolicyStatement(
                    effect=_iam.Effect.ALLOW,
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
                        "ssm:SendCommand",
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


        s3 = _s3.Bucket(
            self, "s3TestBucketRuAnsPl12",
            bucket_name="s3-testbucketruanspl1"
            )
        
        s3.grant_read(lambda_ssm)

        notification = _s3_notifications.LambdaDestination(lambda_ssm)

        s3.add_event_notification(_s3.EventType.OBJECT_CREATED, notification)
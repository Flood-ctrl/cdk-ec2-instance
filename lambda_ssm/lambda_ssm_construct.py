import json
from aws_cdk import (
    core,
    aws_s3 as _s3,
    aws_iam as _iam,
    aws_events as _events,
    aws_lambda as _lambda,
    aws_events_targets as _events_targets,
    aws_s3_notifications as _s3_notifications,
)

class LambdaSsmConstruct(core.Construct):

    def __init__(self, scope: core.Construct, id: str,
                 ec2_tag_key: str, ec2_tag_value: str,
                 playbook_url: str, playbook_file_name: str,
                 log_level: str,
                 **kwargs) -> None:
        """Creates a new construct node.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.
        :param ec2_tag_key: Key for resources tag (key).
        :param ec2_tag_value: Value for resource tag (value).
        :param log_level: Log level for lambda function (INFO, DEBUG, etc)
        :param playbook_url: S3 URL to Ansible playbook.
        :param playbook_file_name: Ansible playbook file name, if playbook_url is not None playbook_file_name is skipping.
        """
        super().__init__(scope, id, **kwargs)

        def get_s3_bucket_name(self):
            self.playbook_url = playbook_url
            if playbook_url is not None:
                splited_playbook_url = playbook_url.split("/")
                s3_bucket_name = splited_playbook_url[2]
            else:
                s3_bucket_name = None
            return s3_bucket_name

        s3 = _s3.Bucket(
        self, "S3SsmRunCommandBucket",
        bucket_name=get_s3_bucket_name(self)
        )

        if playbook_url is None:
            playbook_url = f's3://{s3.bucket_name}/{playbook_file_name}'

        lambda_ssm = _lambda.Function(
            self, "S3TriggerHandler",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset('lambda_ssm'),
            handler="ansible_run_command.handler",
            environment={
                "LOGLEVEL": f'{log_level}',
                "EC2_TAG_KEY": f'{ec2_tag_key}',
                "EC2_TAG_VALUE": f'{ec2_tag_value}',
                "PLAYBOOK_URL": f'{playbook_url}',
            }
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
                        "ec2:DescribeInstances",
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

        
        s3.grant_read(lambda_ssm)

        notification = _s3_notifications.LambdaDestination(lambda_ssm)

        s3.add_event_notification(_s3.EventType.OBJECT_CREATED, notification)

        cloudwatch_event = _events.Rule(
            self, "CloudWatchEvent",
            enabled=True,
            event_pattern=_events.EventPattern(
                source=["aws.ec2"],
                detail_type=["EC2 Instance State-change Notification"],
                detail={
                    "state": ["running"]
                }
            ),
            targets=[_events_targets.LambdaFunction(lambda_ssm)]
        )

        s3_bucket_path = core.CfnOutput(
            self, "S3PlaybookPath",
            value=f's3://{s3.bucket_name}'
        )

        s3_bucket_console_url = core.CfnOutput(
            self, "S3ConsoleUrl",
            value=f's3.console.aws.amazon.com/s3/buckets/{s3.bucket_name}'
        )
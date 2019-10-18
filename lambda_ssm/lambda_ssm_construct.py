from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_s3 as _s3,
    aws_s3_notifications as _s3_notifications
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

        s3 = _s3.Bucket(
            self, "s3TestBucketRuAnsPl1"
        )

        notification = _s3_notifications.LambdaDestination(lambda_ssm)

        s3.add_event_notification(_s3.EventType.OBJECT_CREATED_PUT, notification)
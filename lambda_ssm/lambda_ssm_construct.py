from aws_cdk import (
    core,
    aws_lambda as _lambda,
)

class LambdaSsmConstruct(core.Construct):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        lambda_ssm = _lambda.Function(
            self, "HelloHandler",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset('lambda_ssm'),
            handler="hello.handler",
        )
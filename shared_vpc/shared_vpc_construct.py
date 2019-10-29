from aws_cdk import (
    core,
    aws_ec2 as _ec2
)

class SharedVpcConstruct(core.Construct):

    def __init__(self, scope: core.Construct, id: str, shared_vpc, **kwargs) -> None:

        shared_vpc(
            vpc_id="vpc-0ae61f8eda26a121e"
        )

from aws_cdk import (
    core,
    aws_ec2 as _ec2
)

class SharedVpcConstruct(core.Construct):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:

        shared_vpc = _ec2.Vpc.from_lookup(
            self, "SharedVpc",
            vpc_id="vpc-0ae61f8eda26a121e"
        )

from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_logs as logs,
)

http_port = 80
task_def_cpu = "256"
task_def_memory_mb = "512"

class EC2Instance(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(
            self, "MyEC2Vpc",
            max_azs=2
        )

        core.CfnOutput(
        self, "LoadBalancerDNS",
        value=elastic_loadbalancer.load_balancer_dns_name
        )

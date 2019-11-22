from aws_cdk import (
    core,
    aws_ec2 as _ec2,
    aws_elasticloadbalancingv2 as _elbv2,
)


class ALBConstruct(core.Construct):

    def __init__(self, scope: core.Construct, id: str,
                 vpc,
                 egress_security_group,
                 app_target_group_port: int,
                 target_group_targets_ip: str,
                 internet_facing: bool = True,
                 ingress_sg_port: int = 80,
                 egress_sg_port: int = 80,
                 alb_name: str = "CDK-ALB",
                 listener_port: int = 80,
                 listener_cerificates: list = None,
                 **kwargs) -> None:
        """Creates Application Load Balancer.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.
        """
        super().__init__(scope, id, **kwargs)

        self.alb_sg = _ec2.SecurityGroup(
            self, "ALBSG",
            vpc=vpc,
            security_group_name="ALB_SG",
            description="SG for ALB",
        )

        self.alb_sg.add_ingress_rule(
            peer=_ec2.Peer.ipv4('0.0.0.0/0'),
            connection=_ec2.Port.tcp(ingress_sg_port),
        )

        # self.alb_sg.add_egress_rule(
        #     peer=_ec2.Connections(
        #         security_groups=egress_security_group,
        #     ),
        #     connection=_ec2.Port.tcp(8080),
        # )

        self.alb_sg.connections.allow_to(
            other=egress_security_group,
            port_range=_ec2.Port.tcp(egress_sg_port)
        )

        alb_target_group = _elbv2.ApplicationTargetGroup(
            self, "AppTargetGroup",
            port=app_target_group_port,
            vpc=vpc,
            target_type=_elbv2.TargetType.IP,
            targets=[_elbv2.IpTarget(
                target_group_targets_ip
            )],
        )

        alb = _elbv2.ApplicationLoadBalancer(
            self, "ALB",
            vpc=vpc,
            internet_facing=internet_facing,
            load_balancer_name=alb_name,
            security_group=self.alb_sg,
        )

        alb_listener = _elbv2.ApplicationListener(
            self, "ALBListener",
            load_balancer=alb,
            port=listener_port,
            certificate_arns=listener_cerificates,
            default_target_groups=[alb_target_group],
        )

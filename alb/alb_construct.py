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
                 http_to_https_redirect: bool = False,
                 ingress_sg_port: int = 80,
                 ingress_sg_peer: str = None,
                 sg_name: str = "alb_sg",
                 sg_description: str = "ALB Security group",
                 id_prefix: str = None,
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
            self, f"{id_prefix}ALBSecurityGroup",
            vpc=vpc,
            security_group_name=sg_name,
            description=sg_description,
        )

        self.alb_sg.add_ingress_rule(
            peer=_ec2.Peer.ipv4(ingress_sg_peer),
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
            self, f"{id_prefix}AppTargetGroup",
            port=app_target_group_port,
            vpc=vpc,
            target_type=_elbv2.TargetType.IP,
            targets=[_elbv2.IpTarget(
                target_group_targets_ip
            )],
        )

        self.alb = _elbv2.ApplicationLoadBalancer(
            self, f"{id_prefix}ALB",
            vpc=vpc,
            internet_facing=internet_facing,
            load_balancer_name=alb_name,
            security_group=self.alb_sg,
        )

        alb_listener = _elbv2.ApplicationListener(
            self, f"{id_prefix}ALBListener",
            load_balancer=self.alb,
            port=listener_port,
            certificate_arns=listener_cerificates,
            default_target_groups=[alb_target_group],
        )


        # Rederect from http to https
        assert listener_port != 80, "Listener port could not be 80."
        if http_to_https_redirect:

            http_listener = self.alb.add_listener(
                'HttpListener',
                port=80
            )

            http_listener.add_fixed_response(f"{id_prefix}DummyResponse",
                                             status_code='404')

            http_listener_rule = _elbv2.CfnListenerRule(
                self, f"{id_prefix}HttpListenerRule",
                actions=[
                    {
                        "type": "redirect", "redirectConfig": {
                            "protocol": "HTTPS",
                            "port": "443",
                            "host": "#{host}",
                            "path": "/#{path}",
                            "query": "#{query}",
                            "statusCode": "HTTP_301"
                        }
                    }
                ],
                priority=1,
                listener_arn=http_listener.listener_arn,
                conditions=[
                    {
                        "field": 'path-pattern',
                        "values": ['*']
                    }
                ],

            )

from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_ssm as ssm,
)


class SSMAssociationConstruct(core.Construct):

    def __init__(self, scope: core.Construct, id: str, 
                 playbook_url: str,
                 ec2_tag_key: str,
                 ec2_tag_value: str,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        if playbook_url is not None:
            cfn_include = core.CfnInclude(
                self, "CfnInclude",
                template={
                    "Resources": {
                        "SSMAssociation": {
                            "Type" : "AWS::SSM::Association",
                            "Properties" : {
                                "AssociationName" : "SSMRunAnsible" ,
                                "Name" : "AWS-RunAnsiblePlaybook",
                                "ScheduleExpression": "cron(0 0/30 * * * ? *)",
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
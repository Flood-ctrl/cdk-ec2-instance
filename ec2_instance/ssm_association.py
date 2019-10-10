from aws_cdk import (
    core,
    aws_ssm as ssm,
)

class SSMAssociation(core.Construct):

    def __init__(self, scope: core.Construct, id: str, 
    ssm_association_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ssm_param_values = ssm.CfnAssociation.ParameterValuesProperty(
            parameter_values=["s3://test-ansible-pl-hw/playbook.yml"],
        )

        ssm_tartgets = ssm.CfnAssociation.TargetProperty(
            key="CDK-Type",
            values="EC2Instance",
        ),

        ssm_association = ssm.CfnAssociation(
            self, "SSMAssociation",
            name=ssm_association_name,
            output_location=None,
            parameters={
                "playbookurl": ssm_param_values,
            },

            targets=None,
        )
from aws_cdk import (
    core,
    aws_ssm as ssm,
)

class SSMAssociation(core.Construct):

    def __init__(self, scope: core.Construct, id: str, 
    ssm_association_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        parameters_map={
            "playbookurl": ssm.CfnAssociation.ParameterValuesProperty(
                parameter_values=["s3://test-ansible-pl-hw/playbook.yml"],
            ),
        }

        ssm_tartgets = ssm.CfnAssociation.TargetProperty(
            key="CDK-Type",
            values="EC2Instance",
        ),

        ssm_association = ssm.CfnAssociation(
            self, "SSMAssociation",
            name=ssm_association_name,
            output_location=None,
            parameters=core.IResolvable.resolve(
                self,
                {
                "SourceType": ["S3"],
                "SourceInfo":["{\"path\":\"s3://test-ansible-pl-hw/playbook.yml\"}"],
                "InstallDependencies":["True"],
                "PlaybookFile":["playbook.yml"],
                "ExtraVariables":["SSM=True"],
                "Check":["False"],
                "Verbose":["-v"]
            },
            ),

            targets=None,
        )
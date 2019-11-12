import os
import json
from aws_cdk import (
    core,
    aws_ssm as _ssm,
)

class AnsibleRoleSsmDocumentConstruct(core.Construct):

    def __init__(self, scope: core.Construct, id: str,
                 ssm_document_parameter_name: str='ansible_role_ssm_document',
                 **kwargs) -> None:
        """Creates SSM Document.
        """
        super().__init__(scope, id, **kwargs)

        with open('ansible_role_ssm_document/run_ansible_playbook_role.json') as f:
          ansible_playbook_role_file = json.load(f)

        ssm_document = _ssm.CfnDocument(
            self, "SSMDocument",
            document_type='Command',
            content=ansible_playbook_role_file,
            tags=[core.CfnTag(
                key='Name',
                value='RunAnsibleRole'
            ),
            ]
        )

        self.ssm_document_name = ssm_document.ref
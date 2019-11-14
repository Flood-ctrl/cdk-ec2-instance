import os
import json
from aws_cdk import (
    core,
    aws_ssm as _ssm,
)

class CustomSsmDocumentConstruct(core.Construct):

    def __init__(self, scope: core.Construct, id: str,
                 json_ssm_document_file: str='ssm_document.json',
                 **kwargs) -> None:
        """Creates SSM Document.
        :param json_ssm_document_file: JSON SSM Document file name, could be a path (dirname/ssm_document)
        """
        super().__init__(scope, id, **kwargs)

        with open(json_ssm_document_file) as f:
          ssm_document_content = json.load(f)

        ssm_document = _ssm.CfnDocument(
            self, "CustomSSMDocument",
            document_type='Command',
            content=ssm_document_content,
            tags=[core.CfnTag(
                key='Name',
                value='RunAnsibleRole'
            ),
            ]
        )

        # Attribute for invoking SSM Document name from other construct
        self.ssm_document_name = ssm_document.ref
import json
from aws_cdk import (
    core,
    aws_ssm as _ssm,
)

class AnsibleRoleSsmDocumentConstruct(core.Construct):

    def __init__(self, scope: core.Construct, id: str,
                 **kwargs) -> None:
        """Creates a new construct node.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.
        :param ec2_tag_key: Key for resources tag (key).
        :param ec2_tag_value: Value for resource tag (value).
        :param log_level: Log level for lambda function (INFO, DEBUG, etc)
        :param playbook_url: S3 URL to Ansible playbook.
        :param playbook_file_name: Ansible playbook file name, if playbook_url is not None playbook_file_name is skipping.
        """
        super().__init__(scope, id, **kwargs)

        ssm_document = _ssm.CfnDocument(
            self, "SSMDocument",
            content={
                   "schemaVersion": "2.0",
                   "description": "Use this document to run Ansible playbooks on Amazon EC2 managed instances. Specify either YAML text or URL. If you specify both, the URL parameter will be used. Use the extravar parameter to send runtime variables to the Ansible execution. Use the check parameter to perform a dry run of the Ansible execution. The output of the dry run shows the changes that will be made when the playbook is executed.",
                   "parameters": {
                     "playbook": {
                       "type": "String",
                       "description": "(Optional) If you don't specify a URL, then you must specify playbook YAML in this field.",
                       "default": "",
                       "displayType": "textarea"
                     },
                     "playbookurl": {
                       "type": "String",
                       "description": "(Optional) If you don't specify playbook YAML, then you must specify a URL where the playbook is stored. You can specify the URL in the following formats: http://example.com/playbook.yml  or s3://examplebucket/plabook.url. For security reasons, you can't specify a URL with quotes.",
                       "default": "",
                       "allowedPattern": "^\\s*$|^(http|https|s3)://[^']*$"
                     },
                     "extravars": {
                       "type": "String",
                       "description": "(Optional) Additional variables to pass to Ansible at runtime. Enter a space separated list of key/value pairs. For example: color=red flavor=lime",
                       "default": "SSM=True",
                       "displayType": "textarea",
                       "allowedPattern": "^$|^\\w+\\=\\S+(\\s\\w+\\=\\S+)*$"
                     },
                     "check": {
                       "type": "String",
                       "description": " (Optional) Use the check parameter to perform a dry run of the Ansible execution.",
                       "allowedValues": [
                         "True",
                         "False"
                       ],
                       "default": "False"
                     }
                   },
                   "mainSteps": [
                     {
                       "action": "aws:runShellScript",
                       "name": "runShellScript",
                       "inputs": {
                         "runCommand": [
                           "#!/bin/bash",
                           "ansible --version",
                           "if [ $? -ne 0 ]; then",
                           " echo \"Ansible is not installed. Please install Ansible and rerun the command\" >&2",
                           " exit 1",
                           "fi",
                           "execdir=$(dirname $0)",
                           "cd $execdir",
                           "if [ -z '{{playbook}}' ] ; then",
                           " if [[ \"{{playbookurl}}\" == http* ]]; then",
                           "   wget '{{playbookurl}}' -O playbook.yml",
                           "   if [ $? -ne 0 ]; then",
                           "       echo \"There was a problem downloading the playbook. Make sure the URL is correct and that the playbook exists.\" >&2",
                           "       exit 1",
                           "   fi",
                           " elif [[ \"{{playbookurl}}\" == s3* ]] ; then",
                           "   aws --version",
                           "   if [ $? -ne 0 ]; then",
                           "       echo \"The AWS CLI is not installed. The CLI is required to process Amazon S3 URLs. Install the AWS CLI and run the command again.\" >&2",
                           "       exit 1",
                           "   fi",
                           "   playbook_url={{playbookurl}}",
                           "   playbook_dir=${playbook_url%/*}",
                           "   plabook_file=${playbook_url##*/}",
                           "   aws s3 sync $playbook_dir .",
                           "   if [ $? -ne 0 ]; then",
                           "       echo \"Error while downloading the document from S3\" >&2",
                           "       exit 1",
                           "   fi",
                           " else",
                           "   echo \"The playbook URL is not valid. Verify the URL and try again.\"",
                           " fi",
                           "else",
                           " echo '{{playbook}}' > playbook.yml",
                           "fi",
                           "if  [[ \"{{check}}\" == True ]] ; then",
                           "   ansible-playbook -i \"localhost,\" --check -c local -e \"{{extravars}}\" $plabook_file",
                           "else",
                           "   ansible-playbook -i \"localhost,\" -c local -e \"{{extravars}}\" $plabook_file",
                           "fi"
                         ]
                       }
                     }
                   ]
                 }
        )
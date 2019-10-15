aws_region = "us-east-1"
ssh_key_name = "cdk-us-east-1"
use_ami_id_from_ssm = True          #Use AMI id from exitsting parameters store
ssm_ami_id_name = "centos-ami-id"
ami_id = "ami-01d9d5f6cecc31f85"    #Ubuntu AMI
ec2_tag_key = "CDK-Type"
ec2_tag_value = "EC2Instance"
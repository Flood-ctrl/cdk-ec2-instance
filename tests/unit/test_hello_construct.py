import unittest

from aws_cdk import core

from ec2_instance.ec2_instance_construct import EC2InstanceConstruct

class TestEC2Instance(unittest.TestCase):

    def setUp(self):
        self.app = core.App()
        self.stack = core.Stack(self.app, "TestStack")
    
    def test_num_buckets(self):
        num_buckets = 1
        hello = EC2InstanceConstruct(self.stack, "Test1", num_buckets)
        assert len(hello.buckets) == num_buckets
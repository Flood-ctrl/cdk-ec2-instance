import unittest

from aws_cdk import core

from s3_buckets_construct import S3BucletsConstruct

class TestS3Buclets(unittest.TestCase):

    def setUp(self):
        self.app = core.App()
        self.stack = core.Stack(self.app, "TestStack")
    
    def test_num_buckets(self):
        num_buckets = 1
        s3buckets = S3BucletsConstruct(self.stack, "Test1", num_buckets)
        assert len(s3buckets.buckets) == num_buckets
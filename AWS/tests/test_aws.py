import unittest
from aws import AWS

class TestAWS(unittest.TestCase):
    def setUp(self):
        self.aws=AWS()

    def test_create_topic(self):
        """Create Test_Topic"""
        self.assertTrue(self.aws.create_topic('Test_Topic'))

    def test_create_queue(self):
        """Create Test_Queue"""
        self.assertTrue(self.aws.create_queue('Test_Queue'))

    def test_add_policy(self):
        """Add security policy to SQS"""
        self.aws.create_topic('Test_Topic')

        self.aws.create_queue('Test_Queue')
        self.assertTrue(self.aws.add_policy())

        self.aws.create_topic('Test_Topic2')
        self.assertTrue(self.aws.add_policy())

        self.aws.delete_policy()

    def test_subscribe_to_topic(self):
        """Subscribe queue to topic"""
        self.aws.create_topic('Test_Topic')
        self.aws.create_queue('Test_Queue')
        self.assertTrue(self.aws.subscribe_to_topic())

    def test_receive_message(self):
        """Send/receive message"""
        my_topic = 'Test_Receive_Topic'
        self.aws.create_topic(my_topic)
        self.aws.create_queue('Test_Queue')
        self.assertTrue(self.aws.subscribe_to_topic())
        self.assertTrue(self.aws.add_policy())
        self.aws.register_player(my_topic)
        self.aws.send_message(my_topic, 'This is a test')
        self.assertTrue(self.aws.receive_message())

    def test_send_message_to_bad_queue(self):
        """
        Send message to non-existant queue to make sure it handles things in an
        elegant manner
        """
        my_topic = 'bad_things'
        message = {'handle': 'eschew_obfuscation'}
        resp = self.aws.send_message(my_topic, message)
        self.assertFalse(resp['success'])

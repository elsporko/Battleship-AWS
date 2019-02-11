import boto3
import json
import sys

"""
Module to help facilitate calls to AWS SNS/SQS
"""
class AWS(object):
    """Container to handle interactions with AWS"""
    def __init__(self):
        self.sns = boto3.client('sns', 'us-east-2')
        self.sqs = boto3.client('sqs', 'us-east-2')
        self.sqs_res = boto3.resource('sqs', 'us-east-2')

    def create_topic(self, topic_name):
        print("Creating topic: ", topic_name)
        self.topic = self.sns.create_topic(Name=topic_name)
        self.topic_arn = self.topic['TopicArn']
        print("Topic arn: ", self.topic_arn)
        self.topic_name = topic_name
        return True

    def create_queue(self, queue_name):
        self.queue = self.sqs.create_queue(QueueName=queue_name)
        self.sqs_arn = self.sqs.get_queue_attributes(QueueUrl=self.queue['QueueUrl'], AttributeNames=['QueueArn'])['Attributes']['QueueArn']

        return True

    def add_policy(self):
        """
        Create/Add security policy to queue to allow topics to get tied to them
        """
        self.policy = None
        try:
            self.policy = json.loads(self.get_policy())
            # Do not bother adding a new policy if there is one in place for this topic already
            if self.topic_name in [s['Sid'] for s in self.policy['Statement']]:
                return True
        except KeyError:
            pass

        if not self.policy:
            self.policy = {
                "Version": "2012-10-17",
                "Id": "{}/SQSDefaultPolicy".format(self.sqs_arn),
                "Statement": [],
            }

        #TODO - Add a check to make sure my ARN isn't already in the list
        #if not self.policy_has_permissions_for_topic ():
        #print ("Policy type: ", type(self.policy))
        self.policy['Statement'].append({
          "Sid": self.topic_name,
          "Effect": "Allow",
          "Principal": {
            "AWS": "*"
          },
          "Action": "SQS:SendMessage",
          "Resource": self.sqs_arn,
          "Condition": {
            "ArnEquals": {
              "aws:SourceArn": self.topic_arn
            }
          }
        })
        #print('Policy: ', json.dumps(self.policy))
        self.sqs.set_queue_attributes(QueueUrl=self.queue['QueueUrl'], Attributes={'Policy': json.dumps(self.policy)})
        return True

    def subscribe_to_topic(self):
        """Subscribe to the topic"""
        return self.sns.subscribe(TopicArn=self.topic_arn, Protocol='sqs', Endpoint=self.sqs_arn)
        return True

    def get_policy(self):
        return self.sqs.get_queue_attributes(QueueUrl=self.queue['QueueUrl'], AttributeNames=['Policy'])['Attributes']['Policy']

    def delete_policy(self):
        p = json.loads(self.get_policy())
        p['Statement'] = [s for s in p['Statement'] if not s['Condition']['ArnEquals']['aws:SourceArn'] == self.topic_arn]
        self.policy = p

        self.sqs.set_queue_attributes(QueueUrl=self.queue['QueueUrl'], Attributes={'Policy': json.dumps(self.policy)})
        return True

    def receive_message(self, MaxNumberOfMessages=1, WaitTimeSeconds=20, VisibilityTimeout=10):
        return aws.receive_message(QueueUrl=self.queue.['QueueUrl'],MaxNumberOfMessages=MaxNumberOfMessages, WaitTimeSeconds=WaitTimeSeconds, VisibilityTimeout=VisibilityTimeout)

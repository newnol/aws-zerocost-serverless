# To run this test, you need to install the testing dependencies first:
# pip install boto3 moto pytest

import json
import os
import unittest

import boto3
from moto import mock_aws

# Set required environment variables before importing the lambda function
os.environ["TABLE_NAME"] = "TasksTestTable"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["ALLOWED_ORIGIN"] = "https://d123example.cloudfront.net"


@mock_aws
class TestLambdaFunction(unittest.TestCase):
    def setUp(self):
        """
        Sets up a mock DynamoDB table before each test runs.
        """
        self.dynamodb = boto3.client("dynamodb", region_name="us-east-1")

        # Create a mock table that matches the schema described in project.md
        self.dynamodb.create_table(
            TableName=os.environ["TABLE_NAME"],
            KeySchema=[{"AttributeName": "taskId", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "taskId", "AttributeType": "S"},
                {"AttributeName": "userId", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "userId-index",
                    "KeySchema": [{"AttributeName": "userId", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        # Import the lambda function AFTER setting up the mock environment
        import lambda_function

        self.lambda_handler = lambda_function.lambda_handler

        # Force the lambda function to use our mocked DynamoDB resource
        lambda_function.dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        lambda_function.table = lambda_function.dynamodb.Table(os.environ["TABLE_NAME"])

    def test_cors_options(self):
        """Test the CORS preflight OPTIONS request."""
        event = {"httpMethod": "OPTIONS"}
        response = self.lambda_handler(event, None)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(
            response["headers"]["Access-Control-Allow-Origin"],
            "https://d123example.cloudfront.net",
        )

    def test_post_create_task(self):
        """Test creating a new task."""
        event = {
            "httpMethod": "POST",
            "path": "/tasks",
            "body": json.dumps(
                {
                    "title": "Learn AWS Serverless",
                    "priority": "high",
                    "userId": "user123",
                }
            ),
        }

        response = self.lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 201)

        body = json.loads(response["body"])
        self.assertIn("taskId", body)
        self.assertEqual(body["title"], "Learn AWS Serverless")
        self.assertEqual(body["status"], "pending")

    def test_get_tasks_by_user(self):
        """Test retrieving tasks for a specific user using the GSI."""
        # 1. Create a task first
        self.test_post_create_task()

        # 2. Query the tasks
        event = {
            "httpMethod": "GET",
            "path": "/tasks",
            "queryStringParameters": {"userId": "user123"},
        }

        response = self.lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 200)

        body = json.loads(response["body"])
        self.assertTrue(isinstance(body, list))
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["userId"], "user123")
        self.assertEqual(body[0]["title"], "Learn AWS Serverless")

    def test_put_update_task(self):
        """Test updating an existing task."""
        # 1. Create a task
        create_event = {
            "httpMethod": "POST",
            "path": "/tasks",
            "body": json.dumps({"title": "Initial Title"}),
        }
        create_response = self.lambda_handler(create_event, None)
        task_id = json.loads(create_response["body"])["taskId"]

        # 2. Update the task
        update_event = {
            "httpMethod": "PUT",
            "path": f"/tasks/{task_id}",
            "pathParameters": {"id": task_id},
            "body": json.dumps({"title": "Updated Title", "status": "done"}),
        }

        update_response = self.lambda_handler(update_event, None)
        self.assertEqual(update_response["statusCode"], 200)

        # 3. Verify the update
        get_event = {
            "httpMethod": "GET",
            "path": "/tasks",
            "queryStringParameters": {"userId": "user123"},
        }
        get_response = self.lambda_handler(get_event, None)
        tasks = json.loads(get_response["body"])
        updated_task = next(t for t in tasks if t["taskId"] == task_id)

        self.assertEqual(updated_task["title"], "Updated Title")
        self.assertEqual(updated_task["status"], "done")

    def test_delete_task(self):
        """Test deleting a task."""
        # 1. Create a task
        create_event = {
            "httpMethod": "POST",
            "path": "/tasks",
            "body": json.dumps({"title": "To be deleted"}),
        }
        create_response = self.lambda_handler(create_event, None)
        task_id = json.loads(create_response["body"])["taskId"]

        # 2. Delete the task
        delete_event = {
            "httpMethod": "DELETE",
            "path": f"/tasks/{task_id}",
            "pathParameters": {"id": task_id},
        }
        delete_response = self.lambda_handler(delete_event, None)
        self.assertEqual(delete_response["statusCode"], 200)

        # 3. Verify it was deleted
        get_event = {
            "httpMethod": "GET",
            "path": "/tasks",
            "queryStringParameters": {"userId": "user123"},
        }
        get_response = self.lambda_handler(get_event, None)
        tasks = json.loads(get_response["body"])
        self.assertEqual(len(tasks), 0)


if __name__ == "__main__":
    unittest.main()

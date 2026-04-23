import json
import boto3
import uuid
import os
from datetime import datetime
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB client
dynamodb = boto3.resource("dynamodb")
table_name = os.environ.get("TABLE_NAME", "Tasks")
table = dynamodb.Table(table_name)
allowed_origin = os.environ.get("ALLOWED_ORIGIN", "https://<cf-domain>")


def build_response(status_code, body=None):
    response = {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": allowed_origin,
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Vary": "Origin",
        },
    }
    if body is not None:
        response["body"] = json.dumps(body)
    return response


def lambda_handler(event, context):
    http_method = event.get("httpMethod")
    path = event.get("resource", event.get("path", ""))

    # Handle preflight CORS
    if http_method == "OPTIONS":
        return build_response(200)

    try:
        if http_method == "GET" and (path == "/tasks" or path.endswith("/tasks")):
            # Fetch all tasks for a specific user using GSI
            # In a real app, userId would come from authorization context
            user_id = (
                event.get("queryStringParameters", {}).get("userId", "user123")
                if event.get("queryStringParameters")
                else "user123"
            )

            response = table.query(
                IndexName="userId-index",
                KeyConditionExpression=Key("userId").eq(user_id),
            )
            return build_response(200, response.get("Items", []))

        elif http_method == "POST" and (path == "/tasks" or path.endswith("/tasks")):
            # Create a new task
            body = json.loads(event.get("body", "{}"))

            task_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat() + "Z"

            item = {
                "taskId": task_id,
                "userId": body.get("userId", "user123"),
                "title": body.get("title", "Untitled Task"),
                "description": body.get("description", ""),
                "priority": body.get("priority", "medium"),
                "dueDate": body.get("dueDate", ""),
                "status": body.get("status", "pending"),
                "createdAt": timestamp,
            }

            table.put_item(Item=item)
            return build_response(201, item)

        elif http_method == "PUT" and "/tasks/" in path:
            # Update a task
            path_parameters = event.get("pathParameters", {})
            task_id = path_parameters.get("id")
            if not task_id:
                # Fallback if id is not in pathParameters but in URL
                task_id = path.split("/")[-1]

            body = json.loads(event.get("body", "{}"))

            # Build update expression dynamically based on provided fields
            update_expr = "SET "
            expr_attr_values = {}
            expr_attr_names = {}

            updatable_fields = ["title", "description", "priority", "dueDate", "status"]
            updates = []

            for field in updatable_fields:
                if field in body:
                    updates.append(f"#{field} = :{field}")
                    expr_attr_values[f":{field}"] = body[field]
                    expr_attr_names[f"#{field}"] = field

            if not updates:
                return build_response(400, {"message": "No valid fields to update"})

            update_expr += ", ".join(updates)

            response = table.update_item(
                Key={"taskId": task_id},
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_attr_values,
                ExpressionAttributeNames=expr_attr_names,
                ReturnValues="ALL_NEW",
            )

            return build_response(200, response.get("Attributes", {}))

        elif http_method == "DELETE" and "/tasks/" in path:
            # Delete a task
            path_parameters = event.get("pathParameters", {})
            task_id = path_parameters.get("id")
            if not task_id:
                task_id = path.split("/")[-1]

            table.delete_item(Key={"taskId": task_id})
            return build_response(
                200, {"message": f"Task {task_id} deleted successfully"}
            )

        else:
            return build_response(404, {"message": "Not Found"})

    except Exception as e:
        print(f"Error: {str(e)}")
        return build_response(
            500, {"message": "Internal Server Error", "error": str(e)}
        )

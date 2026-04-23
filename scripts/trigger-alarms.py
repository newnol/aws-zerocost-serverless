import argparse
import json
import sys
import time

import boto3
import requests

# ==============================================================================
# Script Name: trigger-alarms.py
# Description: Automates the process of triggering the two mandatory CloudWatch
#              Alarms for the project by simulating errors:
#              1. API-5xx-Alarm (Needs > 5 API Gateway 5XX errors in 5 mins)
#              2. Lambda-Error-Alarm (Needs > 10 Lambda errors in 5 mins)
# ==============================================================================


def trigger_lambda_errors(function_name, region, count):
    print(
        f"[*] Triggering {count} Lambda errors for function '{function_name}' in region '{region}'..."
    )

    # Initialize boto3 client for Lambda
    try:
        lambda_client = boto3.client("lambda", region_name=region)
    except Exception as e:
        print(f"[!] Failed to initialize boto3 client: {e}")
        print(
            "    Ensure you have AWS credentials configured (e.g., via 'aws configure')."
        )
        return

    # Payload designed to cause an unhandled AttributeError in the Lambda.
    # Passing a string instead of a dict will crash `event.get("httpMethod")`
    # before the try-except block, causing a true Lambda execution error.
    error_payload = json.dumps("this_string_causes_attribute_error")

    success_triggers = 0

    for i in range(1, count + 1):
        try:
            print(f"    - Sending error payload {i}/{count}...", end=" ", flush=True)
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType="RequestResponse",  # Wait for response to ensure it fails
                Payload=error_payload,
            )

            # Check if Lambda reported a function error
            if "FunctionError" in response:
                print(f"Error triggered successfully! ({response['FunctionError']})")
                success_triggers += 1
            else:
                print(
                    f"Invoked, but no FunctionError detected. Check your lambda logic."
                )

            # Sleep slightly to avoid throttling ourselves too hard
            time.sleep(0.5)

        except Exception as e:
            print(f"Failed to invoke: {e}")

    print(
        f"[*] Successfully sent {success_triggers}/{count} error-inducing requests to Lambda."
    )


def trigger_api_gateway_errors(api_url, count):
    print(f"[*] Triggering {count} API Gateway 5XX errors against '{api_url}'...")
    print("    Note: To reliably trigger a 5XX error from the outside, the Lambda")
    print(
        "    behind the API Gateway must fail, OR you can hit a route that is misconfigured."
    )
    print(
        "    This script sends malformed POST requests hoping to crash the backend integration."
    )

    success_triggers = 0
    # Send raw text instead of JSON to cause a JSONDecodeError in the Lambda's json.loads()
    headers = {"Content-Type": "text/plain"}

    # This invalid JSON string will trigger the Exception block in the Lambda, returning a 500 status code
    malformed_body = "this is not valid json {"

    for i in range(1, count + 1):
        try:
            print(f"    - Sending broken request {i}/{count}...", end=" ", flush=True)

            response = requests.post(api_url, data=malformed_body, headers=headers)

            # We are looking for 5xx errors (500, 502, 503, 504)
            if response.status_code >= 500:
                print(f"Got 5XX error! (Status: {response.status_code})")
                success_triggers += 1
            else:
                print(
                    f"Got status {response.status_code} (Not a 5XX). You may need to manually throw an error in your code."
                )

            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

    print(
        f"[*] Successfully received {success_triggers}/{count} 5XX errors from API Gateway."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Trigger CloudWatch Alarms by generating errors."
    )

    # Subparsers for the two different targets
    subparsers = parser.add_subparsers(dest="target", help="Choose what to trigger")
    subparsers.required = True

    # Parser for Lambda
    lambda_parser = subparsers.add_parser(
        "lambda", help="Trigger Lambda errors directly"
    )
    lambda_parser.add_argument(
        "--name", required=True, help="The exact name of the Lambda function"
    )
    lambda_parser.add_argument(
        "--region", default="us-east-1", help="AWS Region (default: us-east-1)"
    )
    lambda_parser.add_argument(
        "--count",
        type=int,
        default=12,
        help="Number of errors to generate (default: 12, to beat the >10 threshold)",
    )

    # Parser for API Gateway
    api_parser = subparsers.add_parser("api", help="Trigger API Gateway 5XX errors")
    api_parser.add_argument(
        "--url",
        required=True,
        help="The API Gateway Endpoint URL (e.g., https://xyz.execute-api.us-east-1.amazonaws.com/prod/tasks)",
    )
    api_parser.add_argument(
        "--count",
        type=int,
        default=7,
        help="Number of errors to generate (default: 7, to beat the >5 threshold)",
    )

    args = parser.parse_args()

    print("==========================================================")
    print(" CloudWatch Alarm Trigger Utility")
    print("==========================================================")
    print("IMPORTANT: CloudWatch Alarms are evaluated over a 5-minute period.")
    print("After running this script, you must wait up to 5 minutes to see")
    print("the alarm state change to 'In alarm' on the AWS Console.")
    print("==========================================================\n")

    if args.target == "lambda":
        trigger_lambda_errors(args.name, args.region, args.count)
    elif args.target == "api":
        # Ensure requests library is available for API testing
        try:
            import requests
        except ImportError:
            print(
                "[!] The 'requests' module is missing. Please install it using: pip install requests"
            )
            sys.exit(1)

        trigger_api_gateway_errors(args.url, args.count)

    print(
        "\n[*] Script execution finished. Please check your CloudWatch Console in a few minutes."
    )

#!/bin/bash

# ==============================================================================
# Script Name: setup-iam-roles.sh
# Description: Automates the creation of two IAM Roles required for the project:
#              1. LambdaTaskRole (DynamoDB access + Logs + VPC ENI)
#              2. LambdaBaseRole (Logs + VPC ENI only)
# ==============================================================================

# Variables to customize
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
TABLE_NAME="TasksTable"

# Construct DynamoDB ARN
DYNAMODB_TABLE_ARN="arn:aws:dynamodb:${REGION}:${ACCOUNT_ID}:table/${TABLE_NAME}"

# Trust policy for Lambda
cat <<EOF > trust-policy.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Policy for LambdaTaskRole
cat <<EOF > task-role-policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": "${DYNAMODB_TABLE_ARN}"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:${REGION}:${ACCOUNT_ID}:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:CreateNetworkInterface",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DeleteNetworkInterface"
            ],
            "Resource": "*"
        }
    ]
}
EOF

# Policy for LambdaBaseRole (No DynamoDB access)
cat <<EOF > base-role-policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:${REGION}:${ACCOUNT_ID}:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:CreateNetworkInterface",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DeleteNetworkInterface"
            ],
            "Resource": "*"
        }
    ]
}
EOF

echo "Creating LambdaBaseRole..."
aws iam create-role \
    --role-name LambdaBaseRole \
    --assume-role-policy-document file://trust-policy.json

echo "Attaching inline policy to LambdaBaseRole..."
aws iam put-role-policy \
    --role-name LambdaBaseRole \
    --policy-name LambdaBaseRolePolicy \
    --policy-document file://base-role-policy.json

echo "Creating LambdaTaskRole..."
aws iam create-role \
    --role-name LambdaTaskRole \
    --assume-role-policy-document file://trust-policy.json

echo "Attaching inline policy to LambdaTaskRole..."
aws iam put-role-policy \
    --role-name LambdaTaskRole \
    --policy-name LambdaTaskRolePolicy \
    --policy-document file://task-role-policy.json

# Clean up temporary JSON files
rm trust-policy.json task-role-policy.json base-role-policy.json

echo "========================================================================"
echo "IAM Roles created successfully!"
echo "Role 1: LambdaTaskRole (ARN: arn:aws:iam::${ACCOUNT_ID}:role/LambdaTaskRole)"
echo "Role 2: LambdaBaseRole (ARN: arn:aws:iam::${ACCOUNT_ID}:role/LambdaBaseRole)"
echo "Next steps for IAM Evidence:"
echo "1. Take a screenshot of IAM > Roles showing these two roles (IM-1)."
echo "2. Open LambdaTaskRole > Inline Policy > JSON and screenshot it to show the specific Resource ARN (IM-2)."
echo "3. Go to Lambda functions, assign these roles, and screenshot the Configuration > Permissions tab (IM-3)."
echo "========================================================================"

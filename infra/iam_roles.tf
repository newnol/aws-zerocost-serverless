terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

variable "region" {
  description = "The AWS region to deploy the resources in"
  type        = string
  default     = "us-east-1"
}

variable "table_name" {
  description = "The name of the DynamoDB table"
  type        = string
  default     = "TasksTable"
}

data "aws_caller_identity" "current" {}

locals {
  account_id         = data.aws_caller_identity.current.account_id
  dynamodb_table_arn = "arn:aws:dynamodb:${var.region}:${local.account_id}:table/${var.table_name}"
}

# ------------------------------------------------------------------------------
# IAM Role 1: LambdaTaskRole (DynamoDB Access + Logs + VPC)
# ------------------------------------------------------------------------------
resource "aws_iam_role" "lambda_task_role" {
  name = "LambdaTaskRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_task_role_policy" {
  name = "LambdaTaskRolePolicy"
  role = aws_iam_role.lambda_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = local.dynamodb_table_arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.region}:${local.account_id}:*"
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface"
        ]
        # VPC actions don't support specific resources for these operations
        Resource = "*"
      }
    ]
  })
}

# ------------------------------------------------------------------------------
# IAM Role 2: LambdaBaseRole (Logs + VPC Only, NO DynamoDB Access)
# ------------------------------------------------------------------------------
resource "aws_iam_role" "lambda_base_role" {
  name = "LambdaBaseRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_base_role_policy" {
  name = "LambdaBaseRolePolicy"
  role = aws_iam_role.lambda_base_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.region}:${local.account_id}:*"
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface"
        ]
        Resource = "*"
      }
    ]
  })
}

output "lambda_task_role_arn" {
  value = aws_iam_role.lambda_task_role.arn
}

output "lambda_base_role_arn" {
  value = aws_iam_role.lambda_base_role.arn
}

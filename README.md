# AWS Zero-Cost Serverless Task Manager

A fully serverless task management application built on AWS, designed with a **zero-cost architecture** — staying within AWS Free Tier limits by eliminating NAT Gateways, using VPC Endpoints for private DynamoDB access, and leveraging pay-per-use serverless services.

## Architecture

```
User → CloudFront → S3 (Static Frontend)
                         ↓
                   API Gateway (REST)
                         ↓
                   Lambda (Python)
                         ↓ (via VPC Endpoint — no NAT)
                      DynamoDB
```

**Key design decisions:**
- **No NAT Gateway** — Lambda runs in a private VPC subnet and reaches DynamoDB through a VPC Endpoint (`com.amazonaws.*.dynamodb`), avoiding the $32+/month NAT cost.
- **CloudFront + S3** — Static frontend served via CloudFront with S3 Block Public Access enforced; direct S3 access returns 403.
- **Least-privilege IAM** — Two separate roles: `LambdaTaskRole` (DynamoDB + Logs) and `LambdaBaseRole` (Logs only).
- **CloudWatch monitoring** — Dashboard with 5 widgets, alarms for Lambda errors and API Gateway 5XX.

## Tech Stack

| Layer | Service |
|---|---|
| Frontend | HTML/CSS/JS hosted on **Amazon S3** + **CloudFront** |
| API | **Amazon API Gateway** (REST, `prod` stage) |
| Backend | **AWS Lambda** (Python 3.x) |
| Database | **Amazon DynamoDB** (on-demand billing) |
| Networking | **VPC** with private subnets + **VPC Endpoint** for DynamoDB |
| Security | **IAM roles**, S3 Block Public Access, CloudFront OAC |
| Monitoring | **CloudWatch** Dashboard + Alarms + **AWS Budgets** |
| IaC | **Terraform** (IAM roles) + AWS CLI / Console |

## Repository Structure

```
aws-zerocost-serverless/
├── backend/
│   ├── lambda_function.py      # Lambda handler — CRUD for tasks
│   └── test_lambda.py          # Unit tests (moto + pytest)
├── frontend/
│   ├── index.html              # Single-page Task Manager UI
│   └── app.js                  # Vanilla JS — fetch API calls
├── infra/
│   └── iam_roles.tf            # Terraform — LambdaTaskRole & LambdaBaseRole
├── scripts/
│   ├── setup-iam-roles.sh      # Bash alternative to Terraform for IAM setup
│   ├── traffic_generator.py    # Generates realistic traffic (burst + steady)
│   └── trigger-alarms.py       # Forces CloudWatch alarms into ALARM state
├── docs/
│   ├── screenshots/            # Evidence screenshots (IAM, VPC, CloudWatch…)
│   └── screenshot-evidence-checklist.md
├── report/
│   └── main.tex                # LaTeX project report (Vietnamese)
├── PROJECT2_EN.pdf             # Project requirements (English)
├── .gitignore
└── README.md
```

## API Endpoints

Base URL: `https://<api-id>.execute-api.<region>.amazonaws.com/prod`

| Method | Path | Description |
|---|---|---|
| `GET` | `/tasks?userId={id}` | List all tasks for a user |
| `POST` | `/tasks` | Create a new task |
| `PUT` | `/tasks/{taskId}` | Update an existing task |
| `DELETE` | `/tasks/{taskId}` | Delete a task |

### Task Schema (DynamoDB)

| Field | Type | Notes |
|---|---|---|
| `taskId` | String (PK) | UUID v4 |
| `userId` | String (GSI) | Used for per-user queries |
| `title` | String | Required |
| `description` | String | Optional |
| `priority` | String | `low` / `medium` / `high` |
| `dueDate` | String | ISO date |
| `status` | String | `pending` / `done` |
| `createdAt` | String | ISO timestamp (UTC) |

## Running the Tests

```bash
# Install dependencies
pip install boto3 moto pytest

# Run from the backend directory
cd backend
python -m pytest test_lambda.py -v
```

Tests use **moto** to mock AWS services locally — no real AWS calls are made.

## Infrastructure as Code

IAM roles can be provisioned with either Terraform or the provided shell script:

```bash
# Option 1 — Terraform
cd infra
terraform init
terraform apply

# Option 2 — Shell script (requires AWS CLI configured)
bash scripts/setup-iam-roles.sh
```

## Testing & Monitoring Scripts

```bash
# Generate 1 hour of realistic traffic (burst + steady) to populate CloudWatch metrics
python scripts/traffic_generator.py

# Force CloudWatch alarms into ALARM state for demonstration
python scripts/trigger-alarms.py lambda --name <FunctionName> --region <region>
python scripts/trigger-alarms.py api --url <ApiGatewayURL>/tasks
```

## Cost Analysis

| Service | Free Tier Limit | Projected Usage |
|---|---|---|
| Lambda | 1M requests / 400K GB-s / month | Well within free tier |
| API Gateway | 1M REST calls / month | Well within free tier |
| DynamoDB | 25 GB storage, 25 RCU/WCU | On-demand; within free tier |
| S3 | 5 GB storage, 20K GET, 2K PUT | Minimal static files |
| CloudFront | 1 TB transfer, 10M requests | Within free tier |
| **NAT Gateway** | **Not used** | **$0** |

**Estimated monthly cost: ~$0** (within AWS Free Tier)

## Security Highlights

- S3 bucket has all four **Block Public Access** settings enabled — direct object URLs return `403 Forbidden`.
- CloudFront uses **Origin Access Control (OAC)** to be the only authorized reader of S3 objects.
- Lambda runs in a **private VPC subnet** with no internet gateway route.
- DynamoDB is accessed via a **VPC Endpoint** (Gateway type) — traffic never leaves the AWS network.
- IAM follows **least privilege**: the task Lambda role only has the six DynamoDB actions it needs, scoped to the exact table ARN.

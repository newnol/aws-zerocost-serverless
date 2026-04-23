# Architecture Diagram Spec

## Final Recommended Layout

- Left edge: `Browser`
- Upper-left group `Frontend`: `CloudFront` -> `Private S3 Bucket`
- Center-left group `API`: `API Gateway` -> `Lambda Task API`
- Upper-center group `IAM`: `LambdaTaskRole` and `LambdaBaseRole`
- Center-right group `VPC 10.0.0.0/16`: `Custom VpcConfig`, `Lambda SG`, `Private Subnet A`, `Private Subnet B`, `Private Route Table`, `Gateway VPCE`
- Far right: `DynamoDB`
- Lower-right group `Ops`: `CloudWatch`, `SNS`, `AWS Budgets`

Use left-to-right request flow on the main row. Keep the monitoring and cost section detached in the lower-right so instructors can grade the primary path without crossing lines.

## Exact Text Labels

Place these labels exactly as shown:

- Diagram title: `Zero-Cost Secure Serverless Task Manager`
- Group title: `Frontend`
- Group title: `IAM`
- Group title: `API`
- Group title: `VPC`
- Group title: `Ops`
- VPC title line 2: `10.0.0.0/16`
- Node: `CloudFront`
- Node: `Private S3 Bucket`
- Node line 2: `OAC origin only`
- Node: `API Gateway`
- Node line 2: `CORS: https://<cf-domain>`
- Node: `Lambda Task API`
- Node line 2: `Python CRUD`
- Node: `LambdaTaskRole`
- Node line 2: `DynamoDB + logs + ENI`
- Node: `LambdaBaseRole`
- Node line 2: `logs + ENI only`
- Node: `Custom VpcConfig`
- Node line 2: `SubnetIds + SG`
- Node: `Lambda SG`
- Node line 2: `443 -> DynamoDB PL`
- Group title: `AZ-a`
- Node: `Private Subnet A`
- Node line 2: `10.0.1.0/24`
- Group title: `AZ-b`
- Node: `Private Subnet B`
- Node line 2: `10.0.2.0/24`
- Node: `Private Route Table`
- Node line 2: `pl-xxxx -> vpce-xxxx`
- Node: `No NAT Gateway`
- Node: `Gateway VPCE`
- Node line 2: `DynamoDB`
- Node: `DynamoDB`
- Node line 2: `Tasks`
- Node: `CloudWatch`
- Node line 2: `logs + alarms`
- Node: `SNS`
- Node line 2: `email`
- Node: `AWS Budgets`
- Node line 2: `cost alert`

Use these short edge labels only:

- `HTTPS`
- `OAC`
- `invoke`
- `task role`
- `VpcConfig`
- `subnet`
- `sg`
- `assoc`
- `443`
- `private`
- `logs`
- `metrics`
- `alarm`
- `budget`

## Common Mistakes To Avoid

- Do not place S3 in front of CloudFront. The visible request path must read `Browser -> CloudFront -> S3`.
- Do not draw Lambda talking directly to DynamoDB over the public internet.
- Do not show any NAT Gateway, Internet Gateway route, or public subnet in the VPC section.
- Do not merge the two IAM roles into one icon or one label.
- Do not use `Access-Control-Allow-Origin: *` anywhere in the diagram text.
- Do not omit the explicit route-table text `pl-xxxx -> vpce-xxxx`.
- Do not draw monitoring arrows in the same strong color as the private data path.
- Do not let Ops icons sit in the main request row; keep them lower-right.
- Do not use long paragraph labels on arrows. Keep labels to one or two words.
- Do not let lines cross through the VPC group title or overlap the subnet boxes.

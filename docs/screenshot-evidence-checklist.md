# Screenshot Evidence Checklist

## 1. Frontend Security Evidence
| ID | Nội dung | Trạng thái | Ghi chú |
|----|----------|------------|--------|
| SE-1 | S3 Block Public Access (4/4 enabled) | ✅ | Có (s3_1.png) |
| SE-2 | Direct S3 access → 403 Forbidden | ✅ | Có (s3_4.png) |
| SE-3 | CloudFront access → 200 OK | ✅ | Có (CleanShot frontend) |
| SE-4 | CloudFront OAC settings | ⚠️ | Có nhưng nên chụp đúng Settings page |

## 2. Networking Evidence
| ID | Nội dung | Trạng thái | Ghi chú |
|----|----------|------------|--------|
| NE-1 | VPC Endpoint DynamoDB (Available) | ✅ | Có |
| NE-2 | Lambda VpcConfig | ✅ | Có |
| NE-3 | Route Table → vpce | ✅ | Có |
| NE-4 | No NAT Gateway | ✅ | Có |
| NE-5 | Lambda call DynamoDB success | ⚠️ | Log chưa rõ StatusCode 200 |

## 3. IAM Evidence
| ID | Nội dung | Trạng thái | Ghi chú |
|----|----------|------------|--------|
| IM-1 | 2 IAM Roles riêng biệt | ❌ | Chưa có |
| IM-2 | Policy dùng ARN cụ thể | ⚠️ | Có 1 role, thiếu role còn lại |
| IM-3 | Lambda gắn đúng Role | ❌ | Chưa có |

## 4. Log Evidence
| Nội dung | Trạng thái | Ghi chú |
|----------|------------|--------|
| Successful request log (REPORT) | ✅ | Có |
| Error request log | ❌ | Chưa có |

## 5. Monitoring & Alarms
| Nội dung | Trạng thái | Ghi chú |
|----------|------------|--------|
| CloudWatch Dashboard (5 widgets) | ✅ | Có |
| CloudWatch Alarms (2 cái) | ❌ | Chưa có |
| AWS Budget config | ❌ | Chưa có |

## 6. Cost Report
| Nội dung | Trạng thái | Ghi chú |
|----------|------------|--------|
| Cost Explorer / Billing | ❌ | Chưa có |

## 7. Other Deliverables
| Nội dung | Trạng thái | Ghi chú |
|----------|------------|--------|
| Architecture Diagram | ✅ | Có trong report |

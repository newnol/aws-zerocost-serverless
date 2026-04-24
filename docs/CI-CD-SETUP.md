# CI/CD Setup Guide

Hướng dẫn setup CI/CD cho AWS Zero-Cost Serverless Task Manager.

## Tổng quan

Project này có 3 options để deploy:

1. **GitHub Actions** (Khuyến nghị) - Free và tích hợp sẵn
2. **Travis CI** - Cần tài khoản trả phí
3. **Manual Script** - Deploy thủ công nhanh chóng

## Option 1: GitHub Actions (Khuyến nghị)

### Setup

1. **Tạo AWS IAM User cho CI/CD**

Tạo IAM user với permissions:
- Lambda: `UpdateFunctionCode`, `GetFunction`
- S3: `PutObject`, `DeleteObject`, `ListBucket`
- CloudFront: `CreateInvalidation`

2. **Thêm GitHub Secrets**

Vào repository Settings > Secrets and variables > Actions, thêm:

```
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=ap-southeast-2
LAMBDA_FUNCTION_NAME=TaskManagerFunction
S3_BUCKET_NAME=your-bucket-name
CLOUDFRONT_DISTRIBUTION_ID=your-distribution-id
```

3. **Enable GitHub Actions**

File workflow đã được tạo tại `.github/workflows/deploy.yml`

### Cách hoạt động

- **Trigger**: Tự động chạy khi push code lên branch `main`
- **Manual trigger**: Có thể chạy thủ công từ Actions tab
- **Jobs**:
  1. Test backend với pytest
  2. Deploy backend lên Lambda (nếu tests pass)
  3. Deploy frontend lên S3 + invalidate CloudFront cache

### Chạy thủ công

1. Vào tab **Actions** trong GitHub repo
2. Chọn workflow **Deploy to AWS**
3. Click **Run workflow**

## Option 2: Travis CI

### Setup

1. **Đăng ký Travis CI**

- Truy cập https://travis-ci.com
- Connect với GitHub repository
- **Lưu ý**: Travis CI không còn free tier cho public repos

2. **Thêm Environment Variables**

Trong Travis CI settings, thêm:

```
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=ap-southeast-2
LAMBDA_FUNCTION_NAME=TaskManagerFunction
S3_BUCKET_NAME=your-bucket-name
CLOUDFRONT_DISTRIBUTION_ID=your-distribution-id
```

3. **Enable Repository**

File config đã được tạo tại `.travis.yml`

### Cách hoạt động

- Tự động chạy khi push lên branch `main`
- Stages: test → deploy backend → deploy frontend

## Option 3: Manual Deployment Script

### Setup

Script đã được tạo tại `scripts/deploy.sh`

1. **Cập nhật configuration**

Edit file `scripts/deploy.sh`, thay đổi các giá trị:

```bash
LAMBDA_FUNCTION_NAME="TaskManagerFunction"
S3_BUCKET_NAME="your-task-manager-bucket"
CLOUDFRONT_DISTRIBUTION_ID="your-distribution-id"
AWS_REGION="ap-southeast-2"
```

2. **Đảm bảo AWS CLI đã configured**

```bash
aws configure
```

### Sử dụng

```bash
# Deploy backend only
./scripts/deploy.sh backend

# Deploy frontend only
./scripts/deploy.sh frontend

# Deploy cả hai
./scripts/deploy.sh all
```

Script sẽ:
- Chạy tests trước khi deploy backend
- Package và upload Lambda function
- Sync frontend files lên S3
- Invalidate CloudFront cache

## So sánh các options

| Feature | GitHub Actions | Travis CI | Manual Script |
|---------|---------------|-----------|---------------|
| **Cost** | Free | Paid | Free |
| **Setup** | Dễ | Trung bình | Rất dễ |
| **Auto deploy** | ✅ | ✅ | ❌ |
| **Test trước deploy** | ✅ | ✅ | ✅ |
| **Manual trigger** | ✅ | ❌ | ✅ |
| **Khuyến nghị** | ⭐⭐⭐ | ⭐ | ⭐⭐ |

## Workflow đề xuất

### Development
1. Làm việc trên branch `dev` hoặc feature branch
2. Test local với `pytest`
3. Merge vào `main` khi ready

### Deployment
- **Tự động**: Push lên `main` → GitHub Actions tự deploy
- **Thủ công**: Chạy `./scripts/deploy.sh all` khi cần

## Troubleshooting

### GitHub Actions fails

**Lỗi: "Error: Credentials could not be loaded"**
- Kiểm tra GitHub Secrets đã được thêm đúng chưa
- Verify AWS credentials còn valid

**Lỗi: "AccessDenied"**
- IAM user cần đủ permissions
- Kiểm tra policy attached vào user

### Script fails

**Lỗi: "aws: command not found"**
```bash
pip install awscli
aws configure
```

**Lỗi: "Tests failed"**
- Fix tests trước khi deploy
- Hoặc comment dòng test trong script (không khuyến nghị)

## Best Practices

1. **Luôn chạy tests trước khi deploy**
2. **Không commit AWS credentials vào code**
3. **Sử dụng GitHub Secrets cho sensitive data**
4. **Test trên branch riêng trước khi merge vào main**
5. **Monitor CloudWatch Logs sau mỗi deployment**

## Cost Considerations

- **GitHub Actions**: 2000 phút/tháng (free tier)
- Mỗi deployment ~2-3 phút
- Ước tính: ~600-1000 deployments/tháng trong free tier
- **Khuyến nghị**: Đủ cho hầu hết use cases

## Next Steps

1. Chọn CI/CD option phù hợp
2. Setup theo hướng dẫn trên
3. Test deployment với một thay đổi nhỏ
4. Monitor logs để đảm bảo deploy thành công

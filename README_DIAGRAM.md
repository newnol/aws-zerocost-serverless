# Hướng dẫn tạo Architecture Diagram

## Yêu cầu

Để chạy script `generate_architecture_diagram.py`, bạn cần cài đặt:

1. **Python 3.x** (đã có)
2. **Graphviz** (công cụ vẽ đồ thị)
3. **Python Diagrams library**

## Cài đặt

### Bước 1: Cài đặt Graphviz

```bash
# Trên macOS (sử dụng Homebrew)
brew install graphviz

# Trên Ubuntu/Debian
sudo apt-get install graphviz

# Trên Windows
# Download từ: https://graphviz.org/download/
```

### Bước 2: Cài đặt Python Diagrams

Do có vấn đề với Python 3.14, hãy thử các cách sau:

**Cách 1: Sử dụng virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install diagrams
```

**Cách 2: Cài đặt trực tiếp (nếu pip hoạt động)**
```bash
pip install diagrams
```

**Cách 3: Sử dụng Python phiên bản cũ hơn**
```bash
# Cài đặt Python 3.11 hoặc 3.12
brew install python@3.12
python3.12 -m pip install diagrams
```

### Bước 3: Chạy script

```bash
python3 generate_architecture_diagram.py
```

Script sẽ tạo file `aws_serverless_architecture.png` trong thư mục hiện tại.

## Diagram bao gồm các thành phần

### 1. Frontend Layer
- **CloudFront CDN**: Phân phối nội dung với OAC (Origin Access Control)
- **S3 Bucket (Private)**: Lưu trữ HTML/CSS/JS, chỉ CloudFront có thể truy cập

### 2. API Layer
- **API Gateway (REST API)**: Xử lý CORS và throttling
- **Lambda Functions**: Chạy trong VPC với VpcConfig

### 3. Custom VPC (10.0.0.0/16)
- **Private Subnet AZ-1** (10.0.1.0/24): Lambda instance 1
- **Private Subnet AZ-2** (10.0.2.0/24): Lambda instance 2 (High Availability)
- **VPC Gateway Endpoint**: Kết nối riêng tư đến DynamoDB

### 4. Database
- **DynamoDB**: TasksTable với GSI (userId-index)

### 5. Security (IAM)
- **LambdaTaskRole**: DynamoDB + CloudWatch Logs + VPC ENI permissions
- **LambdaBaseRole**: CloudWatch Logs + VPC ENI permissions

### 6. Monitoring & Cost Control
- **CloudWatch Dashboard**: 5+ widgets (Invocations, Duration, Errors, Throttles, API Latency)
- **CloudWatch Alarms**: Lambda Error Alarm, API 5xx Alarm
- **SNS Topic**: Email notifications
- **AWS Budget**: $0.01/month limit

## Request Flow

1. **Static Assets**: User → CloudFront → S3 (via OAC) → User
2. **API Requests**: User → API Gateway → Lambda (in VPC) → VPC Endpoint → DynamoDB
3. **Monitoring**: Lambda/API Gateway → CloudWatch → Alarms → SNS → Email

## Các điểm quan trọng trong diagram

✓ S3 bucket là PRIVATE (không public)
✓ CloudFront sử dụng OAC để truy cập S3
✓ Lambda chạy TRONG VPC (có VpcConfig)
✓ Lambda kết nối DynamoDB qua VPC Endpoint (KHÔNG qua internet)
✓ KHÔNG có NAT Gateway (zero cost)
✓ High Availability: 2 AZs
✓ IAM Least Privilege: Separate roles
✓ Full monitoring với CloudWatch

## Troubleshooting

Nếu gặp lỗi khi chạy script:

1. **ImportError: No module named 'diagrams'**
   - Chưa cài đặt diagrams library
   - Chạy: `pip install diagrams`

2. **Graphviz not found**
   - Chưa cài đặt Graphviz
   - Chạy: `brew install graphviz` (macOS)

3. **Python version issues**
   - Thử sử dụng Python 3.11 hoặc 3.12 thay vì 3.14

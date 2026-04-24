#!/bin/bash

# Deploy script for AWS Zero-Cost Serverless Task Manager
# Usage: ./deploy.sh [backend|frontend|all]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration - Update these values
LAMBDA_FUNCTION_NAME="TaskManagerFunction"
S3_BUCKET_NAME="your-task-manager-bucket"
CLOUDFRONT_DISTRIBUTION_ID="your-distribution-id"
AWS_REGION="ap-southeast-2"

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

deploy_backend() {
    print_info "Deploying backend to Lambda..."
    
    cd backend
    
    # Run tests first
    print_info "Running tests..."
    python -m pytest test_lambda.py -v
    
    if [ $? -ne 0 ]; then
        print_error "Tests failed! Aborting deployment."
        exit 1
    fi
    
    print_success "Tests passed!"
    
    # Package Lambda function
    print_info "Packaging Lambda function..."
    zip -r function.zip lambda_function.py
    
    # Deploy to Lambda
    print_info "Uploading to Lambda..."
    aws lambda update-function-code \
        --function-name $LAMBDA_FUNCTION_NAME \
        --zip-file fileb://function.zip \
        --region $AWS_REGION
    
    # Wait for update to complete
    print_info "Waiting for Lambda update to complete..."
    aws lambda wait function-updated \
        --function-name $LAMBDA_FUNCTION_NAME \
        --region $AWS_REGION
    
    # Cleanup
    rm function.zip
    
    cd ..
    print_success "Backend deployed successfully!"
}

deploy_frontend() {
    print_info "Deploying frontend to S3..."
    
    cd frontend
    
    # Sync to S3
    print_info "Syncing files to S3..."
    aws s3 sync . s3://$S3_BUCKET_NAME/ \
        --exclude "README.md" \
        --exclude ".DS_Store" \
        --delete \
        --region $AWS_REGION
    
    print_success "Files synced to S3!"
    
    # Invalidate CloudFront cache
    print_info "Invalidating CloudFront cache..."
    aws cloudfront create-invalidation \
        --distribution-id $CLOUDFRONT_DISTRIBUTION_ID \
        --paths "/*" \
        --region $AWS_REGION
    
    cd ..
    print_success "Frontend deployed successfully!"
}

# Main script
case "$1" in
    backend)
        deploy_backend
        ;;
    frontend)
        deploy_frontend
        ;;
    all)
        deploy_backend
        deploy_frontend
        ;;
    *)
        echo "Usage: $0 {backend|frontend|all}"
        echo ""
        echo "Examples:"
        echo "  $0 backend   - Deploy only backend (Lambda)"
        echo "  $0 frontend  - Deploy only frontend (S3 + CloudFront)"
        echo "  $0 all       - Deploy both backend and frontend"
        exit 1
        ;;
esac

print_success "Deployment completed!"

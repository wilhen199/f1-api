terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = local.region
}

resource "random_id" "backend_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "backend_bucket" {
  bucket = "${local.project_name}-tfstate-${random_id.backend_suffix.hex}"

  force_destroy = true
  lifecycle {
    prevent_destroy = false
  }
  tags = {
    Name    = "${local.project_name}-tfstate-${random_id.backend_suffix.hex}"
    Project = local.project_name
  }
}

resource "aws_s3_bucket_versioning" "backend_bucket_versioning" {
  bucket = aws_s3_bucket.backend_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "backend_bucket_access" {
  bucket = aws_s3_bucket.backend_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_bucket_crypto" {
  bucket = aws_s3_bucket.backend_bucket.bucket
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_dynamodb_table" "backend_locks" {
  name         = "${local.project_name}-tfstate-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  attribute {
    name = "LockID"
    type = "S"
  }
  tags = {
    Name    = "${local.project_name}-tfstate-lock"
    Project = local.project_name
  }
}

output "backend_bucket_name" {
  value = aws_s3_bucket.backend_bucket.bucket
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.backend_locks.name
}

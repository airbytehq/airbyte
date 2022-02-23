# This bucket holds terraform.tfstate files for various tf projects.
resource "aws_s3_bucket" "com-airbyte-terraform-state" {
  bucket = "com-airbyte-terraform-state"
  acl    = "private"
  versioning {
    enabled = true
  }
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.terraform_s3_kms.arn
        sse_algorithm     = "aws:kms"
      }
    }
  }
  tags = {
    Name        = "com-airbyte-terraform-state"
  }
}


# Terraform state files can contain secrets, so we should always encrypt 
# the bucket those are on.  Encryption requires a KMS key, which is created here.

resource "aws_kms_key" "terraform_s3_kms" {
  description             = "KMS key for terraform state S3 bucket"
}
resource "aws_kms_alias" "terraform_s3_kms_alias" {
  name          = "alias/terraform_s3_kms"
  target_key_id = aws_kms_key.terraform_s3_kms.key_id
}


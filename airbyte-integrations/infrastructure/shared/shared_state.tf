# Best Practice is to use a remote state file on S3 plus a dynamodb concurrency lock
# https://www.terraform.io/docs/language/state/remote.html
# https://www.terraform.io/docs/language/state/locking.html

# Create a dynamodb table for locking the state file during terraform apply.
# This can be reused by multiple terraform projects just by referencing the resource.
resource "aws_dynamodb_table" "dynamodb-terraform-state-lock" {
  name = "terraform-state-lock-dynamo"
  hash_key = "LockID"
  read_capacity = 20
  write_capacity = 20
  attribute {
    name = "LockID"
    type = "S"
  }
  tags = {
    Name = "DynamoDB Terraform State Lock Table"
  }
}


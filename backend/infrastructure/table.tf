resource "aws_dynamodb_table" "this" {
  name         = "translate-table"
  hash_key     = "id"
  billing_mode = "PAY_PER_REQUEST"

  attribute {
    name = "id"
    type = "S"
  }

  tags = local.tags
}
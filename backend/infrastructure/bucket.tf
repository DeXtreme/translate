resource "aws_s3_bucket" "this" {
  bucket_prefix = "translate-output-"
  tags          = local.tags
}


resource "aws_s3_bucket_lifecycle_configuration" "this" { # A lifecycle hook to delete files after 1 day
  bucket = aws_s3_bucket.this.id

  rule {
    id = "rule-1"
    filter {}
    expiration {
      days = 1
    }
    status = "Enabled"
  }
}
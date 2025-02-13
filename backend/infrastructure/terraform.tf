terraform {
  backend "s3" {
    bucket = "translate-state-bucket"
    region = "us-east-1"
    key    = "terraform.tfstate"
  }
}
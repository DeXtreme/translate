data "aws_iam_policy" "this" {
  name = "AWSLambdaBasicExecutionRole"
}


data "archive_file" "translate" {
  type        = "zip"
  source_dir  = "${path.module}/../api/translate"
  output_path = "${path.module}/files/translate.zip"
}


data "archive_file" "translate-file" {
  type        = "zip"
  source_dir  = "${path.module}/files/translate_file"
  output_path = "${path.module}/files/translate-file.zip"

  depends_on = [ null_resource.this ]
}


resource "null_resource" "this" {
  provisioner "local-exec" {
    command = <<EOT
      rm -rf ${path.module}/files/translate_file
      cp -r ${path.module}/../api/translate_file ${path.module}/files/translate_file
      cd ${path.module}/files/translate_file
      pip install -r requirements.txt -t ./
    EOT
  }

  triggers = {
    always_run = timestamp()
  }
}



data "aws_iam_policy_document" "assumeRole" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      identifiers = ["lambda.amazonaws.com"]
      type        = "Service"
    }
  }
}

data "aws_iam_policy_document" "this" {
  statement {
    effect = "Allow"
    actions = ["translate:TranslateText",
      "translate:TranslateDocument",
      "comprehend:DetectDominantLanguage"
    ]
    resources = ["*"]
  }

  statement {
    effect  = "Allow"
    actions = ["dynamodb:*"]
    resources = [
      aws_dynamodb_table.this.arn,
      "${aws_dynamodb_table.this.arn}/*"
    ]
  }

  statement {
    effect  = "Allow"
    actions = ["s3:*"]
    resources = [
      aws_s3_bucket.this.arn,
      "${aws_s3_bucket.this.arn}/*"
    ]
  }
}

resource "aws_iam_role" "this" {
  name_prefix        = "translate-app-role"
  assume_role_policy = data.aws_iam_policy_document.assumeRole.json
  tags               = local.tags
}

resource "aws_iam_role_policy" "this" {
  role   = aws_iam_role.this.name
  policy = data.aws_iam_policy_document.this.json
}

resource "aws_iam_role_policy_attachment" "this" {
  role       = aws_iam_role.this.name
  policy_arn = data.aws_iam_policy.this.arn
}


resource "aws_lambda_function" "translate" {
  function_name    = "translate-app-translate-lambda"
  description      = "Lambda function for the /translate endpoint"
  role             = aws_iam_role.this.arn
  filename         = data.archive_file.translate.output_path
  handler          = "main.handler"
  source_code_hash = data.archive_file.translate.output_base64sha256
  runtime          = "python3.10"

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.this.name
    }
  }

  tags = local.tags
}

resource "aws_lambda_function" "translate-file" {
  function_name    = "translate-app-translate-file-lambda"
  description      = "Lambda function for the /translate/file endpoint"
  role             = aws_iam_role.this.arn
  filename         = data.archive_file.translate-file.output_path
  handler          = "main.handler"
  source_code_hash = data.archive_file.translate-file.output_base64sha256
  runtime          = "python3.10"

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.this.name
      S3_BUCKET      = aws_s3_bucket.this.bucket
    }
  }

  tags = local.tags
}

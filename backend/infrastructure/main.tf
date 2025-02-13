data "aws_caller_identity" "this" {}

data "aws_region" "this" {}


resource "aws_api_gateway_rest_api" "this" {
  name               = "translate-app-api"
  description        = "The translate app API"
  binary_media_types = ["*/*"]
  tags               = local.tags
}

resource "aws_api_gateway_resource" "translate" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_rest_api.this.root_resource_id
  path_part   = "translate"
}

resource "aws_api_gateway_method" "translate" {
  rest_api_id   = aws_api_gateway_rest_api.this.id
  resource_id   = aws_api_gateway_resource.translate.id
  http_method   = "POST"
  authorization = "NONE"

}

resource "aws_api_gateway_integration" "translate" {
  rest_api_id             = aws_api_gateway_rest_api.this.id
  resource_id             = aws_api_gateway_resource.translate.id
  http_method             = aws_api_gateway_method.translate.http_method
  integration_http_method = "POST"
  
  type = "AWS_PROXY"
  uri  = aws_lambda_function.translate.invoke_arn
}



resource "aws_api_gateway_resource" "translate-file" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_resource.translate.id
  path_part   = "file"
}

resource "aws_api_gateway_method" "translate-file" {
  rest_api_id   = aws_api_gateway_rest_api.this.id
  resource_id   = aws_api_gateway_resource.translate-file.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "translate-file" {
  rest_api_id             = aws_api_gateway_rest_api.this.id
  resource_id             = aws_api_gateway_resource.translate-file.id
  http_method             = aws_api_gateway_method.translate-file.http_method

  content_handling = "CONVERT_TO_TEXT"
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.translate-file.invoke_arn
}



resource "aws_api_gateway_deployment" "this" {
  rest_api_id = aws_api_gateway_rest_api.this.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.translate,
      aws_api_gateway_method.translate,
      aws_api_gateway_integration.translate,
      aws_api_gateway_resource.translate-file,
      aws_api_gateway_method.translate-file,
      aws_api_gateway_integration.translate-file,

    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}


resource "aws_api_gateway_stage" "this" {
  deployment_id = aws_api_gateway_deployment.this.id
  rest_api_id   = aws_api_gateway_rest_api.this.id
  stage_name    = "prod"

  tags = local.tags
}


resource "aws_lambda_permission" "translate" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.translate.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "arn:aws:execute-api:${data.aws_region.this.name}:${data.aws_caller_identity.this.account_id}:${aws_api_gateway_rest_api.this.id}/*/${aws_api_gateway_method.translate.http_method}${aws_api_gateway_resource.translate.path}"
}

resource "aws_lambda_permission" "translate-file" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.translate-file.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "arn:aws:execute-api:${data.aws_region.this.name}:${data.aws_caller_identity.this.account_id}:${aws_api_gateway_rest_api.this.id}/*/${aws_api_gateway_method.translate-file.http_method}${aws_api_gateway_resource.translate-file.path}"
}
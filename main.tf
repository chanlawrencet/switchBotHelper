terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.37"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.7"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  function_name = var.function_name
}

resource "aws_iam_role" "lambda_exec" {
  name = "${local.function_name}-exec"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "basic_execution" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda"
  output_path = "${path.module}/lambda.zip"
}

resource "aws_lambda_function" "door_opener" {
  function_name = local.function_name
  role          = aws_iam_role.lambda_exec.arn
  runtime       = "python3.13"
  handler       = "app.lambda_handler"
  filename      = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout       = 15
  memory_size   = 256

  environment {
    variables = {
      SWITCHBOT_TOKEN     = var.switchbot_token
      SWITCHBOT_SECRET    = var.switchbot_secret
      LINK_SIGNING_SECRET = var.link_signing_secret
      DEVICE_ID           = var.device_id
      LINK_TTL_SECONDS    = tostring(var.link_ttl_seconds)
    }
  }
}

resource "aws_lambda_function_url" "door_opener" {
  function_name      = aws_lambda_function.door_opener.function_name
  authorization_type = "NONE"

  cors {
    allow_origins = ["*"]
    allow_methods = ["GET"]
    allow_headers = ["*"]
    max_age       = 3600
  }
}

resource "aws_lambda_permission" "function_url_invoke" {
  statement_id           = "AllowPublicFunctionUrlInvoke"
  action                 = "lambda:InvokeFunctionUrl"
  function_name          = aws_lambda_function.door_opener.function_name
  principal              = "*"
  function_url_auth_type = "NONE"
}

resource "aws_lambda_permission" "function_invoke" {
  statement_id             = "AllowPublicInvokeForFunctionUrl"
  action                   = "lambda:InvokeFunction"
  function_name            = aws_lambda_function.door_opener.function_name
  principal                = "*"
  invoked_via_function_url = true
}

resource "aws_cloudwatch_log_group" "door_opener" {
  name              = "/aws/lambda/${aws_lambda_function.door_opener.function_name}"
  retention_in_days = 14
}
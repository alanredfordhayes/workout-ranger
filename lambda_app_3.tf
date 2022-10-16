##LOCALS
locals {
  app_3_name = "${var.name}-${random_string.random.result}-instagram"
  #LAMBDA
  ##aws_lambda_function
  aws_lambda_function_app_3_function_name = "${local.app_3_name}"
  aws_lambda_function_app_3_description   = "${local.app_3_name}"
  aws_lambda_function_app_3_timeout       = 20
  ##aws_lambda_permission
  aws_lambda_permission_app_3_statement_id  = "AllowExecutionFromAPIGateway"
  aws_lambda_permission_app_3_action        = "lambda:InvokeFunction"
  aws_lambda_permission_app_3_principal      = "apigateway.amazonaws.com"
  #IAM
  ##aws_iam_role
  aws_iam_role_app_3_name = "${local.app_3_name}"
  ##aws_iam_role_policy_attachment
  aws_iam_role_policy_attachment_app_3_policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ##aws_iam_policy
  aws_iam_policy_app_3_name = "${local.app_3_name}"
  aws_iam_policy_app_3_path  = "/"
  aws_iam_policy_app_3_description = "${local.app_3_name}"
  #Cloudwatch
  ##aws_cloudwatch_log
  aws_cloudwatch_log_app_3_group_name = "${local.app_3_name}"
}

##LAMBDA
resource "aws_lambda_function" "app_3" {
  function_name     = local.aws_lambda_function_app_3_function_name
  description       = local.aws_lambda_function_app_3_description
  timeout           = local.aws_lambda_function_app_3_timeout
  runtime           = "python3.9"
  handler           = "app_3.lambda_handler"
  s3_bucket         = aws_s3_bucket.app_3.id
  s3_key            = aws_s3_object.app_3.key
  source_code_hash  = data.archive_file.app_3.output_base64sha256
  role              = aws_iam_role.app_3.arn
  environment {
    variables = {
      QueueName  = aws_sqs_queue.app_2.name
    }
  }
}

resource "aws_lambda_permission" "app_3" {
  statement_id  = local.aws_lambda_permission_app_3_statement_id
  action        = local.aws_lambda_permission_app_3_action
  function_name = aws_lambda_function.app_3.function_name
  principal     = local.aws_lambda_permission_app_3_principal
}

##S3
data "archive_file" "app_3" { 
  type        = "zip"
  source_dir  = "${path.module}/app_3"
  output_path = "${path.module}/app_3.zip"
}

resource "aws_s3_bucket" "app_3" {
  bucket_prefix = local.app_3_name
  force_destroy = true
}

resource "aws_s3_object" "app_3" {
  bucket  = aws_s3_bucket.app_3.id
  key     = "app_3.zip"
  source  = data.archive_file.app_3.output_path
  etag    = filemd5(data.archive_file.app_3.output_path)
}

##IAM
resource "aws_iam_role" "app_3" {
  name = local.aws_iam_role_app_3_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "app_3" {
  role       = aws_iam_role.app_3.name
  policy_arn = local.aws_iam_role_policy_attachment_app_3_policy_arn
}

resource "aws_iam_policy" "app_3" {
    name = local.aws_iam_policy_app_3_name
    path = local.aws_iam_policy_app_3_path
    description = local.aws_iam_policy_app_3_description
    policy = jsonencode(
      {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "secretsmanager:ListSecrets"
                ],
                "Resource": "*"
            },
            {
                "Sid": "VisualEditor1",
                "Effect": "Allow",
                "Action": [
                    "secretsmanager:GetResourcePolicy",
                    "secretsmanager:GetSecretValue",
                    "sqs:GetQueueUrl",
                    "secretsmanager:DescribeSecret",
                    "sqs:ReceiveMessage",
                    "secretsmanager:ListSecretVersionIds"
                ],
                "Resource": [
                    "arn:aws:sqs:us-east-1:${var.AWS_ACCOUNT_NUMBER}:shopify-wani-social",
                    "arn:aws:secretsmanager:us-east-1:${var.AWS_ACCOUNT_NUMBER}:secret:placid-JmBBUn",
                    "arn:aws:secretsmanager:us-east-1:${var.AWS_ACCOUNT_NUMBER}:secret:workout_ranger_instagram-S594Xg"

                ]
            }
        ]
      }
    )
}

resource "aws_iam_policy_attachment" "app_3" {
  name       = aws_iam_policy.app_3.name
  roles      = [aws_iam_role.app_3.name]
  policy_arn = aws_iam_policy.app_3.arn
}

##cloudwatch
resource "aws_cloudwatch_log_group" "app_3" {
  name = local.aws_cloudwatch_log_app_3_group_name
  retention_in_days = 30
}
##LOCALS
locals {
  app_5_name = "${var.name}-${random_string.random.result}-spotify-shopify"
  #LAMBDA
  ##aws_lambda_function
  aws_lambda_function_app_5_function_name = "${local.app_5_name}"
  aws_lambda_function_app_5_description   = "${local.app_5_name}"
  aws_lambda_function_app_5_timeout       = 150
  ##aws_lambda_permission
  aws_lambda_permission_app_5_statement_id  = "AllowExecutionFromAPIGateway"
  aws_lambda_permission_app_5_action        = "lambda:InvokeFunction"
  aws_lambda_permission_app_5_principal      = "apigateway.amazonaws.com"
  #IAM
  ##aws_iam_role
  aws_iam_role_app_5_name = "${local.app_5_name}"
  ##aws_iam_role_policy_attachment
  aws_iam_role_policy_attachment_app_5_policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ##aws_iam_policy
  aws_iam_policy_app_5_name = "${local.app_5_name}"
  aws_iam_policy_app_5_path  = "/"
  aws_iam_policy_app_5_description = "${local.app_5_name}"
  #Cloudwatch
  ##aws_cloudwatch_log
  aws_cloudwatch_log_app_5_group_name = "${local.app_5_name}"
}

##LAMBDA
resource "aws_lambda_function" "app_5" {
  function_name     = local.aws_lambda_function_app_5_function_name
  description       = local.aws_lambda_function_app_5_description
  timeout           = local.aws_lambda_function_app_5_timeout
  runtime           = "python3.9"
  handler           = "app_5.lambda_handler"
  s3_bucket         = aws_s3_bucket.app_5.id
  s3_key            = aws_s3_object.app_5.key
  source_code_hash  = data.archive_file.app_5.output_base64sha256
  role              = aws_iam_role.app_5.arn
  layers            = [
    "arn:aws:lambda:us-east-1:${var.AWS_ACCOUNT_NUMBER}:layer:openai:2",
    "arn:aws:lambda:us-east-1:${var.AWS_ACCOUNT_NUMBER}:layer:requests-layer:1"
  ]
}

resource "aws_lambda_permission" "app_5" {
  statement_id  = local.aws_lambda_permission_app_5_statement_id
  action        = local.aws_lambda_permission_app_5_action
  function_name = aws_lambda_function.app_5.function_name
  principal     = local.aws_lambda_permission_app_5_principal
}

##S3
data "archive_file" "app_5" { 
  type        = "zip"
  source_dir  = "${path.module}/app_5"
  output_path = "${path.module}/app_5.zip"
}

resource "aws_s3_bucket" "app_5" {
  bucket_prefix = local.app_5_name
  force_destroy = true
}

resource "aws_s3_object" "app_5" {
  bucket  = aws_s3_bucket.app_5.id
  key     = "app_5.zip"
  source  = data.archive_file.app_5.output_path
  etag    = filemd5(data.archive_file.app_5.output_path)
}

##IAM
resource "aws_iam_role" "app_5" {
  name = local.aws_iam_role_app_5_name

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

resource "aws_iam_role_policy_attachment" "app_5" {
  role       = aws_iam_role.app_5.name
  policy_arn = local.aws_iam_role_policy_attachment_app_5_policy_arn
}

resource "aws_iam_policy" "app_5" {
    name = local.aws_iam_policy_app_5_name
    path = local.aws_iam_policy_app_5_path
    description = local.aws_iam_policy_app_5_description
    policy = jsonencode(
        {
          Version = "2012-10-17"
          Statement = [
            {
              "Sid": "VisualEditor0",
              "Effect": "Allow",
              "Action": [
                  "secretsmanager:GetRandomPassword",
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
                  "secretsmanager:DescribeSecret",
                  "secretsmanager:ListSecretVersionIds"
              ],
              "Resource": [
                  "arn:aws:secretsmanager:us-east-1:${var.AWS_ACCOUNT_NUMBER}:secret:workout_ranger_spotify_shopify-Od8Npv",
                  "arn:aws:secretsmanager:us-east-1:${var.AWS_ACCOUNT_NUMBER}:secret:workoutranger_shopify_admin_api_access_token-6vDz4g",
                  "arn:aws:secretsmanager:us-east-1:${var.AWS_ACCOUNT_NUMBER}:secret:placid-JmBBUn",
                  "arn:aws:secretsmanager:us-east-1:${var.AWS_ACCOUNT_NUMBER}:secret:workout_ranger_instagram-S594Xg",
                  "arn:aws:secretsmanager:us-east-1:${var.AWS_ACCOUNT_NUMBER}:secret:openai-lbgVrI"
              ]
            }
          ]
        }
    )
}

resource "aws_iam_policy_attachment" "app_5" {
  name       = aws_iam_policy.app_5.name
  roles      = [aws_iam_role.app_5.name]
  policy_arn = aws_iam_policy.app_5.arn
}

##cloudwatch
resource "aws_cloudwatch_log_group" "app_5" {
  name = local.aws_cloudwatch_log_app_5_group_name
  retention_in_days = 30
}
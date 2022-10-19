##LOCALS
locals {
  app_4_name = "${var.name}-${random_string.random.result}-blogs"
  #LAMBDA
  ##aws_lambda_function
  aws_lambda_function_app_4_function_name = "${local.app_4_name}"
  aws_lambda_function_app_4_description   = "${local.app_4_name}"
  aws_lambda_function_app_4_timeout       = 150
  ##aws_lambda_permission
  aws_lambda_permission_app_4_statement_id  = "AllowExecutionFromAPIGateway"
  aws_lambda_permission_app_4_action        = "lambda:InvokeFunction"
  aws_lambda_permission_app_4_principal      = "apigateway.amazonaws.com"
  #IAM
  ##aws_iam_role
  aws_iam_role_app_4_name = "${local.app_4_name}"
  ##aws_iam_role_policy_attachment
  aws_iam_role_policy_attachment_app_4_policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ##aws_iam_policy
  aws_iam_policy_app_4_name = "${local.app_4_name}"
  aws_iam_policy_app_4_path  = "/"
  aws_iam_policy_app_4_description = "${local.app_4_name}"
  #Cloudwatch
  ##aws_cloudwatch_log
  aws_cloudwatch_log_app_4_group_name = "${local.app_4_name}"
}

##LAMBDA
resource "aws_lambda_function" "app_4" {
  function_name     = local.aws_lambda_function_app_4_function_name
  description       = local.aws_lambda_function_app_4_description
  timeout           = local.aws_lambda_function_app_4_timeout
  runtime           = "python3.9"
  handler           = "app_4.lambda_handler"
  s3_bucket         = aws_s3_bucket.app_4.id
  s3_key            = aws_s3_object.app_4.key
  source_code_hash  = data.archive_file.app_4.output_base64sha256
  role              = aws_iam_role.app_4.arn
}

resource "aws_lambda_permission" "app_4" {
  statement_id  = local.aws_lambda_permission_app_4_statement_id
  action        = local.aws_lambda_permission_app_4_action
  function_name = aws_lambda_function.app_4.function_name
  principal     = local.aws_lambda_permission_app_4_principal
}

##S3
data "archive_file" "app_4" { 
  type        = "zip"
  source_dir  = "${path.module}/app_4"
  output_path = "${path.module}/app_4.zip"
}

resource "aws_s3_bucket" "app_4" {
  bucket_prefix = local.app_4_name
  force_destroy = true
}

resource "aws_s3_object" "app_4" {
  bucket  = aws_s3_bucket.app_4.id
  key     = "app_4.zip"
  source  = data.archive_file.app_4.output_path
  etag    = filemd5(data.archive_file.app_4.output_path)
}

##IAM
resource "aws_iam_role" "app_4" {
  name = local.aws_iam_role_app_4_name

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

resource "aws_iam_role_policy_attachment" "app_4" {
  role       = aws_iam_role.app_4.name
  policy_arn = local.aws_iam_role_policy_attachment_app_4_policy_arn
}

resource "aws_iam_policy" "app_4" {
    name = local.aws_iam_policy_app_4_name
    path = local.aws_iam_policy_app_4_path
    description = local.aws_iam_policy_app_4_description
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
                  "arn:aws:secretsmanager:us-east-1:${var.AWS_ACCOUNT_NUMBER}:secret:workoutranger_shopify_admin_api_access_token-6vDz4g"
              ]
            }
          ]
        }
    )
}

resource "aws_iam_policy_attachment" "app_4" {
  name       = aws_iam_policy.app_4.name
  roles      = [aws_iam_role.app_4.name]
  policy_arn = aws_iam_policy.app_4.arn
}

##cloudwatch
resource "aws_cloudwatch_log_group" "app_4" {
  name = local.aws_cloudwatch_log_app_4_group_name
  retention_in_days = 30
}
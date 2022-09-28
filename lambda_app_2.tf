##LOCALS
locals {
  app_2_name = "${var.name}-${random_string.random.result}-social"
  #LAMBDA
  ##aws_lambda_function
  aws_lambda_function_app_2_function_name = "${local.app_2_name}"
  aws_lambda_function_app_2_description   = "${local.app_2_name}"
  aws_lambda_function_app_2_timeout       = 3
  ##aws_lambda_permission
  aws_lambda_permission_app_2_statement_id  = "AllowExecutionFromAPIGateway"
  aws_lambda_permission_app_2_action        = "lambda:InvokeFunction"
  aws_lambda_permission_app_2_principal      = "apigateway.amazonaws.com"
  #IAM
  ##aws_iam_role
  aws_iam_role_app_2_name = "${local.app_2_name}"
  ##aws_iam_role_policy_attachment
  aws_iam_role_policy_attachment_app_2_policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ##aws_iam_policy
  aws_iam_policy_app_2_name = "${local.app_2_name}"
  aws_iam_policy_app_2_path  = "/"
  aws_iam_policy_app_2_description = "${local.app_2_name}"
  #Cloudwatch
  ##aws_cloudwatch_log
  aws_cloudwatch_log_app_2_group_name = "${local.app_2_name}"
}

##LAMBDA
resource "aws_lambda_function" "app_2" {
  function_name     = local.aws_lambda_function_app_2_function_name
  description       = local.aws_lambda_function_app_2_description
  timeout           = local.aws_lambda_function_app_2_timeout
  runtime           = "python3.9"
  handler           = "app_2.lambda_handler"
  s3_bucket         = aws_s3_bucket.app_2.id
  s3_key            = aws_s3_object.app_2.key
  source_code_hash  = data.archive_file.app_2.output_base64sha256
  role              = aws_iam_role.app_2.arn
  environment {
    variables = {
      TableName1 = local.aws_dynamodb_table_app_1_db_1
      TableName2 = local.aws_dynamodb_table_app_1_db_2
      TableName3 = local.aws_dynamodb_table_app_1_db_3
      TableName4 = local.aws_dynamodb_table_app_1_db_4
      TableName5 = local.aws_dynamodb_table_app_1_db_5
    }
  }
}

resource "aws_lambda_permission" "app_2" {
  statement_id  = local.aws_lambda_permission_app_2_statement_id
  action        = local.aws_lambda_permission_app_2_action
  function_name = aws_lambda_function.app_2.function_name
  principal     = local.aws_lambda_permission_app_2_principal
}

##S3
data "archive_file" "app_2" { 
  type        = "zip"
  source_dir  = "${path.module}/app_2"
  output_path = "${path.module}/app_2.zip"
}

resource "aws_s3_bucket" "app_2" {
  bucket_prefix = local.app_2_name
  force_destroy = true
}

resource "aws_s3_object" "app_2" {
  bucket  = aws_s3_bucket.app_2.id
  key     = "app_2.zip"
  source  = data.archive_file.app_2.output_path
  etag    = filemd5(data.archive_file.app_2.output_path)
}

##IAM
resource "aws_iam_role" "app_2" {
  name = local.aws_iam_role_app_2_name

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

resource "aws_iam_role_policy_attachment" "app_2" {
  role       = aws_iam_role.app_2.name
  policy_arn = local.aws_iam_role_policy_attachment_app_2_policy_arn
}

resource "aws_iam_policy" "app_2" {
    name = local.aws_iam_policy_app_2_name
    path = local.aws_iam_policy_app_2_path
    description = local.aws_iam_policy_app_2_description
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
                  "secretsmanager:ListSecrets"              ],
              "Resource": "*"
            },
            {
              "Sid": "VisualEditor1",
              "Effect": "Allow",
              "Action": [
                  "secretsmanager:GetResourcePolicy",
                  "secretsmanager:GetSecretValue",
                  "dynamodb:PutItem",
                  "secretsmanager:DescribeSecret",
                  "dynamodb:GetItem",
                  "dynamodb:UpdateItem",
                  "dynamodb:UpdateTable",
                  "secretsmanager:ListSecretVersionIds"
              ],
              "Resource": [
                  "arn:aws:dynamodb:us-east-1:${var.AWS_ACCOUNT_NUMBER}:table/${local.aws_dynamodb_table_app_1_db_1}",
                  "arn:aws:dynamodb:us-east-1:${var.AWS_ACCOUNT_NUMBER}:table/${local.aws_dynamodb_table_app_1_db_2}",
                  "arn:aws:dynamodb:us-east-1:${var.AWS_ACCOUNT_NUMBER}:table/${local.aws_dynamodb_table_app_1_db_3}",
                  "arn:aws:dynamodb:us-east-1:${var.AWS_ACCOUNT_NUMBER}:table/${local.aws_dynamodb_table_app_1_db_4}",
                  "arn:aws:dynamodb:us-east-1:${var.AWS_ACCOUNT_NUMBER}:table/${local.aws_dynamodb_table_app_1_db_5}",
                  "arn:aws:secretsmanager:us-east-1:${var.AWS_ACCOUNT_NUMBER}:secret:placid-JmBBUn"
              ]
            }
          ]
        }
    )
}

resource "aws_iam_policy_attachment" "app_2" {
  name       = aws_iam_policy.app_2.name
  roles      = [aws_iam_role.app_2.name]
  policy_arn = aws_iam_policy.app_2.arn
}

##cloudwatch
resource "aws_cloudwatch_log_group" "app_2" {
  name = local.aws_cloudwatch_log_app_2_group_name
  retention_in_days = 30
}
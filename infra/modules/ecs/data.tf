# Trust relationships
data "aws_iam_policy_document" "f1-api-assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "f1-api-policy_ssm_parameters_store" {
  statement {
    actions = [
      "ssm:GetParameters",
      "ssm:GetParameter"
    ]

    resources = [
      aws_ssm_parameter.f1-api-F1COM_BASE_URL.arn,
      aws_ssm_parameter.f1-api-F1COM_APIKEY.arn
    ]
  }
}


resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
}

data "aws_iam_policy_document" "github_trust" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:wilhen199/f1-api:*"]
    }
  }
}

resource "aws_iam_role" "github_actions" {
  name               = "f1-api-github-actions"
  assume_role_policy = data.aws_iam_policy_document.github_trust.json
}


resource "aws_iam_role_policy_attachment" "github_actions_policy" {
  for_each   = toset(local.github_actions_policies)
  role       = aws_iam_role.github_actions.name
  policy_arn = each.value
}

output "github_actions_role_arn" {
  value = aws_iam_role.github_actions.arn
}

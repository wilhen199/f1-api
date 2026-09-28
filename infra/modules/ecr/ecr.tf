resource "aws_ecr_repository" "f1-api-app_ecr_repo" {
  name         = var.ecr_repo_name
  force_delete = true
  tags = {
    project = var.project
  }
}

locals {
  region       = "us-east-1"
  project_name = "f1-api"
  bucket_name  = "f1-api-tfstate-wf"
  table_name   = "f1-api-tfstate-lock"

  github_actions_policies = [
    "arn:aws:iam::aws:policy/AmazonECS_FullAccess",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess",
    "arn:aws:iam::aws:policy/ElasticLoadBalancingFullAccess",
    "arn:aws:iam::aws:policy/AmazonVPCFullAccess",
    "arn:aws:iam::aws:policy/SecretsManagerReadWrite",
    "arn:aws:iam::aws:policy/IAMFullAccess",
  ]
}

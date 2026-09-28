locals {
  project              = "f1-api"
  vpc_cidr             = "10.0.0.0/16"
  availability_zones   = ["us-east-1a", "us-east-1b"]
  public_subnet_cidrs  = ["10.0.0.0/24", "10.0.1.0/24"]
  private_subnet_cidrs = ["10.0.3.0/24", "10.0.4.0/24"]

  ecr_repo_name = "${local.project}-ecr-repo"

  cluster_name                  = "${local.project}-app-cluster"
  app_task_family               = "${local.project}-app-task"
  container_port                = 8000
  app_task_name                 = "${local.project}-app-task"
  ecs_task_definition_role_name = "${local.project}-app-task-execution-role"

  alb_name        = "${local.project}-app-alb"
  ecs_app_tg_name = "${local.project}-app-alb-tg"

  service_name = "${local.project}--app-service"
}

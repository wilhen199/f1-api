module "network" {
  source  = "./modules/network"
  project = local.project

  vpc_cidr             = local.vpc_cidr
  availability_zones   = local.availability_zones
  public_subnet_cidrs  = local.public_subnet_cidrs
  private_subnet_cidrs = local.private_subnet_cidrs
}

module "ecr" {
  source  = "./modules/ecr"
  project = local.project

  ecr_repo_name = local.ecr_repo_name
}

module "ecs" {
  source  = "./modules/ecs"
  project = local.project

  cluster_name                  = local.cluster_name
  service_name                  = local.service_name
  ecs_task_definition_role_name = local.ecs_task_definition_role_name
  ecs_app_tg_name               = local.ecs_app_tg_name
  app_task_family               = local.app_task_family
  alb_name                      = local.alb_name
  app_task_name                 = local.app_task_name
  container_port                = local.container_port
  ecr_repo_url                  = module.ecr.respository_url
  ssm_parameter_values          = var.ssm_parameter_values
  public_subnets                = module.network.public_subnets_ids
  private_subnets               = module.network.private_subnets_ids
  f1-api-vpc_id                 = module.network.vpc_id
}

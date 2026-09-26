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

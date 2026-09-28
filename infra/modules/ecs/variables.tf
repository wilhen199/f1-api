variable "project" {
  description = "Project Name"
  type        = string
}

variable "cluster_name" {
  description = "App Cluster Name"
  type        = string
}

variable "ecr_repo_url" {
  description = "ECR Repository URL"
  type        = string
}

variable "app_task_name" {
  description = "Task Name"
  type        = string
}

variable "app_task_family" {
  description = "Task Family Name"
  type        = string
}

variable "container_port" {
  description = "Container Port"
  type        = number
}

variable "ecs_task_definition_role_name" {
  description = "ECS Task Execution Role Name"
  type        = string
}

variable "ssm_parameter_values" {
  type        = map(string)
  description = "Parameters SSM Values"
}

variable "alb_name" {
  description = "ALB Name"
  type        = string
}

variable "ecs_app_tg_name" {
  description = "ECS Application Target Group Name"
  type        = string
}

variable "service_name" {
  description = "ECS Service Name"
  type        = string
}

variable "public_subnets" {
  description = "Public Subnets for VPC"
  type        = list(string)
}

variable "private_subnets" {
  description = "Private Subnet for VPC"
  type        = list(string)
}

variable "f1-api-vpc_id" {
  description = "VPC ID for app"
  type        = string
}

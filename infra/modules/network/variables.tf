variable "project" {
  description = "Project Name"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR for VPC"
  type        = string
}

variable "public_subnet_cidrs" {
  description = "Public Subnet CIDR for VPC"
  type        = list(string)
}

variable "availability_zones" {
  description = "Availability Zones for Subnets"
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "Public Subnet CIDR for VPC"
  type        = list(string)
}

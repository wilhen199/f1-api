variable "ssm_parameter_values" {
  type        = map(string)
  description = "Parameters SSM Values"
  sensitive   = true
}
variable "image_tag" {
  type        = string
  description = "Docker image tag to deploy"
  default     = "latest"
}

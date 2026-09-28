output "app_url" {
  description = "Load Balancer DNS Name"
  value       = module.ecs.app_url
}

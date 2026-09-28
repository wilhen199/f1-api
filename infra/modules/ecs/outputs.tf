output "app_url" {
  description = "Load Balancer DNS Name"
  value       = aws_lb.f1-api-load_balancer.dns_name
}

output "vpc_id" {
  value = aws_vpc.f1-api-vpc.id
}

output "public_subnets" {
  description = "Public Subnets"
  value       = [aws_subnet.f1-api-public_subnet_1, aws_subnet.f1-api-public_subnet_2]
}

output "private_subnets" {
  description = "Private Subnets"
  value       = [aws_subnet.f1-api-private_subnet_1, aws_subnet.f1-api-private_subnet_2]
}

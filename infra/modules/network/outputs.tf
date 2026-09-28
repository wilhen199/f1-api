output "vpc_id" {
  value = aws_vpc.f1-api-vpc.id
}

output "public_subnets_ids" {
  description = "Public Subnets"
  value       = [aws_subnet.f1-api-public_subnet_1.id, aws_subnet.f1-api-public_subnet_2.id]
}

output "private_subnets_ids" {
  description = "Private Subnets"
  value       = [aws_subnet.f1-api-private_subnet_1.id, aws_subnet.f1-api-private_subnet_2.id]
}

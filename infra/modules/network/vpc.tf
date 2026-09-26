resource "aws_vpc" "f1-api-vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = {
    Name    = "${var.project}-vpc"
    Project = var.project
  }
}

resource "aws_subnet" "f1-api-public_subnet_1" {
  vpc_id            = aws_vpc.f1-api-vpc.id
  cidr_block        = var.public_subnet_cidrs[0]
  availability_zone = var.availability_zones[0]
  tags = {
    Name    = "${var.project}-public-subnet-1"
    Project = var.project
  }
}

resource "aws_subnet" "f1-api-public_subnet_2" {
  vpc_id            = aws_vpc.f1-api-vpc.id
  cidr_block        = var.public_subnet_cidrs[1]
  availability_zone = var.availability_zones[1]
  tags = {
    Name    = "${var.project}-public-subnet-2"
    Project = var.project
  }
}

resource "aws_internet_gateway" "f1-api-igw" {
  vpc_id = aws_vpc.f1-api-vpc.id
  tags = {
    Name    = "${var.project}-igw"
    Project = var.project
  }
}

resource "aws_eip" "f1-api-eip_1" {
  domain = "vpc"
  tags = {
    Name    = "${var.project}-eip-1"
    Project = var.project
  }
  depends_on = [aws_internet_gateway.f1-api-igw]
}

resource "aws_nat_gateway" "f1-api-natgw_1" {
  allocation_id = aws_eip.f1-api-eip_1.id
  subnet_id     = aws_subnet.f1-api-public_subnet_1.id
  tags = {
    Name    = "${var.project}-natgw-1"
    Project = var.project
  }
}

resource "aws_eip" "f1-api-eip_2" {
  domain = "vpc"
  tags = {
    Name    = "${var.project}-eip-2"
    Project = var.project
  }
  depends_on = [aws_internet_gateway.f1-api-igw]
}

resource "aws_nat_gateway" "f1-api-natgw_2" {
  allocation_id = aws_eip.f1-api-eip_2.id
  subnet_id     = aws_subnet.f1-api-public_subnet_2.id
  tags = {
    Name    = "${var.project}-natgw-2"
    Project = var.project
  }
}

resource "aws_subnet" "f1-api-private_subnet_1" {
  vpc_id            = aws_vpc.f1-api-vpc.id
  cidr_block        = var.private_subnet_cidrs[0]
  availability_zone = var.availability_zones[0]
  tags = {
    Name    = "${var.project}-private-subnet-1"
    Project = var.project
  }
}

resource "aws_subnet" "f1-api-private_subnet_2" {
  vpc_id            = aws_vpc.f1-api-vpc.id
  cidr_block        = var.private_subnet_cidrs[1]
  availability_zone = var.availability_zones[1]
  tags = {
    Name    = "${var.project}-private-subnet-2"
    Project = var.project
  }
}

resource "aws_default_route_table" "f1-api-public_route_table" {
  #vpc_id                 = aws_vpc.f1-api-vpc.id
  default_route_table_id = aws_vpc.f1-api-vpc.default_route_table_id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.f1-api-igw.id
  }
  tags = {
    Name    = "${var.project}-public-route-table"
    Project = var.project
  }
}

resource "aws_route_table" "f1-api-private_route_table_1" {
  vpc_id = aws_vpc.f1-api-vpc.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.f1-api-natgw_1.id
  }
  tags = {
    Name    = "${var.project}-private-route-table"
    Project = var.project
  }
}

resource "aws_route_table" "f1-api-private_route_table_2" {
  vpc_id = aws_vpc.f1-api-vpc.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.f1-api-natgw_2.id
  }
  tags = {
    Name    = "${var.project}-private-route-table-2"
    Project = var.project
  }
}

resource "aws_route_table_association" "f1-api-public_rt_assoc_1" {
  subnet_id      = aws_subnet.f1-api-public_subnet_1.id
  route_table_id = aws_default_route_table.f1-api-public_route_table.id
}

resource "aws_route_table_association" "f1-api-public_rt_assoc_2" {
  subnet_id      = aws_subnet.f1-api-public_subnet_2.id
  route_table_id = aws_default_route_table.f1-api-public_route_table.id
}

resource "aws_route_table_association" "f1-api-private_rt_assoc_1" {
  subnet_id      = aws_subnet.f1-api-private_subnet_1.id
  route_table_id = aws_route_table.f1-api-private_route_table_1.id
}

resource "aws_route_table_association" "f1-api-private_rt_assoc_2" {
  subnet_id      = aws_subnet.f1-api-private_subnet_2.id
  route_table_id = aws_route_table.f1-api-private_route_table_2.id
}

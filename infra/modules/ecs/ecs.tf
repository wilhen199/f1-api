resource "aws_ecs_cluster" "f1-api-cluster" {
  name = var.cluster_name
  tags = {
    project = var.project
  }
}

resource "aws_ecs_task_definition" "f1-api-task_definition" {
  family                   = var.app_task_family
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  memory                   = 512
  cpu                      = 256
  execution_role_arn       = aws_iam_role.f1-api-ecs_task_definition_role.arn
  task_role_arn            = aws_iam_role.f1-api-ecs_task_definition_role.arn

  container_definitions = jsonencode([
    {
      name      = var.app_task_name
      image     = var.ecr_repo_url
      cpu       = 256
      memory    = 512
      essential = true
      portMappings = [
        {
          containerPort = "${var.container_port}"
          hostPort      = "${var.container_port}"
        }
      ],
      secrets = [
        {
          name      = "F1COM_BASE_URL"
          valueFrom = aws_ssm_parameter.f1-api-F1COM_BASE_URL.arn
        },
        {
          name      = "F1COM_APIKEY"
          valueFrom = aws_ssm_parameter.f1-api-F1COM_APIKEY.arn
        }
      ],
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.f1-api-logs_group.name
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
  }])
  tags = {
    project = var.project
  }
}


resource "aws_iam_role" "f1-api-ecs_task_definition_role" {
  name               = var.ecs_task_definition_role_name
  assume_role_policy = data.aws_iam_policy_document.f1-api-assume_role.json
  tags = {
    project = var.project
  }
}

resource "aws_iam_role_policy_attachment" "f1-api-role_attachment_ecs" {
  role       = aws_iam_role.f1-api-ecs_task_definition_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_policy" "f1-api-policy_ssm_parameters_store" {
  name        = "f1-api-ssm-parameters-store-policy"
  description = "allow-access-to-ssm-parameter-store from f1-api"
  policy      = data.aws_iam_policy_document.f1-api-policy_ssm_parameters_store.json
}

resource "aws_ssm_parameter" "f1-api-F1COM_BASE_URL" {
  name  = "/f1-api/F1COM_BASE_URL"
  type  = "String"
  value = var.ssm_parameter_values["base_url"]
  tags = {
    Project = var.project
  }
}

resource "aws_ssm_parameter" "f1-api-F1COM_APIKEY" {
  name  = "/f1-api/F1COM_APIKEY"
  type  = "String"
  value = var.ssm_parameter_values["api_key"]
  tags = {
    Project = var.project
  }
}

resource "aws_iam_role_policy_attachment" "f1-api-role_attachment_ssm" {
  role       = aws_iam_role.f1-api-ecs_task_definition_role.name
  policy_arn = aws_iam_policy.f1-api-policy_ssm_parameters_store.arn
}

resource "aws_lb" "f1-api-load_balancer" {
  name               = var.alb_name
  load_balancer_type = "application"
  security_groups    = [aws_security_group.f1-api_alb_sg.id]
  subnets            = var.public_subnets
  depends_on = [
    aws_security_group.f1-api_alb_sg
  ]
  tags = {
    Project = var.project
  }
}

resource "aws_security_group" "f1-api_alb_sg" {
  vpc_id = var.f1-api-vpc_id
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "${var.project}-alb-sg"
    Project = var.project
  }
}

resource "aws_lb_target_group" "f1-api-tg" {
  name        = var.ecs_app_tg_name
  vpc_id      = var.f1-api-vpc_id
  port        = var.container_port
  protocol    = "HTTP"
  target_type = "ip"
  health_check {
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_lb_listener" "f1-api-listener" {
  load_balancer_arn = aws_lb.f1-api-load_balancer.arn
  port              = "80"
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.f1-api-tg.arn
  }
}

resource "aws_ecs_service" "f1-api-app_service" {
  name            = var.service_name
  cluster         = aws_ecs_cluster.f1-api-cluster.id
  task_definition = aws_ecs_task_definition.f1-api-task_definition.id
  desired_count   = 1
  launch_type     = "FARGATE"

  load_balancer {
    target_group_arn = aws_lb_target_group.f1-api-tg.arn
    container_name   = var.app_task_name
    container_port   = var.container_port
  }
  network_configuration {
    subnets          = var.private_subnets
    security_groups  = [aws_security_group.f1-api-ecs_sg.id]
    assign_public_ip = true
  }
}

resource "aws_security_group" "f1-api-ecs_sg" {
  vpc_id = var.f1-api-vpc_id
  ingress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    security_groups = ["${aws_security_group.f1-api_alb_sg.id}"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "${var.project}-ecs-sg"
    Project = var.project
  }
}

resource "aws_cloudwatch_log_group" "f1-api-logs_group" {
  name = "/ecs/f1-api"

  tags = {
    Project = var.project
  }
}

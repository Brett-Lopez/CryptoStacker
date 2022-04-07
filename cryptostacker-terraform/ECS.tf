#https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecs_cluster

resource "aws_ecs_cluster" "csr-flask-web-app-ecs-cluster-tf" {
  name = "csr-flask-web-app-ecs-cluster-tf"
  capacity_providers = ["FARGATE"]

  #todo: might disable later?
  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  default_capacity_provider_strategy {
    capacity_provider = "FARGATE"   #(Required) The short name of the capacity provider.
    weight = 1                      #(Optional) The relative percentage of the total number of launched tasks that should use the specified capacity provider.
    base = 0                        #(Optional) The number of tasks, at a minimum, to run on the specified capacity provider.
  }
}

#https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecs_task_definition
#https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_role
data "aws_iam_role" "ecsTaskExecutionRole" {
  name = "ecsTaskExecutionRole"
}

#https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/ecs_task_definition
data "aws_ecs_task_definition" "csr-flask-web-app-task-def-tf" {
  task_definition = aws_ecs_task_definition.csr-flask-web-app-task-def-tf.family
}

resource "aws_ecs_task_definition" "csr-flask-web-app-task-def-tf" {
  family = "csr-flask-web-app-task-def-tf"
  requires_compatibilities = ["FARGATE"]
  cpu = "4096"
  memory = "8192"
  execution_role_arn = data.aws_iam_role.ecsTaskExecutionRole.arn
  task_role_arn = aws_iam_role.CSR-ECS-TASKS-WWW-WEBAPP-TF.arn 
  network_mode = "awsvpc"
  lifecycle {
    #ignore_changes = ["*"]  #The ["*"] form of ignore_changes wildcard is was deprecated and is now invalid. Use "ignore_changes = all" to ignore changes to all attributes.
    ignore_changes = all
  }

  container_definitions = jsonencode([
        {
        name      = "csr-flask-web-app-tf"
        image     = "370458797273.dkr.ecr.us-east-2.amazonaws.com/csr-flask-web-app-tf:latesta"
        cpu       = 4000
        memory    = 8000
        memoryReservation = 7000
        essential = true
        logConfiguration = {
            logDriver = "awslogs"
            options = {
                awslogs-group = "/ecs/csr-flask-web-app-task-def-tf"
                awslogs-region = "${var.AWS_REGION}"
                awslogs-stream-prefix = "ecs"
                }
            }
        portMappings = [
            {
            hostPort = 8000
            containerPort = 8000
            protocol = "tcp"
            }
        ]
        }
    ]
   )
  }



#Shit is fucked - should work but it doesn't.
# 1/29/22 seems to be fixed with the latest aws module upgrade "3.63.0" -> "3.74.0"
resource "aws_ecs_service" "csr-flask-web-app-service-tf" {
  name            = "csr-flask-web-app-service-tf"
  cluster         = aws_ecs_cluster.csr-flask-web-app-ecs-cluster-tf.id
  task_definition = "csr-flask-web-app-task-def-tf:2"
  desired_count   = 1
  deployment_maximum_percent = 300
  deployment_minimum_healthy_percent = 100
  enable_ecs_managed_tags = true
  enable_execute_command = false
  force_new_deployment = false #Enable to force a new task deployment of the service. This can be used to update tasks to use a newer Docker image with same image/tag combination (e.g., myimage:latest), roll Fargate tasks onto a newer platform version, or immediately deploy ordered_placement_strategy and placement_constraints updates.
  health_check_grace_period_seconds = 45
  platform_version = "LATEST"
  propagate_tags = "TASK_DEFINITION"  #The valid values are SERVICE and TASK_DEFINITION.
  scheduling_strategy = "REPLICA"
  wait_for_steady_state = false #if true, Terraform will wait for the service to reach a steady state

  load_balancer {
    target_group_arn = aws_lb_target_group.www-cryptostacker-io-tf.arn
    #target_group_arn = "arn:aws:elasticloadbalancing:us-east-2:370458797273:targetgroup/cryptostacker-io-con/79930638443cdb8e"
    container_name = "csr-flask-web-app-tf"
    container_port = 8000
  }

  #https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-configure-network.html
  network_configuration {
    subnets = module.vpc.public_subnets
    security_groups = [aws_security_group.allow_ecs_sg-tf.id] #ids or names?
    assign_public_ip = true
  }

  lifecycle {
      #ignore_changes = [desired_count, task_definition]
      ignore_changes = all
  }

  deployment_circuit_breaker {
    enable   = false
    rollback = false
  }

  capacity_provider_strategy {
    base = "1"
    capacity_provider = "FARGATE"
    weight = "1"
  }

  deployment_controller {
    type = "ECS"
  }
}

#autoscaling
#https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/appautoscaling_policy
resource "aws_appautoscaling_target" "csr-flask-web-app_ecs-target-tf" {
  max_capacity       = 100
  min_capacity       = 10
  resource_id        = "service/${aws_ecs_cluster.csr-flask-web-app-ecs-cluster-tf.name}/${aws_ecs_service.csr-flask-web-app-service-tf.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "csr-flask-web-app_ecs_policy-tf" {
  name               = "csr-flask-web-app_ecs_policy-tf:${aws_appautoscaling_target.csr-flask-web-app_ecs-target-tf.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.csr-flask-web-app_ecs-target-tf.resource_id
  scalable_dimension = aws_appautoscaling_target.csr-flask-web-app_ecs-target-tf.scalable_dimension
  service_namespace  = aws_appautoscaling_target.csr-flask-web-app_ecs-target-tf.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label = "${aws_lb.www-cryptostacker-io-alb-tf.arn_suffix}/${aws_lb_target_group.www-cryptostacker-io-tf.arn_suffix}"

    }
    target_value = 50
  }
}

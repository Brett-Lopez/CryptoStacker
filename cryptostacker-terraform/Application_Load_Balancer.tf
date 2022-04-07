#######################################
## www-cryptostacker-io block begins ##
#######################################

#https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb
resource "aws_lb" "www-cryptostacker-io-alb-tf" {
  name                       = "www-cryptostacker-io-alb-tf"
  internal                   = false
  load_balancer_type         = "application"
  security_groups            = [aws_security_group.allow_all_for_alb-tf.id]
  subnets                    = module.vpc.public_subnets
  drop_invalid_header_fields = true
  enable_deletion_protection = true
  idle_timeout               = "60"
  enable_http2               = true
  ip_address_type            = "ipv4"

}

#define data resource for certificate so the ARN output can be called by the ALB resources
data "aws_acm_certificate" "www-cryptostacker-io" {
  domain   = "www.cryptostacker.io"
}


resource "aws_lb_listener" "www-cryptostacker-io-alb-tf" {
  load_balancer_arn = aws_lb.www-cryptostacker-io-alb-tf.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-FS-1-2-2019-08"
  certificate_arn   = data.aws_acm_certificate.www-cryptostacker-io.arn #todo figure out below error;

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.www-cryptostacker-io-tf.arn
  }
}

resource "aws_lb_listener_certificate" "www-cryptostacker-io-alb-tf" {
  listener_arn      = aws_lb_listener.www-cryptostacker-io-alb-tf.arn
  certificate_arn   = data.aws_acm_certificate.www-cryptostacker-io.arn
}

#port 80 redirect to 443
resource "aws_lb_listener" "www-cryptostacker-io-alb_80-tf" {
  load_balancer_arn = aws_lb.www-cryptostacker-io-alb-tf.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

#TARGET GROUP
#https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb_target_group
resource "aws_lb_target_group" "www-cryptostacker-io-tf" {
  name             = "www-cryptostacker-io-tf"
  port             = 8000
  protocol         = "HTTPS"
  target_type      = "ip"
  protocol_version = "HTTP1"
  #protocol_version = "HTTP2" #breaking change - gunicorn doesn't currently support HTTP/2. There's a tracking issue for it. You can still use nginx with docker swarm.
  vpc_id           = module.vpc.vpc_id
  deregistration_delay = "60" #Amount time for Elastic Load Balancing to wait before changing the state of a deregistering target from draining to unused. The range is 0-3600 seconds. The default value is 300 seconds.
  load_balancing_algorithm_type = "least_outstanding_requests" #Determines how the load balancer selects targets when routing requests. Only applicable for Application Load Balancer Target Groups. The value is round_robin or least_outstanding_requests

  health_check {
    enabled             = true
    port                = "traffic-port"
    protocol            = "HTTPS"
    healthy_threshold   = "5" #The number of consecutive health checks successes required before considering an unhealthy target healthy.
    unhealthy_threshold = "2" #The number of consecutive health check failures required before considering a target unhealthy.
    timeout             = "5" #The amount of time, in seconds, during which no response means a failed health check.
    interval            = "30" #The approximate amount of time between health checks of an individual target
    matcher             = "200" #Success codes - The HTTP codes to use when checking for a successful response from a target. You can specify multiple values (for example, "200,202") or a range of values (for example, "200-299").
    path                = "/"
  }

}

#######################################
# www-cryptostacker-io block ends
#######################################

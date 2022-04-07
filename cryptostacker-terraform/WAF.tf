#https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/wafv2_web_acl

resource "aws_wafv2_web_acl" "CSR-WEB-APP-ALB-TF" {
  name        = "CSR-WEB-APP-ALB-TF"
  description = "Managed rule for the CSR flask web app"
  scope       = "REGIONAL"
  visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "rule-metric-CSR-WEB-APP-ALB-TF"
      sampled_requests_enabled   = true
  }
  default_action {
      allow {}
  }

#ip rules - bypass waf 
  rule {
    name     = "bypass_waf_by_ip-tf"
    priority = 0

    action {
      allow {}
    }

    statement {
      #IPSetReferenceStatement
      ip_set_reference_statement {
        arn = aws_wafv2_ip_set.Allow_list_ips_bypass_waf_rules_tf.arn
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "bypass_waf_by_ip-tf"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "block_big_body-tf"
    priority = 1

    action {
      block {}
    }

    statement {
        size_constraint_statement {
            field_to_match {
                body {}
                }
            comparison_operator = "GT"
            size                = "2000"
            #size                = "8192"
            text_transformation {
                type     = "NONE"
                priority = 0
            }
        }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "block_big_body-metric-tf"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "block_big_query_string-tf"
    priority = 2

    action {
      block {}
    }

    statement {
        size_constraint_statement {
            field_to_match {
                query_string {}
                }
            comparison_operator = "GT"
            size                = "2000"
            #size                = "8192"
            text_transformation {
                type     = "NONE"
                priority = 0
            }
        }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "block_big_body-metric-tf"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "block_big_all_query_arguments-tf"
    priority = 3

    action {
      block {}
    }

    statement {
        size_constraint_statement {
            field_to_match {
                all_query_arguments {}
                }
            comparison_operator = "GT"
            size                = "8192"
            text_transformation {
                type     = "NONE"
                priority = 0
            }
        }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "block_big_body-metric-tf"
      sampled_requests_enabled   = true
    }
  }

  rule {
  name     = "rate-limit-all-traffic-by-ip-tf"
  priority = 5
  action {
    block {}
    }
  statement {
      rate_based_statement {
      limit              = 100
      aggregate_key_type = "IP"
    }
  }
  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "rate-limit-all-traffic-by-ip-metric-tf"
    sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWS-AWSManagedRulesBotControlRuleSet"
    priority = 6

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesBotControlRuleSet"
        vendor_name = "AWS"

        #excluded_rule {
        #  name = "CategorySeo" #Allow listing Google and duckduckgo IP addresses instead
        #}

      }
    }
    override_action {
      none {}
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesBotControlRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWS-AWSManagedRulesAmazonIpReputationList"
    priority = 7

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAmazonIpReputationList"
        vendor_name = "AWS"
      }
    }
    override_action {
      none {}
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesAmazonIpReputationList"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWS-AWSManagedRulesAnonymousIpList"
    priority = 8

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAnonymousIpList"
        vendor_name = "AWS"
      }
    }
    override_action {
      none {}
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesAnonymousIpList"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWS-AWSManagedRulesCommonRuleSet"
    priority = 9

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }
    override_action {
      none {}
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesCommonRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWS-AWSManagedRulesKnownBadInputsRuleSet"
    priority = 10

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }
    override_action {
      none {}
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesKnownBadInputsRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWS-AWSManagedRulesLinuxRuleSet"
    priority = 11

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesLinuxRuleSet"
        vendor_name = "AWS"
      }
    }
    override_action {
      none {}
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesLinuxRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWS-AWSManagedRulesSQLiRuleSet"
    priority = 12

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }
    override_action {
      none {}
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesSQLiRuleSet"
      sampled_requests_enabled   = true
    }
  }

#block /metrics
  rule {
    name     = "block_metrics_portal-tf"
    priority = 13

    action {
      block {}
    }

    statement {
        byte_match_statement {
           field_to_match {
                uri_path {}
           }
          positional_constraint = "CONTAINS"
          search_string = "/metrics"
          text_transformation {
              type = "LOWERCASE"
              priority = 0
            }
        }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "block_metrics_portal-metric-tf"
      sampled_requests_enabled   = true
    }
  }

#block /admin
  rule {
    name     = "block_admin_portal-tf"
    priority = 14

    action {
      block {}
    }

    statement {
        byte_match_statement {
           field_to_match {
                uri_path {}
           }
          positional_constraint = "CONTAINS"
          search_string = "/admin"
          text_transformation {
              type = "LOWERCASE"
              priority = 0
            }
        }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "block_admin_portal-metric-tf"
      sampled_requests_enabled   = true
    }
  }


#ipv4 allow rule
  rule {
    name     = "allow_ipv4-tf"
    priority = 15

    action {
      allow {}
    }

    statement {
      #IPSetReferenceStatement
      ip_set_reference_statement {
        arn = aws_wafv2_ip_set.Allow_list_ips-tf.arn
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "allow_ipv4-metric-tf"
      sampled_requests_enabled   = true
    }
  }

#ipv6 allow rule
  rule {
    name     = "allow_ipv6-tf"
    priority = 16

    action {
      allow {}
    }

    statement {
      #IPSetReferenceStatement
      ip_set_reference_statement {
        arn = aws_wafv2_ip_set.Allow_list_ipsv6-tf.arn
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "allow_ipv6-metric-tf"
      sampled_requests_enabled   = true
    }
  }

}

resource "aws_wafv2_web_acl_association" "CSR-WEB-APP-ALB-TF" {
  resource_arn = aws_lb.www-cryptostacker-io-alb-tf.arn
  web_acl_arn  = aws_wafv2_web_acl.CSR-WEB-APP-ALB-TF.arn
}

resource "aws_wafv2_ip_set" "Allow_list_ips-tf" {
  name               = "Allow_list_ips-tf"
  scope              = "REGIONAL"
  ip_address_version = "IPV4"
  addresses          = []
}

resource "aws_wafv2_ip_set" "Allow_list_ipsv6-tf" {
  name               = "Allow_list_ipsv6-tf"
  scope              = "REGIONAL"
  ip_address_version = "IPV6"
  addresses          = []
}

#set search engine IPs here
#https://help.duckduckgo.com/duckduckgo-help-pages/results/duckduckbot/
#https://developers.google.com/search/docs/advanced/crawling/verifying-googlebot
#https://developers.google.com/search/apis/ipranges/googlebot.json
resource "aws_wafv2_ip_set" "Allow_list_ips_bypass_waf_rules_tf" {
  name               = "Allow_list_ips_bypass_waf_rules_tf"
  scope              = "REGIONAL"
  ip_address_version = "IPV4"
  addresses          = [] 
}


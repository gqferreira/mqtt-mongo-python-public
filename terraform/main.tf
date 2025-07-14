# ---------------------------------------------------------------

resource "aws_key_pair" "deployer" {
  key_name   = "key_ec2-${terraform.workspace}"
  public_key = file("${path.module}/keys/key_ec2_${terraform.workspace}.pub")
}

# ---------------------------------------------------------------

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "vpc-${terraform.workspace}"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "sa-east-1a"

  tags = {
    Name = "public-subnet-${terraform.workspace}"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "igw-${terraform.workspace}"
  }
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "public-rt-${terraform.workspace}"
  }
}

resource "aws_route_table_association" "public_rt_assoc" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_security_group" "allow_ports" {
  name        = "allow-ports-${terraform.workspace}"
  description = "Allow inbound traffic"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "MONGODB"
    from_port   = 27018
    to_port     = 27018
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "API"
    from_port   = 3001
    to_port     = 3001
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ---------------------------------------------------------------

resource "aws_iam_role" "cloudwatch_agent_ec2_role" {
  name = "ec2-cloudwatch-agent-role-telemetry-${terraform.workspace}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "ec2.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "cloudwatch_agent_policy" {
  name = "CloudWatchAgentPolicyTelemetry-${terraform.workspace}"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "cloudwatch:PutMetricData",
          "cloudwatch:ListMetrics",
          "ec2:DescribeTags",
          "logs:PutLogEvents",
          "logs:CreateLogStream",
          "logs:DescribeLogStreams",
          "logs:DescribeLogGroups",
          "logs:CreateLogGroup"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_cloudwatch_policy" {
  role       = aws_iam_role.cloudwatch_agent_ec2_role.name
  policy_arn = aws_iam_policy.cloudwatch_agent_policy.arn
}

resource "aws_iam_instance_profile" "cloudwatch_agent_profile" {
  name = "cloudwatch-agent-instance-profile-telemetry-${terraform.workspace}"
  role = aws_iam_role.cloudwatch_agent_ec2_role.name
}

resource "aws_cloudwatch_metric_alarm" "cpu_alert" {
  alarm_name          = "CPU_ALERT-${terraform.workspace}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Average"
  threshold           = 10
  alarm_description   = "CPU usage exceeded 10%"
  treat_missing_data  = "notBreaching"
  actions_enabled     = true
  alarm_actions       = [aws_sns_topic.alert_topic.arn]
  dimensions = {
    InstanceId = aws_instance.app_server.id
  }

  tags = {
    Name = "HighCPUAlarm-${terraform.workspace}"
  }
}

resource "aws_cloudwatch_dashboard" "ec2_metrics" {
  dashboard_name = "Dashboard-telemetry-${terraform.workspace}"
  dashboard_body = jsonencode({
    widgets = [
      {
        type  = "metric",
        x     = 10,
        y     = 0,
        width = 10,
        height = 12,
        properties = {
          title  = "CPU Usage",
          view   = "gauge",
          region = "sa-east-1",
          period = 60,
          stat   = "Average",
          metrics = [
            ["CWAgent", "cpu_usage_system", "cpu", "cpu-total", "InstanceId", aws_instance.app_server.id, { "stat":"Average" }]
          ],
          yAxis = {
            left = { min = 0, max = 100 }
          },
          annotations = {
            horizontal = [
              { value = 10, fill = "above", color = "#8888FF", label = "Normal" },
              { value = 80, fill = "above", color = "#FF9900", label = "Warning" },
              { value = 90, fill = "above", color = "#D62728", label = "Critical" }
            ]
          }
        }
      },
      {
        type = "metric",
        x = 0,
        y = 0,
        width = 10,
        height = 6,
        properties = {
          title = "CPU Usage",
          metrics = [
            ["CWAgent", "cpu_usage_user", "cpu", "cpu-total", "InstanceId", aws_instance.app_server.id, { "stat": "Average" }],
            ["CWAgent", "cpu_usage_system", "cpu", "cpu-total", "InstanceId", aws_instance.app_server.id, { "stat": "Average" }]
          ],
          region = "sa-east-1",
          period = 60
        }
      },
      {
        type = "metric",
        x = 0,
        y = 6,
        width = 10,
        height = 6,
        properties = {
          title = "Memory Usage",
          metrics = [
            ["CWAgent", "mem_used_percent", "InstanceId", aws_instance.app_server.id, { "stat": "Average" }]
          ],
          region = "sa-east-1",
          period = 60
        }
      },
      {
        type = "alarm",
        x    = 20,
        y    = 0,
        width  = 4,
        height = 3,
        properties = {
            title = "High CPU Alarm",
          alarms = [
            aws_cloudwatch_metric_alarm.cpu_alert.arn
          ]
        }
      }
    ]
  })
}

# ---------------------------------------------------------------

resource "aws_iam_role" "lambda_exec" {
  name = "lambda_sns_to_slack_role-${terraform.workspace}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Principal = {
        Service = "lambda.amazonaws.com"
      },
      Effect = "Allow",
      Sid    = ""
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "sns_to_slack" {
  function_name = "sns-to-slack-${terraform.workspace}"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "index.handler"
  runtime       = "nodejs18.x"

  filename         = "${path.module}/lambda.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda.zip")

environment {
    variables = {
      SLACK_WEBHOOK_URL = var.slack_webhook_url
    }
  }
}

resource "aws_sns_topic" "alert_topic" {
  name = "cpu-alert-topic-${terraform.workspace}"
}

resource "aws_sns_topic_subscription" "lambda_sub" {
  topic_arn = aws_sns_topic.alert_topic.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.sns_to_slack.arn
}

resource "aws_lambda_permission" "allow_sns" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sns_to_slack.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.alert_topic.arn
}

# ---------------------------------------------------------------

resource "aws_instance" "app_server" {
  ami                         = var.ami_id
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.deployer.key_name
  vpc_security_group_ids      = [aws_security_group.allow_ports.id]
  subnet_id                   = aws_subnet.public.id
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.cloudwatch_agent_profile.name
  monitoring                  = true
  user_data                   = templatefile("${path.module}/startup.sh", {
    private_key = file("${path.module}/keys/key_github"),
    branch = var.branch,
    environment = terraform.workspace
  })
  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }
  tags = {
    Name = "ec2-terraform-${terraform.workspace}"
  }
}

resource "aws_eip_association" "eip_assoc" {
  instance_id   = aws_instance.app_server.id
  allocation_id = var.eip_id
}
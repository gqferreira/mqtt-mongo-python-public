variable "ami_id" {
  description = "AMI ID to launch EC2"
  type        = string
}

variable "instance_type" {
  description = "Type of EC2 instance"
  type        = string
}

variable "eip_id" {
  description = "Elastic IP"
  type        = string
}

variable "branch" {
  description = "Default branch"
  type        = string
}

variable "slack_webhook_url" {
  type      = string
  sensitive = true
}
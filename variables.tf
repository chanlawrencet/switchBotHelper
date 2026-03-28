variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "function_name" {
  type    = string
  default = "switchbot-door-opener"
}

variable "switchbot_token" {
  type      = string
  sensitive = true
}

variable "switchbot_secret" {
  type      = string
  sensitive = true
}

variable "link_signing_secret" {
  type      = string
  sensitive = true
}

variable "device_id" {
  type    = string
  default = "CE2A80866523"
}

variable "link_ttl_seconds" {
  type    = number
  default = 900
}
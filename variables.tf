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

variable "notification_email" {
  type    = string
  default = ""
}

variable "pushover_user_key" {
  type      = string
  default   = ""
  sensitive = true
}

variable "pushover_app_token" {
  type      = string
  default   = ""
  sensitive = true
}

variable "pushover_device" {
  type    = string
  default = ""
}

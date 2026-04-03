output "base_url" {
  description = "Public Lambda Function URL. Terraform also writes this to .env as BASE_URL."
  value       = aws_lambda_function_url.door_opener.function_url
}

output "local_helper_usage" {
  description = "Next local commands after apply."
  value       = <<-EOT
    Terraform wrote .env with BASE_URL for you.

    Next steps:
      source ./load_tfvars.sh
      python3 generate.py
  EOT
}

output "notification_email_status" {
  description = "SNS email notification setup status."
  value = (
    trimspace(var.notification_email) != ""
    ? "Unlock emails will be sent to ${trimspace(var.notification_email)} after you confirm the SNS subscription email."
    : "Unlock email notifications are disabled. Set notification_email to enable them."
  )
}

output "pushover_status" {
  description = "Pushover notification setup status."
  value = (
    nonsensitive(trimspace(var.pushover_user_key)) != "" && nonsensitive(trimspace(var.pushover_app_token)) != ""
    ? "Pushover notifications are enabled."
    : "Pushover notifications are disabled. Set pushover_user_key and pushover_app_token to enable them."
  )
}

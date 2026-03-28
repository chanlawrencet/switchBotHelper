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

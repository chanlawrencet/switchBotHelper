output "lambda_function_url" {
  value = aws_lambda_function_url.door_opener.function_url
}

output "generate_link_command" {
  value = "python3 generate_link.py"
}
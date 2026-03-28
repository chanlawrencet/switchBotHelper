# switchBotHelper

Open a SwitchBot Bot from a short-lived browser link using AWS Lambda and Terraform.

This project is designed for simple guest access:

1. Generate a signed link
2. Send it to a visitor
3. They open it in a browser
4. Lambda validates the link and sends a `press` command to your SwitchBot Bot

## Features

- Uses the SwitchBot OpenAPI
- Deploys a public AWS Lambda Function URL
- Protects access with expiring signed links
- Managed with Terraform

## How it works

The Lambda expects two query parameters:

- `exp`: Unix expiration timestamp
- `sig`: HMAC signature of `exp`

If the link is valid and not expired, Lambda calls the SwitchBot API and sends a `press` command to the configured Bot.

## Project structure

```text
.
├── main.tf
├── variables.tf
├── outputs.tf
├── terraform.tfvars.example
├── install.sh
├── generate.py
└── lambda/
    ├── app.py
    └── requirements.txt
```

## Prerequisites

- AWS account and CLI configured
- Terraform installed
- Python 3 installed
- A SwitchBot Bot connected to a hub with cloud access enabled

## Configuration

Copy the example tfvars file:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Set these values in terraform.tfvars:

```hcl
aws_region          = "us-east-1"
function_name       = "switchbot-door-opener"
switchbot_token     = "YOUR_SWITCHBOT_TOKEN"
switchbot_secret    = "YOUR_SWITCHBOT_SECRET"
link_signing_secret = "REPLACE_WITH_A_RANDOM_SECRET"
device_id           = "YOUR_DEVICE_ID"
link_ttl_seconds    = 900
```

## Install Lambda dependencies

Before deploying, run the repo install script:

```bash
./install.sh
```

That script:

- changes into `lambda/`
- creates a virtual environment at `lambda/.venv`
- upgrades `pip`
- installs `requirements.txt` into `lambda/` with `pip install -t .`
- deactivates the virtual environment when finished

## Deploy

```bash
terraform init
terraform apply
```

After apply, Terraform will output the Lambda Function URL.

## Generate a visitor link

Set these locally:

```bash
export BASE_URL="https://YOUR_FUNCTION_URL.lambda-url.us-east-1.on.aws/"
export LINK_SIGNING_SECRET="same-value-as-terraform"
```

Then run:

```bash
python3 generate.py
```

Example output:

```text
https://example.lambda-url.us-east-1.on.aws/?exp=1712345678&sig=...
```

Send that URL to your visitor.

## Security notes

This project is intentionally lightweight, but keep these in mind:

- The signed visitor link is sensitive until it expires
- Your SwitchBot token and secret must never be exposed client-side
- The device ID is not a secret by itself, but avoid publishing it unnecessarily

This setup does not prevent:

- a visitor forwarding a valid link
- repeated use before expiry
- abuse if someone gets hold of an unexpired URL

If you need stronger protection later, common upgrades are:

- one-time-use links with DynamoDB
- rate limiting
- storing secrets in AWS Secrets Manager

## Useful commands

### Preview infrastructure changes:

```bash
terraform plan
```

### Destroy infrastructure:

```bash
terraform destroy
```

### Format Terraform:

```bash
terraform fmt
```

## Notes

- This project opens a real door. Use carefully.
- Do not commit `terraform.tfvars` or secrets to Git.
- A short TTL such as 5 to 15 minutes is recommended.

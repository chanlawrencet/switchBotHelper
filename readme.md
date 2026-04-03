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
├── list_devices.py
├── load_tfvars.sh
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
notification_email  = "you@example.com"
pushover_user_key   = ""
pushover_app_token  = ""
pushover_device     = ""
```

If you do not know your `device_id` yet, you can list the devices on your SwitchBot account first.

Load the values from `terraform.tfvars` into your current shell:

```bash
source ./load_tfvars.sh
```

Then run:

```bash
python3 list_devices.py
```

The script prints both regular devices and infrared remotes as JSON. Use the `deviceId` for the Bot you want to press and copy that value into `terraform.tfvars` as `device_id`.

`load_tfvars.sh` exports these variables from `terraform.tfvars` when present:

- `AWS_REGION`
- `FUNCTION_NAME`
- `SWITCHBOT_TOKEN`
- `SWITCHBOT_SECRET`
- `LINK_SIGNING_SECRET`
- `DEVICE_ID`
- `LINK_TTL_SECONDS`

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

After apply, Terraform will:

- print the deployed `BASE_URL` more clearly in the outputs
- write a local `.env` file with `BASE_URL=...`
- optionally configure unlock email notifications if `notification_email` is set
- pass optional Pushover settings through to Lambda if `pushover_user_key` and `pushover_app_token` are set

If you set `notification_email`, AWS SNS will send a confirmation email after `terraform apply`. You must click the confirmation link in that email before notifications start arriving.

## Generate a visitor link

Load the Terraform values into your shell:

```bash
source ./load_tfvars.sh
```

Then run:

```bash
python3 generate.py
```

You can optionally override the default TTL from the command line:

```bash
python3 generate.py --hours 4
python3 generate.py --days 2
python3 generate.py --weeks 1
```

Example output:

```text
https://example.lambda-url.us-east-1.on.aws/?exp=1712345678&sig=...
```

Send that URL to your visitor.

## Notifications

If `notification_email` is configured and confirmed, Lambda sends an SNS email each time a valid door unlock link is used.

The notification includes:

- the expiry time in Eastern Time
- the configured `device_id`

If `pushover_user_key` and `pushover_app_token` are configured, Lambda also sends a direct Pushover notification on each successful unlock.

Pushover setup:

1. Put your Pushover user key into `pushover_user_key`
2. Create a Pushover application at `https://pushover.net/apps` and put its API token into `pushover_app_token`
3. Optionally set `pushover_device` if you want to target only one device
4. Run `terraform apply`

Pushover messages include:

- the configured `device_id`
- the expiry time in Eastern Time
- the expiry time in UTC
- the raw `exp` value from the link

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

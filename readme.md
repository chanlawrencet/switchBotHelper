Paste this into README.md:

# switchBotHelper

Open a SwitchBot Bot from a browser link using AWS Lambda Function URLs.

This project is meant for a simple guest-access flow:

1. You generate a short-lived signed link
2. You send that link to a visitor
3. They open it in a browser
4. AWS Lambda validates the link and sends a `press` command to your SwitchBot Bot

## What this does

- Uses the SwitchBot OpenAPI to send a `press` command to a Bot
- Hosts the endpoint on AWS Lambda
- Exposes it with a public Lambda Function URL
- Protects it with a lightweight expiring signature

This is intentionally simple. It is not meant to be highly secure.

## Project structure

```text
.
├── main.tf
├── variables.tf
├── outputs.tf
├── terraform.tfvars.example
├── generate_link.py
└── lambda/
    ├── app.py
    └── requirements.txt

Prerequisites

You should have:
	•	AWS CLI installed and logged in
	•	Terraform installed
	•	Python 3 installed
	•	A SwitchBot Bot device connected to a hub with cloud access enabled

Device used

This project is set up for this device by default:
	•	Front Door
	•	device id: CE2A80866523

You can change that in Terraform variables if needed.

How it works

The Lambda expects two query parameters:
	•	exp: unix expiration timestamp
	•	sig: HMAC signature of exp

If the link is valid and not expired, Lambda calls SwitchBot:
	•	endpoint: /v1.1/devices/{deviceId}/commands
	•	command: press

Setup

1. Create the Terraform files

Add the Terraform and Lambda files discussed earlier.

2. Create your tfvars file

cp terraform.tfvars.example terraform.tfvars

Then fill in:
	•	switchbot_token
	•	switchbot_secret
	•	link_signing_secret

Example:

aws_region          = "us-east-1"
function_name       = "switchbot-door-opener"
switchbot_token     = "YOUR_SWITCHBOT_TOKEN"
switchbot_secret    = "YOUR_SWITCHBOT_SECRET"
link_signing_secret = "replace-with-a-random-long-string"
device_id           = "CE2A80866523"
link_ttl_seconds    = 900

Lambda Python dependencies

Install the Lambda dependency into the lambda/ folder before applying Terraform:

cd lambda
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -t .
deactivate
cd ..

Deploy

terraform init
terraform apply

After apply, Terraform will output the Lambda Function URL.

Generate a visitor link

Set these environment variables locally:

export BASE_URL="https://YOUR_FUNCTION_URL.lambda-url.us-east-1.on.aws/"
export LINK_SIGNING_SECRET="same-value-as-terraform"

Then run:

python3 generate_link.py

That will print a URL you can send to a visitor.

Example flow

Generate a link:

python3 generate_link.py

Output will look like:

https://abc123.lambda-url.us-east-1.on.aws/?exp=1712345678&sig=...

Send that URL to your guest.

When they open it, the Lambda returns a simple HTML page:
	•	success: Door signal sent
	•	failure: Link invalid or expired

Local notes

You already confirmed the SwitchBot command works locally with your Bot.

You also ran into the usual macOS/Homebrew Python issue where global pip install is blocked. A virtual environment works fine:

python3 -m venv venv
source venv/bin/activate
pip install requests

Security notes

This is intentionally lightweight, but there are still a few protections:
	•	links expire
	•	signatures are required
	•	SwitchBot credentials stay server-side in Lambda

Things this does not protect against well:
	•	someone forwarding a still-valid link
	•	repeated use before expiry
	•	anyone who obtains the signed URL

If you want better protection later, the next upgrade would be:
	•	one-time-use tokens in DynamoDB
	•	rate limiting
	•	Secrets Manager instead of plain env vars

Useful commands

Check AWS auth:

aws sts get-caller-identity

Check S3 buckets:

aws s3 ls

Format Terraform:

terraform fmt

Preview changes:

terraform plan

Destroy everything:

terraform destroy

Git tips

Add a .gitignore so you do not commit secrets or build artifacts.

Suggested entries:

.terraform/
.terraform.lock.hcl
terraform.tfvars
lambda.zip
lambda/.venv/
lambda/__pycache__/
lambda/*.pyc
lambda/bin/
lambda/lib/
lambda/share/

Future improvements

Possible upgrades:
	•	one-time links
	•	button page instead of immediate open
	•	custom domain
	•	SMS sender workflow
	•	CloudWatch alerts/logging cleanup

Disclaimer

This project can open a real door. Use carefully.
Do not expose permanent public links.
Do not commit secrets to Git.

If you want, I can also write the `.gitignore` and the exact file contents next.
#!/usr/bin/env bash

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "Source this script instead of executing it:" >&2
  echo "  source ./load_tfvars.sh" >&2
  exit 1
fi

_tfvars_file="${1:-terraform.tfvars}"

if [[ ! -f "${_tfvars_file}" ]]; then
  echo "terraform vars file not found: ${_tfvars_file}" >&2
  return 1
fi

_tfvar_value() {
  local key="$1"
  local line value

  line="$(grep -E "^[[:space:]]*${key}[[:space:]]*=" "${_tfvars_file}" | tail -n 1)" || true
  if [[ -z "${line}" ]]; then
    return 1
  fi

  value="${line#*=}"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"

  if [[ "${value}" == \"*\" && "${value}" == *\" ]]; then
    value="${value#\"}"
    value="${value%\"}"
  fi

  printf '%s' "${value}"
}

export TFVARS_FILE="${_tfvars_file}"
export AWS_REGION="$(_tfvar_value aws_region || true)"
export FUNCTION_NAME="$(_tfvar_value function_name || true)"
export SWITCHBOT_TOKEN="$(_tfvar_value switchbot_token || true)"
export SWITCHBOT_SECRET="$(_tfvar_value switchbot_secret || true)"
export LINK_SIGNING_SECRET="$(_tfvar_value link_signing_secret || true)"
export DEVICE_ID="$(_tfvar_value device_id || true)"
export LINK_TTL_SECONDS="$(_tfvar_value link_ttl_seconds || true)"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source ./.env
  set +a
fi

unset -f _tfvar_value
unset _tfvars_file

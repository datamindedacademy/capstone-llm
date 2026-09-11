#!/usr/bin/env bash
# Writes AIRFLOW__API__BASE_URL into the .env file that docker compose reads.
#
# In GitHub Codespaces the Airflow UI is not on localhost:8080 but on the forwarded-port
# URL. Airflow 3 refuses to redirect to a host it does not know, which shows up as
# {"detail":"Invalid or unsafe next URL"} when you click the forwarded port link.
# Telling Airflow its public URL fixes that.
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ -z "${CODESPACE_NAME:-}" ]]; then
  # Not in a Codespace: the compose default (http://localhost:8080) is correct.
  exit 0
fi

base_url="https://${CODESPACE_NAME}-8080.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"

# Replace any previous value, keeping whatever else is in .env.
touch .env
sed -i '/^AIRFLOW__API__BASE_URL=/d' .env
echo "AIRFLOW__API__BASE_URL=${base_url}" >> .env

echo "Airflow UI will be served at ${base_url}"

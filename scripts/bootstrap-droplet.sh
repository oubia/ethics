#!/usr/bin/env bash
# One-time bootstrap for a fresh Ubuntu DigitalOcean Droplet
# - Installs Docker & Docker Compose plugin
# - Sets up UFW firewall
# - Clones the repo into /opt/ethics
# - Prepares directories and .env file

set -euo pipefail

REPO_URL=${REPO_URL:-"https://github.com/oubia/ethics.git"}
WORKDIR=${WORKDIR:-"/opt/ethics"}

if [ "$(id -u)" -ne 0 ]; then
  echo "Run this script as root (e.g., sudo)." >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y ca-certificates curl gnupg git ufw

# Install Docker Engine (latest)
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

. /etc/os-release

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  ${VERSION_CODENAME} stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Enable and start Docker
systemctl enable docker
systemctl start docker

# Basic UFW firewall
ufw allow OpenSSH || true
ufw allow 80/tcp || true
ufw allow 443/tcp || true
ufw --force enable || true

# Create workdir and clone repo if missing
mkdir -p "${WORKDIR}"
if [ ! -d "${WORKDIR}/.git" ]; then
  git clone "${REPO_URL}" "${WORKDIR}"
fi

# Ensure runtime directories exist
mkdir -p "${WORKDIR}/Vectorestor"

cd "${WORKDIR}"

# Prepare env file from example if absent
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example. Please edit and set REACT_APP_BASE_URL and Caddy email in Caddyfile." >&2
fi

echo "Bootstrap complete. Next: edit ${WORKDIR}/.env and ${WORKDIR}/Caddyfile, then run:\n  docker compose -f docker-compose.prod.yml up -d --build"
#!/bin/bash
set -e

# ─────────────────────────────────────────────────────
# Wildlife Dashboard — Setup Script
# Installs Docker, generates secrets, and starts services
# ─────────────────────────────────────────────────────

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════╗"
echo "║   🦁 Wildlife Classifier — Setup            ║"
echo "╚══════════════════════════════════════════════╝"
echo -e "${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ─── Step 1: Check/Install Docker ──────────────────
echo -e "${YELLOW}[1/4] Checking Docker...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker not found. Installing Docker Engine...${NC}"

    # Install prerequisites
    sudo apt-get update -qq
    sudo apt-get install -y -qq ca-certificates curl gnupg lsb-release

    # Add Docker GPG key
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    # Add Docker repo
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
        sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker
    sudo apt-get update -qq
    sudo apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Add user to docker group
    sudo usermod -aG docker "$USER"

    echo -e "${GREEN}✓ Docker installed!${NC}"
    echo -e "${YELLOW}  NOTE: You may need to restart your WSL session for group changes to take effect.${NC}"
    echo -e "${YELLOW}  Run: wsl --shutdown  (from PowerShell), then reopen WSL and run this script again.${NC}"
else
    echo -e "${GREEN}✓ Docker is installed: $(docker --version)${NC}"
fi

# Start Docker daemon if not running (WSL specific)
if ! sudo service docker status &> /dev/null; then
    echo -e "${YELLOW}Starting Docker daemon...${NC}"
    sudo service docker start
    sleep 2
fi

# Verify Docker is working
if ! docker info &> /dev/null; then
    echo -e "${RED}✗ Docker is not running properly. If you just installed it, restart WSL:${NC}"
    echo -e "${YELLOW}  1. Open PowerShell and run: wsl --shutdown${NC}"
    echo -e "${YELLOW}  2. Reopen WSL${NC}"
    echo -e "${YELLOW}  3. Run this script again${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker is running${NC}"

# ─── Step 2: Generate Secrets ──────────────────────
echo ""
echo -e "${YELLOW}[2/4] Generating secrets...${NC}"

if [ ! -f .env ]; then
    # Generate random secrets
    POSTGRES_PW=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))")
    DASH_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

    # Generate Supabase JWT keys using Python
    python3 -c "
import json, base64, hmac, hashlib, time

jwt_secret = '${JWT_SECRET}'

def make_jwt(payload, secret):
    header = base64.urlsafe_b64encode(json.dumps({'alg':'HS256','typ':'JWT'}).encode()).rstrip(b'=').decode()
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
    signature_input = f'{header}.{payload_b64}'
    signature = base64.urlsafe_b64encode(
        hmac.new(secret.encode(), signature_input.encode(), hashlib.sha256).digest()
    ).rstrip(b'=').decode()
    return f'{header}.{payload_b64}.{signature}'

# Token valid for 10 years
exp = int(time.time()) + (10 * 365 * 24 * 3600)

anon = make_jwt({'role': 'anon', 'iss': 'supabase', 'iat': int(time.time()), 'exp': exp}, jwt_secret)
service = make_jwt({'role': 'service_role', 'iss': 'supabase', 'iat': int(time.time()), 'exp': exp}, jwt_secret)

print(f'ANON_KEY={anon}')
print(f'SERVICE_ROLE_KEY={service}')
" > /tmp/supabase_keys.txt

    ANON_KEY=$(grep 'ANON_KEY=' /tmp/supabase_keys.txt | cut -d'=' -f2)
    SERVICE_ROLE_KEY=$(grep 'SERVICE_ROLE_KEY=' /tmp/supabase_keys.txt | cut -d'=' -f2)
    rm /tmp/supabase_keys.txt

    cat > .env << EOF
# ──────────────────────────────────────────────────────
# Wildlife Dashboard — Generated Configuration
# Generated on: $(date -Iseconds)
# ──────────────────────────────────────────────────────

# Database
POSTGRES_PASSWORD=${POSTGRES_PW}

# JWT
JWT_SECRET=${JWT_SECRET}
JWT_EXPIRY=3600

# Supabase API Keys
ANON_KEY=${ANON_KEY}
SERVICE_ROLE_KEY=${SERVICE_ROLE_KEY}

# URLs
API_EXTERNAL_URL=http://localhost:8000
SITE_URL=http://localhost:8050

# Dash App
DASH_SECRET_KEY=${DASH_SECRET}
EOF

    echo -e "${GREEN}✓ Generated .env with secure secrets${NC}"
else
    echo -e "${GREEN}✓ .env already exists, skipping generation${NC}"
fi

# ─── Step 3: Build & Start ─────────────────────────
echo ""
echo -e "${YELLOW}[3/4] Building and starting services...${NC}"
echo -e "${CYAN}  This may take a few minutes on first run (downloading images)...${NC}"

docker compose up -d --build

# ─── Step 4: Health Check ──────────────────────────
echo ""
echo -e "${YELLOW}[4/4] Waiting for services to be ready...${NC}"

# Wait for database
echo -n "  Database: "
for i in $(seq 1 30); do
    if docker compose exec -T db pg_isready -U supabase_admin &> /dev/null; then
        echo -e "${GREEN}✓ ready${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for auth
echo -n "  Auth:     "
for i in $(seq 1 30); do
    if docker compose exec -T kong curl -sf http://auth:9999/health &> /dev/null; then
        echo -e "${GREEN}✓ ready${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for dashboard
echo -n "  Dashboard: "
for i in $(seq 1 20); do
    if curl -sf http://localhost:8050 &> /dev/null; then
        echo -e "${GREEN}✓ ready${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# ─── Done ──────────────────────────────────────────
echo ""
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════╗"
echo "║   ✅ Setup Complete!                         ║"
echo "╠══════════════════════════════════════════════╣"
echo "║                                              ║"
echo "║   🌐 Dashboard:  http://localhost:8050       ║"
echo "║   🔧 Studio:     http://localhost:3000       ║"
echo "║   🔌 API:        http://localhost:8000       ║"
echo "║                                              ║"
echo "║   To stop:  docker compose down              ║"
echo "║   To start: docker compose up -d             ║"
echo "║   Logs:     docker compose logs -f dashboard ║"
echo "║                                              ║"
echo "╚══════════════════════════════════════════════╝"
echo -e "${NC}"

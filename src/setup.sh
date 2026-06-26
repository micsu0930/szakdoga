#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v docker &> /dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq ca-certificates curl gnupg lsb-release
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update -qq
    sudo apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo usermod -aG docker "$USER"
fi

if ! sudo service docker status &> /dev/null; then
    sudo service docker start
    sleep 2
fi

if ! docker info &> /dev/null; then
    exit 1
fi

if [ ! -f .env ]; then
    POSTGRES_PW=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))")
    DASH_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

    python3 -c "
import json, base64, hmac, hashlib, time
jwt_secret = '${JWT_SECRET}'
def make_jwt(payload, secret):
    header = base64.urlsafe_b64encode(json.dumps({'alg':'HS256','typ':'JWT'}).encode()).rstrip(b'=').decode()
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
    signature_input = f'{header}.{payload_b64}'
    signature = base64.urlsafe_b64encode(hmac.new(secret.encode(), signature_input.encode(), hashlib.sha256).digest()).rstrip(b'=').decode()
    return f'{header}.{payload_b64}.{signature}'
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
POSTGRES_PASSWORD=${POSTGRES_PW}
JWT_SECRET=${JWT_SECRET}
JWT_EXPIRY=3600
ANON_KEY=${ANON_KEY}
SERVICE_ROLE_KEY=${SERVICE_ROLE_KEY}
API_EXTERNAL_URL=http://localhost:8000
SITE_URL=http://localhost:8050
DASH_SECRET_KEY=${DASH_SECRET}
EOF
fi

docker compose up -d --build

for i in $(seq 1 30); do
    if docker compose exec -T db pg_isready -U supabase_admin &> /dev/null; then
        break
    fi
    sleep 2
done

for i in $(seq 1 30); do
    if docker compose exec -T kong curl -sf http://auth:9999/health &> /dev/null; then
        break
    fi
    sleep 2
done

for i in $(seq 1 20); do
    if curl -sf http://localhost:8050 &> /dev/null; then
        break
    fi
    sleep 2
done

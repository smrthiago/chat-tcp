#!/bin/bash
# Setup inicial do projeto
set -e

echo "=== Chat TCP — Setup ==="
echo ""

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale em https://python.org"
    exit 1
fi

PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python $PYTHON_VER encontrado"

# Cria e ativa ambiente virtual
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Ambiente virtual criado"
fi

source venv/bin/activate

# Instala dependências
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependências instaladas"

# Cria .env se não existir
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Arquivo .env criado a partir do .env.example"
fi

# Cria diretório de logs
mkdir -p logs
echo "✅ Diretório de logs criado"

echo ""
echo "=== Setup concluído! ==="
echo ""
echo "  Para iniciar o servidor:"
echo "    ./scripts/run_server.sh"
echo ""
echo "  Para iniciar um cliente (em outro terminal):"
echo "    ./scripts/run_client.sh"
echo ""

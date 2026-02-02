# 🤖 Cicna Evolution - Webhook WhatsApp Bot

Sistema de webhook para integração com Evolution API, permitindo receber e processar mensagens do WhatsApp em tempo real.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Endpoints da API](#endpoints-da-api)
- [Integração com Outros Projetos](#integração-com-outros-projetos)
- [Troubleshooting](#troubleshooting)

## 🎯 Sobre o Projeto

Este projeto fornece um webhook FastAPI que se integra ao Evolution API para:
- Receber mensagens do WhatsApp em tempo real
- Armazenar mensagens recebidas
- Encaminhar dados para outros serviços
- Fornecer API REST para consulta de mensagens

## ✨ Funcionalidades

- ✅ Recebimento de webhooks do Evolution API
- ✅ Processamento de mensagens de texto
- ✅ Armazenamento em memória de mensagens
- ✅ API REST para consulta de mensagens
- ✅ Encaminhamento de dados para APIs externas
- ✅ Suporte a múltiplos tipos de mensagem (texto, texto estendido)

## 📦 Requisitos

### Software Necessário

- **Python 3.10+**
- **Docker e Docker Compose** (para Evolution API)
- **Evolution API v2.x** rodando em containers

### Dependências Python

```bash
fastapi
uvicorn
httpx
python-dotenv
```

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone <seu-repositorio>
cd cicna-evolution
```

### 2. Instale as dependências

```bash
# Usando pip
pip install -r requirements.txt

# OU usando uv (mais rápido)
uv pip install -r requirements.txt
```

### 3. Suba o Evolution API com Docker

```bash
docker-compose -f docker-compose.yaml up -d
```

Verifique se os containers estão rodando:
```bash
docker ps
```

Você deve ver containers como:
- `evolution_api`
- `postgres`
- `redis`

## ⚙️ Configuração

### 1. Configure o arquivo `.env`

Certifique-se de que o arquivo `.env` contém:

```properties
# API Key do Evolution API
AUTHENTICATION_API_KEY=dale

# Configurações do Evolution API (já no docker-compose.yaml)
DATABASE_ENABLED=true
DATABASE_PROVIDER=postgresql
DATABASE_CONNECTION_URI=postgresql://postgres:PASSWORD@postgres:5432/evolution?schema=public
```

### 2. Crie uma variável de ambiente para a instância

Edite o arquivo `.env` e adicione o nome da sua instância:

```properties
# API Key do Evolution API
AUTHENTICATION_API_KEY=dale

# Nome da instância (escolha um nome único)
INSTANCE_NAME=minha_instancia
```

### 3. Atualize o main.py para usar a variável de ambiente

No arquivo `main.py`, certifique-se que está carregando a instância do `.env`:

```python
INSTANCE = os.getenv("INSTANCE_NAME", "minha_instancia")
```

### 4. Crie sua instância no Evolution API

**IMPORTANTE:** Escolha um nome único para sua instância.

```bash
# Substitua "minha_instancia" pelo nome que você escolheu
curl -X POST http://localhost:8080/instance/create \
  -H "Content-Type: application/json" \
  -H "apikey: dale" \
  -d '{
    "instanceName": "minha_instancia",
    "token": "token_opcional",
    "qrcode": true
  }'
```

A API retornará um **QR Code**. Escaneie com seu WhatsApp para conectar.

**Alternativa:** Acesse o Evolution Manager no navegador:
```
http://localhost:8080/manager
```

Lá você pode:
- Criar novas instâncias
- Ver o QR Code
- Gerenciar conexões

### 5. Descubra o IP da sua máquina

```bash
# Linux/Mac
hostname -I | awk '{print $1}'

# Ou
ip route get 1 | awk '{print $NF;exit}'
```

Anote o IP (exemplo: `192.168.1.100`)

### 6. Configure o webhook na sua instância

**IMPORTANTE:** 
- Use o IP da sua máquina (não localhost) porque o Evolution está no Docker
- Substitua `minha_instancia` pelo nome que você escolheu

```bash
curl -X POST http://localhost:8080/webhook/set/minha_instancia \
  -H "Content-Type: application/json" \
  -H "apikey: dale" \
  -d '{
    "webhook": {
      "enabled": true,
      "url": "http://SEU_IP_AQUI:8000/webhook/process",
      "webhook_by_events": false,
      "events": ["MESSAGES_UPSERT"]
    }
  }'
```

**Substitua:**
- `minha_instancia` → Nome da sua instância
- `SEU_IP_AQUI` → IP que você descobriu no passo anterior

### 7. Verifique se o webhook foi configurado

```bash
curl -X GET http://localhost:8080/webhook/find/minha_instancia \
  -H "apikey: dale"
```

## 🎮 Uso

### Inicie o servidor

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Você verá:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Teste se está funcionando

```bash
curl http://localhost:8000/
```

Deve retornar:
```json
{"mensagem": "O Bot está ONLINE! 🟢"}
```

### Envie uma mensagem de teste

Envie uma mensagem no WhatsApp para o número conectado à instância "minha_instancia". O webhook deve:
1. Receber a mensagem
2. Imprimir logs no terminal
3. Armazenar a mensagem
4. Encaminhar para API externa (se configurado)

## 🌐 Endpoints da API

### 1. Health Check

```http
GET /
```

Retorna o status do bot.

**Resposta:**
```json
{"mensagem": "O Bot está ONLINE! 🟢"}
```

### 2. Webhook (recebe do Evolution API)

```http
POST /webhook/process
POST /webhook/process/messages-upsert
```

Recebe webhooks do Evolution API com dados de mensagens.

**Body esperado:**
```json
{
  "event": "messages.upsert",
  "data": {
    "key": {
      "remoteJid": "5511999999999@s.whatsapp.net",
      "fromMe": false
    },
    "message": {
      "conversation": "Olá!"
    }
  }
}
```

### 3. Listar Mensagens

```http
GET /api/mensagens?telefone=5511999999999@s.whatsapp.net
```

Lista mensagens recebidas. Use o parâmetro `telefone` para filtrar.

**Resposta:**
```json
[
  {
    "telefone": "5511999999999@s.whatsapp.net",
    "mensagem": "Olá!",
    "timestamp": "2024-01-20T10:30:00",
    "dados_completos": {...}
  }
]
```

### 4. Limpar Mensagens

```http
DELETE /api/mensagens/limpar
```

Remove todas as mensagens armazenadas da memória.

**Resposta:**
```json
{"status": "limpo"}
```

## 🔗 Integração com Outros Projetos

### Opção 1: Webhook Push (Recomendado)

O webhook **encaminha automaticamente** as mensagens para sua API:

```python
# No main.py, linha ~104
response = await client.post(
    "http://localhost:8001/api/v1/webhook/whatsapp",
    json=webhook.data
)
```

**Configure sua API externa** para receber em `/api/v1/webhook/whatsapp`:

```python
# No seu outro projeto
@app.post("/api/v1/webhook/whatsapp")
async def receber_whatsapp(data: dict):
    telefone = data["key"]["remoteJid"]
    mensagem = data["message"].get("conversation")
    # Processar mensagem...
    return {"status": "ok"}
```

### Opção 2: Polling/Pull

**Do seu outro projeto, consulte as mensagens:**

```python
import httpx

async def buscar_mensagens():
    async with httpx.AsyncClient() as client:
        # Buscar todas
        response = await client.get("http://localhost:8000/api/mensagens")
        mensagens = response.json()
        
        # Buscar de um telefone específico
        response = await client.get(
            "http://localhost:8000/api/mensagens",
            params={"telefone": "5511999999999@s.whatsapp.net"}
        )
        return response.json()
```

### Opção 3: Fila de Mensagens (Produção)

Use Redis ou RabbitMQ para desacoplar:

```python
import redis.asyncio as redis

redis_client = redis.Redis(host='localhost', port=6379)

# Publicar no webhook
await redis_client.lpush('fila_whatsapp', json.dumps(mensagem))

# Consumir no outro projeto
while True:
    msg = await redis_client.brpop('fila_whatsapp', timeout=0)
    processar(msg)
```

## 🔧 Troubleshooting

### ❌ Webhook não recebe mensagens

**1. Verifique se o webhook está configurado:**
```bash
# Substitua "minha_instancia" pelo nome da sua instância
curl -X GET http://localhost:8080/webhook/find/minha_instancia -H "apikey: dale"
```

**2. Verifique se a instância está conectada:**
```bash
# Substitua "minha_instancia" pelo nome da sua instância
curl -X GET http://localhost:8080/instance/connectionState/minha_instancia -H "apikey: dale"
```

Deve retornar `"state": "open"`. Se retornar `"state": "close"`, escaneie o QR Code novamente.

**3. Teste a conectividade do Docker:**
```bash
docker exec -it evolution_api curl http://SEU_IP:8000/
```

**4. Verifique os logs do Evolution:**
```bash
docker logs -f evolution_api
```

### ❌ Erro "host.docker.internal not found"

Use o **IP real da sua máquina** em vez de `host.docker.internal`:

```bash
# Descubra seu IP
hostname -I | awk '{print $1}'

# Configure com o IP real (substitua "minha_instancia" pelo nome da sua)
curl -X POST http://localhost:8080/webhook/set/minha_instancia \
  -H "Content-Type: application/json" \
  -H "apikey: dale" \
  -d '{
    "webhook": {
      "enabled": true,
      "url": "http://192.168.1.100:8000/webhook/process",
      "events": ["MESSAGES_UPSERT"]
    }
  }'
```

### ❌ Erro 401 Unauthorized

A API key está incorreta. Verifique no `.env`:
```bash
grep AUTHENTICATION_API_KEY .env
```

### ❌ AUTHENTICATION_API_KEY não encontrada

O arquivo `.env` não foi carregado. Certifique-se que:
1. O arquivo `.env` existe na raiz do projeto
2. Contém a linha: `AUTHENTICATION_API_KEY=dale`
3. O servidor foi reiniciado após criar/editar o `.env`

### ❌ Mensagens não aparecem nos logs

1. Verifique se o servidor está rodando com `--host 0.0.0.0`
2. Envie uma mensagem de teste via curl (veja seção [Teste Manual](#teste-manual))
3. Verifique se não há firewall bloqueando a porta 8000

## 🧪 Teste Manual

Teste o webhook sem enviar mensagens reais:

```bash
curl -X POST http://localhost:8000/webhook/process \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "data": {
      "key": {
        "remoteJid": "5511999999999@s.whatsapp.net",
        "fromMe": false
      },
      "message": {
        "conversation": "teste"
      }
    }
  }'
```

Deve aparecer no terminal:
```
==================================================
🔔 WEBHOOK RECEBIDO!
📦 Dados: {...}
💬 Mensagem recebida: [...]
```

## 📝 Estrutura do Projeto

```
cicna-evolution/
├── main.py                 # Aplicação FastAPI principal
├── requirements.txt        # Dependências Python
├── .env                    # Variáveis de ambiente
├── docker-compose.yaml     # Evolution API + PostgreSQL + Redis
└── README.md              # Este arquivo
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 📄 Licença

Este projeto está sob a licença MIT.

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique a seção [Troubleshooting](#troubleshooting)
2. Revise os logs do Evolution API: `docker logs -f evolution_api`
3. Abra uma issue no repositório

---

**Desenvolvido com ❤️ para integração WhatsApp via Evolution API**
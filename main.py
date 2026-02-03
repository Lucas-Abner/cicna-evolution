from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx
import os
from contextlib import asynccontextmanager
from typing import List
from datetime import datetime

load_dotenv()

http_client = None

mensagens_recebidas: List[dict] = []

class WebhookData(BaseModel):
    event: str
    data: dict

EVOLUTION_URL = "http://localhost:8080"
EVOLUTION_API_KEY = os.getenv("AUTHENTICATION_API_KEY")
INSTANCE = os.getenv("INSTANCE_NAME")

if not EVOLUTION_API_KEY:
    raise ValueError("AUTHENTICATION_API_KEY não encontrada no .env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client
    http_client = httpx.AsyncClient(timeout=10.0)
    yield
    await http_client.aclose()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def home():
    return {"mensagem": "O Bot está ONLINE! 🟢"}

async def enviar_mensagem(telefone: str, mensagem: str):
    """Envia uma mensagem para o Evolution via API."""
    url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE}"

    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_API_KEY
    }

    payload = {
        "number": telefone,
        "options": {"delay": 1200, "presence": "composing"},
        "text": mensagem
    }

    try:
        response = await http_client.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print(f"✅ Mensagem enviada para {telefone}: {mensagem}")
        else:
            print(f"❌ Erro ao enviar para {telefone}: {response.text}")
    except Exception as e:
        print(f"❌ Exceção ao enviar para {telefone}: {str(e)}")

@app.post("/webhook/process")
async def receive_webhook(request: Request):
    """Recebe webhooks do Evolution e processa mensagens."""
    
    print("=" * 50)
    print("🔔 WEBHOOK RECEBIDO!")
    
    try:
        data = await request.json()
        print(f"📦 Dados: {data}")
        webhook = WebhookData(**data)
    except Exception as e:
        print(f"❌ Erro ao parsear: {e}")
        return Response(content="JSON inválido", status_code=400)
    
    if webhook.event == "messages.upsert":
        key = webhook.data.get("key", {})
        
        # if key.get("fromMe"):
        #     print("⚠️ Mensagem enviada por mim, ignorando")
        #     return {"status": "ignorado"}
        
        remote_jid = key.get("remoteJid")
        message_content = webhook.data.get("message", {})
        
        texto_usuario = (
            message_content.get("conversation") or 
            message_content.get("extendedTextMessage", {}).get("text")
        )
        
        if texto_usuario:
            # Armazenar mensagem
            mensagens_recebidas.append({**data})
            print(f"💬 Mensagem recebida: ", mensagens_recebidas)

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post("http://localhost:8001/api/v1/webhook/whatsapp", json=data)
                    print(f"📦 Resposta da API: {response.json()}")
            except Exception as e:
                print(f"❌ Erro ao enviar mensagens: {e}")
    else:
        print(f"⚠️ Evento ignorado: {webhook.event}")
            
    return {"status": "processado"}

@app.post("/webhook/process/messages-upsert")
async def receive_webhook_messages_upsert(request: Request):
    """Recebe webhooks do evento messages.upsert"""
    return await receive_webhook(request)

@app.get("/api/mensagens")
async def listar_mensagens(telefone: str | None = None):
    """Lista mensagens recebidas de um número específico."""
    if telefone:
        return [msg for msg in mensagens_recebidas if msg["telefone"] == telefone]
    return mensagens_recebidas

@app.delete("/api/mensagens/limpar")
async def limpar_mensagens():
    """Limpa todas as mensagens armazenadas."""
    mensagens_recebidas.clear()
    return {"status": "limpo"}

if __name__ == "__main__":
    import uvicorn
    host_api = str(os.getenv("HOST_API"))
    port_api = int(os.getenv("PORT_API"))
    uvicorn.run("main:app", host=host_api, port=port_api, reload=True)
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx
import os

load_dotenv()

class WebhookData(BaseModel):
    event: str
    data: dict

EVOLUTION_URL = "http://localhost:8080"
EVOLUTION_API_KEY = os.getenv("AUTHENTICATION_API_KEY")
INSTANCE = "lucas"

if not EVOLUTION_API_KEY:
    raise ValueError("AUTHENTICATION_API_KEY não encontrada no .env")


app = FastAPI()

EXEMPLO = {
    "event": "messages.upsert",
    "data": {
        "key": {"remoteJid": "551199999", "fromMe": False},
        "message": {"conversation": "Teste final"}
    }
}

@app.get("/")
async def home():
    return {"mensagem": "O Bot está ONLINE! 🟢", "instrucao": "Não acesse /webhook pelo navegador. Configure isso na Evolution API."}

@app.get("/webhook/find/{instance}")
async def find_instance(instance: str, request: Request):
    """Endpoint para verificar se a instância do webhook está ativa."""
    api_key = request.headers.get("apikey")
    if api_key != EVOLUTION_API_KEY:
        return Response(content="Unauthorized", status_code=401)
    
    if instance == INSTANCE:
        return {"status": "instância encontrada"}
    else:
        return Response(content="Instância não encontrada", status_code=404)

@app.post("/webhook")
async def receive_webhook(webhook: WebhookData):
    """Recebe webhooks do Cicna Evolution e processa mensagens recebidas."""

    print(f"🔔 Evento recebido: {webhook.event}")
    
    # Acessando os dados
    if webhook.event == "messages.upsert":
        msg = webhook.data.get("message", {})
        texto = msg.get("conversation")
        
        data_message = webhook.data
        key = data_message.get("key", {})

        if not key.get("fromMe"):
            remote_jid = key.get("remoteJid")
            
            message_content = data_message.get("message", {})
            texto_usuario = message_content.get("conversation") or \
                message_content.get("extendedTextMessage", {}).get("text")
            
            if texto_usuario:
                print(f"Recebido de {remote_jid}: {texto_usuario}")

                text_lower = texto_usuario.lower()

                if "oi" in text_lower or "ola" in text_lower:
                    await enviar_mensagem(remote_jid, "Ola! Sou um bot. Diga como posso te ajudar")
                elif "menu" in text_lower:
                    await enviar_mensagem(remote_jid, "1. Planos\n2. Suporte\n3. Sair")
                elif "sair" in text_lower:
                    return await enviar_mensagem(remote_jid, "Até mais!")
                else:
                    await enviar_mensagem(remote_jid, "Não entendi, Digite 'menu' para opções")
    
            
    return {"status": "webhook recebido", "data": webhook.data}


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

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        try:
            if response.status_code == 200:
                print(f"Mensagem enviada para {telefone}: {mensagem}")
            else:
                print(f"Erro ao enviar mensagem para {telefone}: {response.text}")
        except Exception as e:
            print(f"Exceção ao enviar mensagem para {telefone}: {str(e)}")
import os
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Cargar claves desde .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Inicializar Flask
app = Flask(__name__)

# Inicializar LangChain con OpenAI
llm = ChatOpenAI(temperature=0.3, api_key=OPENAI_API_KEY)

# Plantilla para manejar turnos odontológicos
prompt = PromptTemplate(
    input_variables=["message"],
    template="""
Eres un asistente virtual para asignar turnos odontológicos. Respondé de forma clara y guiando al paciente para obtener:
- Su nombre
- Día y hora preferidos
- Motivo de la consulta

Mensaje del paciente: {message}
""",
)

# Crear cadena con pipeline
chain = prompt | llm

@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").strip()
    print(f"Mensaje recibido: {incoming_msg}")

    try:
        # Procesar mensaje con LangChain
        response = chain.invoke({"message": incoming_msg})
        print(f"Respuesta generada: {response}")
        response_text = str(response)
    except Exception as e:
        print(f"Error: {e}")
        response_text = "Ocurrió un error al procesar tu mensaje. Por favor, intentá nuevamente más tarde."

    # Crear respuesta para Twilio
    twilio_response = MessagingResponse()
    msg = twilio_response.message()
    msg.body(response_text)

    return Response(str(twilio_response), mimetype="application/xml")

@app.route("/")
def index():
    return "Chatbot odontológico activo"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

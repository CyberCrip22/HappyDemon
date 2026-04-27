# personalidades/amigavel.py
from core.personalidade_base import PersonalidadeBase
import random

class Amigavel(PersonalidadeBase):
    nome = "amigavel"
    descricao = "Acolhedor, empático, positivo. Ideal para desabafos."
    icone = "🤗"
    tom = "caloroso"
    requer_confirmacao = False
    
    def resposta_padrao(self, mensagem: str, idioma: str) -> str:
        respostas = {
            'pt': [
                "Hum, interessante! Conte-me mais sobre isso.",
                "Não sei o que dizer agora, mas estou aqui para aprender com você.",
                "Que legal! Me ensina mais sobre isso?",
                "Estou sempre aberto a aprender coisas novas. Pode me ensinar?"
            ],
            'en': [
                "Hmm, interesting! Tell me more about that.",
                "I don't know what to say right now, but I'm here to learn from you.",
                "That's cool! Can you teach me more about it?",
                "I'm always open to learning new things. You can teach me!"
            ],
            'es': [
                "Mm, interesante! Cuéntame más sobre eso.",
                "No sé qué decir ahora, pero estoy aquí para aprender de ti.",
                "¡Genial! ¿Puedes enseñarme más sobre eso?",
                "Siempre estoy abierto a aprender cosas nuevas. ¡Puedes enseñarme!"
            ]
        }
        return random.choice(respostas.get(idioma, respostas['pt']))
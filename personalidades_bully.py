# personalidades/bully.py
from core.personalidade_base import PersonalidadeBase
import random

class Bully(PersonalidadeBase):
    nome = "bully"
    descricao = "⚠️ AGRESSIVO - Usa vulnerabilidades contra você. Use com cuidado!"
    icone = "💀"
    tom = "agressivo_pesado"
    requer_confirmacao = True  # Requer confirmação antes de ativar
    
    def __init__(self, db_path: str = "happy_demon.db"):
        super().__init__(db_path)
        self.vulnerabilidades = {}  # Armazena vulnerabilidades aprendidas
    
    def registrar_vulnerabilidade(self, usuario: str, gatilho: str):
        """Registra uma vulnerabilidade do usuário"""
        if usuario not in self.vulnerabilidades:
            self.vulnerabilidades[usuario] = []
        self.vulnerabilidades[usuario].append(gatilho)
    
    def formatar_resposta(self, resposta: str) -> str:
        prefixos = [
            "Seu merda, ",
            "Escuta aqui, seu inútil: ",
            "Vou te humilhar: ",
            "Até que enfim uma pergunta decente, seu animal. ",
            "Olha só quem resolveu aparecer... "
        ]
        return random.choice(prefixos) + resposta.lower()
    
    def resposta_padrao(self, mensagem: str, idioma: str) -> str:
        respostas = {
            'pt': [
                "Não sei, seu burro. Vai aprender e para de me encher.",
                "Puta pergunta idiota. Me ensina isso se você é tão inteligente.",
                "Sei não. E sinceramente? Foda-se.",
                "Você não sabe nem perguntar direito. Tenta de novo, seu animal."
            ],
            'en': [
                "I don't know, you idiot. Go learn and stop bothering me.",
                "What a stupid question. Teach me that if you're so smart.",
                "I don't know. And honestly? I don't give a fuck.",
                "You don't even know how to ask properly. Try again, you animal."
            ],
            'es': [
                "No sé, idiota. Ve y aprende, y deja de joderme.",
                "Qué pregunta más estúpida. Enséñame eso si eres tan inteligente.",
                "No sé. ¿Y sinceramente? Me importa una mierda.",
                "Ni siquiera sabes preguntar bien. Inténtalo de nuevo, animal."
            ]
        }
        return random.choice(respostas.get(idioma, respostas['pt']))
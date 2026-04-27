# core/personalidade_manager.py
"""Gerenciador de personalidades do HappyDemon"""

import os
import json
import importlib
from typing import Dict, List, Optional

class PersonalidadeManager:
    """Gerencia o carregamento e seleção de personalidades"""
    
    def __init__(self, db_path: str = "happy_demon.db"):
        self.db_path = db_path
        self.personalidades: Dict = {}
        self.personalidade_atual = None
        self._carregar_personalidades()
    
    def _carregar_personalidades(self):
        """Carrega todas as personalidades disponíveis"""
        # Personalidades embutidas (hardcoded)
        personalidades_embutidas = [
            "amigavel", "tsundere", "yandere", "zoeira", "arrombada"
        ]
        
        for nome in personalidades_embutidas:
            try:
                modulo = importlib.import_module(f"personalidades.{nome}")
                classe = getattr(modulo, nome.capitalize())
                self.personalidades[nome] = classe(self.db_path)
            except Exception as e:
                print(f"Erro ao carregar personalidade '{nome}': {e}")
        
        # Carrega personalidades custom de arquivos JSON
        self._carregar_custom_personalidades()
    
    def _carregar_custom_personalidades(self):
        """Carrega personalidades definidas em arquivos JSON"""
        custom_dir = os.path.join(os.path.dirname(__file__), '..', 'custom')
        if not os.path.exists(custom_dir):
            return
        
        for arquivo in os.listdir(custom_dir):
            if arquivo.endswith('.json'):
                caminho = os.path.join(custom_dir, arquivo)
                with open(caminho, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Cria personalidade custom baseada no JSON
                from .personalidade_base import PersonalidadeBase
                
                class PersonalidadeCustom(PersonalidadeBase):
                    nome = config.get('nome', 'custom')
                    descricao = config.get('descricao', 'Personalidade customizada')
                    icone = config.get('icone', '🤖')
                    tom = config.get('tom', 'neutro')
                    
                    def __init__(self, db_path):
                        super().__init__(db_path)
                        self.config = config
                        self.prefixos = config.get('formatacao', {}).get('prefixos', [])
                        self.sufixos = config.get('formatacao', {}).get('sufixos', [])
                        self.respostas_padrao = config.get('respostas_padrao', {})
                    
                    def resposta_padrao(self, mensagem: str, idioma: str) -> str:
                        return self.respostas_padrao.get(idioma, "Não sei o que dizer.")
                    
                    def formatar_resposta(self, resposta: str) -> str:
                        import random
                        resultado = resposta
                        if self.prefixos:
                            resultado = random.choice(self.prefixos) + resultado
                        if self.sufixos:
                            resultado += random.choice(self.sufixos)
                        return resultado
                
                self.personalidades[config.get('nome', 'custom')] = PersonalidadeCustom(self.db_path)
    
    def listar_personalidades(self) -> List[Dict]:
        """Retorna lista de personalidades disponíveis com metadados"""
        return [
            {
                'nome': p.nome,
                'descricao': p.descricao,
                'icone': p.icone,
                'tom': p.tom,
                'requer_confirmacao': p.requer_confirmacao
            }
            for p in self.personalidades.values()
        ]
    
    def selecionar_personalidade(self, nome: str) -> bool:
        """Seleciona uma personalidade pelo nome"""
        if nome in self.personalidades:
            self.personalidade_atual = self.personalidades[nome]
            return True
        return False
    
    def obter_personalidade_atual(self):
        """Retorna a personalidade atual"""
        if self.personalidade_atual is None:
            # Carrega personalidade padrão
            self.selecionar_personalidade('amigavel')
        return self.personalidade_atual
    
    def processar(self, mensagem: str, idioma: str) -> str:
        """Processa mensagem com a personalidade atual"""
        bot = self.obter_personalidade_atual()
        
        # Busca resposta no banco
        resposta = bot.buscar_resposta(mensagem, idioma)
        
        if resposta:
            return bot.formatar_resposta(resposta)
        
        # Se não sabe, retorna resposta padrão
        return bot.resposta_padrao(mensagem, idioma)
    
    def aprender(self, pergunta: str, resposta: str, idioma: str):
        """Ensina nova resposta para a personalidade atual"""
        bot = self.obter_personalidade_atual()
        bot.aprender(pergunta, resposta, idioma)
# core/personalidade_base.py
"""Classe base para todas as personalidades do HappyDemon"""

from abc import ABC, abstractmethod
import random
import sqlite3
from typing import Optional

class PersonalidadeBase(ABC):
    """Base que toda personalidade deve implementar"""
    
    nome = "base"
    descricao = "Personalidade padrão do HappyDemon"
    icone = "😈"
    tom = "neutro"
    requer_confirmacao = False  # True para personalidades agressivas (bully)
    
    def __init__(self, db_path: str = "happy_demon.db"):
        self.db_path = db_path
        self.conexao = None
        self.cursor = None
    
    def conectar(self):
        """Conecta ao banco de dados"""
        self.conexao = sqlite3.connect(self.db_path)
        self.cursor = self.conexao.cursor()
    
    def desconectar(self):
        """Desconecta do banco"""
        if self.conexao:
            self.conexao.close()
    
    def _criar_tabelas(self):
        """Cria as tabelas necessárias se não existirem"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS conhecimento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pergunta TEXT NOT NULL,
                resposta TEXT NOT NULL,
                idioma TEXT DEFAULT 'pt',
                personalidade TEXT DEFAULT 'padrao',
                vezes_usada INTEGER DEFAULT 0,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conexao.commit()
    
    def buscar_resposta(self, mensagem: str, idioma: str) -> Optional[str]:
        """Busca uma resposta no banco de dados para esta personalidade"""
        mensagem_lower = mensagem.lower().strip()
        self.conectar()
        self._criar_tabelas()
        
        self.cursor.execute("""
            SELECT resposta FROM conhecimento 
            WHERE pergunta = ? AND idioma = ? AND personalidade = ?
            ORDER BY RANDOM() LIMIT 1
        """, (mensagem_lower, idioma, self.nome))
        
        resultado = self.cursor.fetchone()
        self.desconectar()
        
        if resultado:
            return resultado[0]
        return None
    
    def aprender(self, pergunta: str, resposta: str, idioma: str):
        """Aprende uma nova resposta para esta personalidade"""
        pergunta_lower = pergunta.lower().strip()
        resposta_lower = resposta.lower().strip()
        
        self.conectar()
        self._criar_tabelas()
        
        # Verifica se já existe
        self.cursor.execute("""
            SELECT id FROM conhecimento 
            WHERE pergunta = ? AND resposta = ? AND idioma = ? AND personalidade = ?
        """, (pergunta_lower, resposta_lower, idioma, self.nome))
        
        if self.cursor.fetchone() is None:
            self.cursor.execute("""
                INSERT INTO conhecimento (pergunta, resposta, idioma, personalidade)
                VALUES (?, ?, ?, ?)
            """, (pergunta_lower, resposta_lower, idioma, self.nome))
            self.conexao.commit()
        
        self.desconectar()
    
    def formatar_resposta(self, resposta: str) -> str:
        """Formata a resposta com o estilo da personalidade"""
        return resposta
    
    @abstractmethod
    def resposta_padrao(self, mensagem: str, idioma: str) -> str:
        """Resposta quando não sabe o que dizer"""
        pass
    
    def __del__(self):
        self.desconectar()
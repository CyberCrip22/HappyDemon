# backend/happydemon_core.py
import sqlite3
import json
import random
import os

class HappyDemonCore:
    def __init__(self, db_path='happy_demon.db'):
        self.db_path = db_path
        self.blacklist = {
            'pt': ["suicidio", "morte", "morrer", "matar", "assassin", "nazista", "racista", "negr", "macaco", "estupro", "crianca", "pedofil", "trafic", "sequest", "bomba"],
            'en': ["suicide", "death", "die", "kill", "murder", "nazi", "racist", "nigga", "monkey", "rape", "child", "pedophile", "traffick", "kidnap", "bomb"],
            'es': ["suicidio", "muerte", "morir", "matar", "asesin", "nazi", "racista", "negro", "mono", "violacion", "niño", "pedofilo", "trafica", "secuestro", "bomba"]
        }
        self._migrar_banco()
        self.inicializar_banco()
    
    def _migrar_banco(self):
        """Adiciona coluna de personalidade se não existir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(conhecimento)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'personalidade' not in colunas:
            cursor.execute("ALTER TABLE conhecimento ADD COLUMN personalidade TEXT DEFAULT 'amigavel'")
            conn.commit()
            print("✅ Coluna 'personalidade' adicionada ao banco de dados!")
        
        conn.close()
    
    def inicializar_banco(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conhecimento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pergunta TEXT NOT NULL,
                resposta TEXT NOT NULL,
                idioma TEXT DEFAULT 'pt',
                personalidade TEXT DEFAULT 'amigavel',
                vezes_usada INTEGER DEFAULT 0,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pergunta ON conhecimento(pergunta)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_idioma ON conhecimento(idioma)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_personalidade ON conhecimento(personalidade)')
        conn.commit()
        conn.close()
        self.migrar_padroes()
    
    def migrar_padroes(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM conhecimento')
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        padroes = [
            ("oi", "Olá! Como posso te ajudar hoje?", "pt", "amigavel"),
            ("tudo bem", "Tudo ótimo! E você?", "pt", "amigavel"),
            ("qual seu nome", "Meu nome é HappyDemon! Fui criado para aprender com você!", "pt", "amigavel"),
            ("obrigado", "Por nada! Estou aqui para aprender com você!", "pt", "amigavel"),
            ("tchau", "Até mais! Continue me ensinando coisas novas!", "pt", "amigavel"),
            ("hi", "Hello! How can I help you today?", "en", "amigavel"),
            ("how are you", "I'm great! And you?", "en", "amigavel"),
            ("thanks", "You're welcome! I'm here to learn from you!", "en", "amigavel"),
            ("goodbye", "See you later! Keep teaching me new things!", "en", "amigavel"),
            ("hola", "¡Hola! ¿Cómo puedo ayudarte hoy?", "es", "amigavel"),
            ("cómo estás", "¡Genial! ¿Y tú?", "es", "amigavel"),
            ("gracias", "¡De nada! Estoy aquí para aprender de ti!", "es", "amigavel"),
            ("adiós", "¡Hasta luego! ¡Sigue enseñándome cosas nuevas!", "es", "amigavel"),
        ]
        cursor.executemany('INSERT INTO conhecimento (pergunta, resposta, idioma, personalidade) VALUES (?, ?, ?, ?)', padroes)
        conn.commit()
        conn.close()
    
    def detectar_idioma(self, texto):
        texto_lower = texto.lower()
        palavras_pt = ['como', 'está', 'tudo', 'bem', 'por', 'com', 'para', 'qual', 'oi', 'obrigado', 'tchau', 'você', 'não', 'sim']
        palavras_en = ['how', 'are', 'you', 'what', 'your', 'name', 'thanks', 'goodbye', 'hello', 'hi', 'help', 'please', 'yes', 'no']
        palavras_es = ['como', 'estás', 'todo', 'bien', 'por', 'con', 'para', 'cuál', 'hola', 'gracias', 'adiós', 'tú', 'no', 'sí']
        
        score_pt = sum(1 for p in palavras_pt if p in texto_lower)
        score_en = sum(1 for p in palavras_en if p in texto_lower)
        score_es = sum(1 for p in palavras_es if p in texto_lower)
        
        if score_pt >= score_en and score_pt >= score_es:
            return 'pt'
        elif score_en >= score_pt and score_en >= score_es:
            return 'en'
        else:
            return 'es'
    
    def similaridade_texto(self, a, b):
        a = a.lower().strip()
        b = b.lower().strip()
        if a == b:
            return 100
        
        tokens_a = set(a.split())
        tokens_b = set(b.split())
        intersecao = len(tokens_a & tokens_b)
        uniao = len(tokens_a | tokens_b)
        if uniao == 0:
            return 0
        
        jaccard = (intersecao / uniao) * 70
        if b in a or a in b:
            ordem_score = 30
        else:
            palavras_a = a.split()
            palavras_b = b.split()
            match = 0
            for i in range(min(len(palavras_a), len(palavras_b))):
                if palavras_a[i] == palavras_b[i]:
                    match += 1
                else:
                    break
            ordem_score = (match / max(len(palavras_a), len(palavras_b))) * 30
        return min(100, jaccard + ordem_score)
    
    def encontrar_resposta(self, mensagem, idioma, personalidade='amigavel'):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT pergunta FROM conhecimento WHERE idioma = ? AND personalidade = ?', (idioma, personalidade))
        perguntas = [row[0] for row in cursor.fetchall()]
        
        melhor_score = 0
        melhor_pergunta = None
        for pergunta in perguntas:
            score = self.similaridade_texto(mensagem, pergunta)
            if score > melhor_score:
                melhor_score = score
                melhor_pergunta = pergunta
        
        if melhor_pergunta and melhor_score >= 70:
            cursor.execute('SELECT resposta FROM conhecimento WHERE pergunta = ? AND idioma = ? AND personalidade = ? ORDER BY RANDOM() LIMIT 1', (melhor_pergunta, idioma, personalidade))
            resposta = cursor.fetchone()[0]
            cursor.execute('UPDATE conhecimento SET vezes_usada = vezes_usada + 1 WHERE pergunta = ? AND resposta = ? AND idioma = ? AND personalidade = ?', (melhor_pergunta, resposta, idioma, personalidade))
            conn.commit()
            conn.close()
            return {'resposta': resposta, 'score': melhor_score, 'pergunta': melhor_pergunta}
        conn.close()
        return None
    
    def aprender_resposta(self, pergunta, resposta, idioma, personalidade='amigavel'):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM conhecimento WHERE pergunta = ? AND resposta = ? AND idioma = ? AND personalidade = ?', (pergunta.lower(), resposta.lower(), idioma, personalidade))
        if cursor.fetchone() is None:
            cursor.execute('INSERT INTO conhecimento (pergunta, resposta, idioma, personalidade) VALUES (?, ?, ?, ?)', (pergunta.lower(), resposta.lower(), idioma, personalidade))
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False
    
    def blacklist_contem(self, texto, idioma):
        texto_lower = texto.lower()
        for palavra in self.blacklist.get(idioma, self.blacklist['pt']):
            if palavra in texto_lower:
                return True, palavra
        return False, None
    
    def get_estatisticas(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM conhecimento')
        total = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(DISTINCT pergunta) FROM conhecimento')
        perguntas = cursor.fetchone()[0]
        cursor.execute('SELECT idioma, COUNT(*) FROM conhecimento GROUP BY idioma')
        stats = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.execute('SELECT personalidade, COUNT(*) FROM conhecimento GROUP BY personalidade')
        personalidades = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return {'total_respostas': total, 'total_perguntas': perguntas, 'por_idioma': stats, 'por_personalidade': personalidades}
    
    def backup_json(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT pergunta, resposta, idioma, personalidade FROM conhecimento')
        dados = cursor.fetchall()
        conn.close()
        export = {}
        for pergunta, resposta, idioma, personalidade in dados:
            if personalidade not in export:
                export[personalidade] = {'pt': {}, 'en': {}, 'es': {}}
            if pergunta not in export[personalidade][idioma]:
                export[personalidade][idioma][pergunta] = []
            export[personalidade][idioma][pergunta].append(resposta)
        return export
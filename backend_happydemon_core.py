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
        self.inicializar_banco()
    
    def inicializar_banco(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conhecimento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pergunta TEXT NOT NULL,
                resposta TEXT NOT NULL,
                idioma TEXT DEFAULT 'pt',
                vezes_usada INTEGER DEFAULT 0,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pergunta ON conhecimento(pergunta)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_idioma ON conhecimento(idioma)')
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
            ("oi", "Olá! Como posso te ajudar hoje?", "pt"),
            ("tudo bem", "Tudo ótimo! E você?", "pt"),
            ("tudo bem", "Tô de boa, e tu?", "pt"),
            ("qual seu nome", "Meu nome é HappyDemon! Fui criado para aprender com você!", "pt"),
            ("obrigado", "Por nada! Estou aqui para aprender com você!", "pt"),
            ("tchau", "Até mais! Continue me ensinando coisas novas!", "pt"),
            ("hi", "Hello! How can I help you today?", "en"),
            ("how are you", "I'm great! And you?", "en"),
            ("what's your name", "My name is HappyDemon! I was created to learn from you!", "en"),
            ("thanks", "You're welcome! I'm here to learn from you!", "en"),
            ("goodbye", "See you later! Keep teaching me new things!", "en"),
            ("hola", "¡Hola! ¿Cómo puedo ayudarte hoy?", "es"),
            ("cómo estás", "¡Genial! ¿Y tú?", "es"),
            ("cómo te llamas", "Me llamo HappyDemon! ¡Fui creado para aprender de ti!", "es"),
            ("gracias", "¡De nada! Estoy aquí para aprender de ti!", "es"),
            ("adiós", "¡Hasta luego! ¡Sigue enseñándome cosas nuevas!", "es"),
        ]
        cursor.executemany('INSERT INTO conhecimento (pergunta, resposta, idioma) VALUES (?, ?, ?)', padroes)
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
    
    def encontrar_resposta(self, mensagem, idioma):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT pergunta FROM conhecimento WHERE idioma = ?', (idioma,))
        perguntas = [row[0] for row in cursor.fetchall()]
        
        melhor_score = 0
        melhor_pergunta = None
        for pergunta in perguntas:
            score = self.similaridade_texto(mensagem, pergunta)
            if score > melhor_score:
                melhor_score = score
                melhor_pergunta = pergunta
        
        if melhor_pergunta and melhor_score >= 70:
            cursor.execute('SELECT resposta FROM conhecimento WHERE pergunta = ? AND idioma = ? ORDER BY RANDOM() LIMIT 1', (melhor_pergunta, idioma))
            resposta = cursor.fetchone()[0]
            cursor.execute('UPDATE conhecimento SET vezes_usada = vezes_usada + 1 WHERE pergunta = ? AND resposta = ? AND idioma = ?', (melhor_pergunta, resposta, idioma))
            conn.commit()
            conn.close()
            return {'resposta': resposta, 'score': melhor_score, 'pergunta': melhor_pergunta}
        conn.close()
        return None
    
    def aprender_resposta(self, pergunta, resposta, idioma):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM conhecimento WHERE pergunta = ? AND resposta = ? AND idioma = ?', (pergunta.lower(), resposta.lower(), idioma))
        if cursor.fetchone() is None:
            cursor.execute('INSERT INTO conhecimento (pergunta, resposta, idioma) VALUES (?, ?, ?)', (pergunta.lower(), resposta.lower(), idioma))
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
        conn.close()
        return {'total_respostas': total, 'total_perguntas': perguntas, 'por_idioma': stats}
    
    def backup_json(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT pergunta, resposta, idioma FROM conhecimento')
        dados = cursor.fetchall()
        conn.close()
        export = {'pt': {}, 'en': {}, 'es': {}}
        for pergunta, resposta, idioma in dados:
            if pergunta not in export[idioma]:
                export[idioma][pergunta] = []
            export[idioma][pergunta].append(resposta)
        return export
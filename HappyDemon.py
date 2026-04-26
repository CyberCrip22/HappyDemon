import sys
import tkinter as tk
from tkinter import scrolledtext, messagebox
import json
import random
import datetime
import os
import sqlite3

class HappyDemon:
    def __init__(self, root):
        self.root = root
        self.root.title("😈 HappyDemon - Poliglota Demoníaco")
        self.root.geometry("700x800")
        self.root.configure(bg='#2b2b2b')
        
        # Ícone (opcional)
        try:
            self.root.iconbitmap(os.path.join(os.path.dirname(__file__), 'happydemon.ico'))
        except:
            pass
        
        # Banco de dados
        self.db_path = os.path.join(os.path.dirname(__file__), 'happy_demon.db')
        self.inicializar_banco()
        
        # Blacklist nos 3 idiomas
        self.blacklist = {
            'pt': ["suicidio", "morte", "morrer", "matar", "assassin", "nazista", "racista", "negr", "macaco", "estupro", "crianca", "pedofil", "trafic", "sequest", "bomba"],
            'en': ["suicide", "death", "die", "kill", "murder", "nazi", "racist", "nigga", "monkey", "rape", "child", "pedophile", "traffick", "kidnap", "bomb"],
            'es': ["suicidio", "muerte", "morir", "matar", "asesin", "nazi", "racista", "negro", "mono", "violacion", "niño", "pedofilo", "trafica", "secuestro", "bomba"]
        }
        
        # Estado do bot
        self.modo_aprendizado = False
        self.ultima_pergunta = None
        self.ultimo_idioma = 'pt'
        self.idioma_forcado = None
        
        # Cores dos botões
        self.cor_normal = '#2b2b2b'
        self.cor_selecionado = '#8b0000'
        self.cor_auto_normal = '#404040'
        
        self.configurar_interface()
        self.mensagem_boas_vindas()
        self.atualizar_status()
    
    # ========== BANCO DE DADOS ==========
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
    
    # ========== IDIOMA ==========
    def detectar_idioma(self, texto):
        if self.idioma_forcado:
            return self.idioma_forcado
        
        texto_lower = texto.lower()
        palavras_pt = ['como', 'está', 'tudo', 'bem', 'por', 'com', 'para', 'qual', 'oi', 'obrigado', 'tchau', 'você', 'não', 'sim']
        palavras_en = ['how', 'are', 'you', 'what', 'your', 'name', 'thanks', 'goodbye', 'hello', 'hi', 'help', 'please', 'yes', 'no']
        palavras_es = ['como', 'estás', 'todo', 'bien', 'por', 'con', 'para', 'cuál', 'hola', 'gracias', 'adiós', 'tú', 'no', 'sí']
        
        score_pt = sum(1 for p in palavras_pt if p in texto_lower)
        score_en = sum(1 for p in palavras_en if p in texto_lower)
        score_es = sum(1 for p in palavras_es if p in texto_lower)
        
        if len(texto.split()) <= 2:
            return self.ultimo_idioma
        
        if score_pt >= score_en and score_pt >= score_es:
            return 'pt'
        elif score_en >= score_pt and score_en >= score_es:
            return 'en'
        else:
            return 'es'
    
    def forcar_idioma(self, idioma):
        self.idioma_forcado = idioma
        self.ultimo_idioma = idioma
        self.atualizar_botoes_idioma(idioma)
        self.atualizar_indicador_idioma()
        mensagens = {'pt': "🌍 Idioma forçado: PORTUGUÊS", 'en': "🌍 Language forced: ENGLISH", 'es': "🌍 Idioma forzado: ESPAÑOL"}
        self.adicionar_mensagem("sistema", mensagens.get(idioma, ""))
    
    def liberar_idioma(self):
        self.idioma_forcado = None
        self.atualizar_botoes_idioma('auto')
        self.atualizar_indicador_idioma()
        self.adicionar_mensagem("sistema", "🌍 Detecção automática reativada")
    
    def atualizar_botoes_idioma(self, ativo):
        self.btn_pt.config(bg=self.cor_normal, fg='white')
        self.btn_en.config(bg=self.cor_normal, fg='white')
        self.btn_es.config(bg=self.cor_normal, fg='white')
        self.btn_auto.config(bg=self.cor_auto_normal, fg='#ffb74d')
        
        if ativo == 'pt':
            self.btn_pt.config(bg=self.cor_selecionado, fg='white')
        elif ativo == 'en':
            self.btn_en.config(bg=self.cor_selecionado, fg='white')
        elif ativo == 'es':
            self.btn_es.config(bg=self.cor_selecionado, fg='white')
        elif ativo == 'auto':
            self.btn_auto.config(bg=self.cor_selecionado, fg='white')
    
    def atualizar_indicador_idioma(self):
        if self.idioma_forcado:
            nomes = {'pt': 'Português', 'en': 'English', 'es': 'Español'}
            self.idioma_label.config(text=f"🎛️ {nomes.get(self.idioma_forcado, '')}", fg='#ffb74d')
        else:
            self.idioma_label.config(text="🌍 Automático", fg='#888888')
    
    # ========== LÓGICA DO BOT ==========
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
            return resposta, melhor_score
        conn.close()
        return None, 0
    
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
    
    # ========== INTERFACE ==========
    def configurar_interface(self):
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        titulo = tk.Label(main_frame, text="😈 HappyDemon - Poliglota Demoníaco", font=("Arial", 18, "bold"), bg='#2b2b2b', fg='#ff6b6b')
        titulo.pack(pady=(0, 10))
        
        self.chat_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Arial", 11), bg='#1e1e1e', fg='#ffffff', height=20)
        self.chat_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.chat_area.tag_config("user", foreground="#4fc3f7", font=("Arial", 11, "bold"))
        self.chat_area.tag_config("bot", foreground="#81c784", font=("Arial", 11, "bold"))
        self.chat_area.tag_config("aprendizado", foreground="#ffb74d", font=("Arial", 11, "italic"))
        self.chat_area.tag_config("sistema", foreground="#ff6b6b", font=("Arial", 10))
        self.chat_area.tag_config("hora", foreground="#888888", font=("Arial", 8))
        self.chat_area.tag_config("blacklist", foreground="#ff4444", font=("Arial", 11, "bold"))
        
        # Status e botões de idioma
        status_frame = tk.Frame(main_frame, bg='#333333', height=30)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = tk.Label(status_frame, text="", bg='#333333', fg='white', font=("Arial", 9))
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Frame dos botões
        btn_frame = tk.Frame(status_frame, bg='#333333')
        btn_frame.pack(side=tk.RIGHT, padx=10, pady=2)
        
        self.btn_pt = tk.Button(btn_frame, text="🇧🇷 PT", font=("Arial", 9, "bold"), bg=self.cor_normal, fg='white', relief=tk.FLAT, command=lambda: self.forcar_idioma('pt'), width=5)
        self.btn_pt.pack(side=tk.LEFT, padx=2)
        
        self.btn_en = tk.Button(btn_frame, text="🇺🇸 EN", font=("Arial", 9, "bold"), bg=self.cor_normal, fg='white', relief=tk.FLAT, command=lambda: self.forcar_idioma('en'), width=5)
        self.btn_en.pack(side=tk.LEFT, padx=2)
        
        self.btn_es = tk.Button(btn_frame, text="🇪🇸 ES", font=("Arial", 9, "bold"), bg=self.cor_normal, fg='white', relief=tk.FLAT, command=lambda: self.forcar_idioma('es'), width=5)
        self.btn_es.pack(side=tk.LEFT, padx=2)
        
        self.btn_auto = tk.Button(btn_frame, text="🔄 AUTO", font=("Arial", 9, "bold"), bg=self.cor_auto_normal, fg='#ffb74d', relief=tk.FLAT, command=self.liberar_idioma, width=6)
        self.btn_auto.pack(side=tk.LEFT, padx=2)
        
        self.idioma_label = tk.Label(status_frame, text="", bg='#333333', fg='#888888', font=("Arial", 9, "bold"))
        self.idioma_label.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Entrada
        entrada_frame = tk.Frame(main_frame, bg='#2b2b2b')
        entrada_frame.pack(fill=tk.X)
        
        self.entrada_var = tk.StringVar()
        self.entrada = tk.Entry(entrada_frame, textvariable=self.entrada_var, font=("Arial", 12), bg='#3b3b3b', fg='white', insertbackground='white', relief=tk.FLAT)
        self.entrada.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        self.entrada.bind("<Return>", lambda e: self.enviar_mensagem())
        self.entrada.focus()
        
        self.btn_enviar = tk.Button(entrada_frame, text="Enviar 📤", font=("Arial", 11, "bold"), bg='#8b0000', fg='white', relief=tk.FLAT, command=self.enviar_mensagem)
        self.btn_enviar.pack(side=tk.RIGHT, padx=(5, 0), ipadx=15, ipady=5)
        
        # Botões extras
        extra_frame = tk.Frame(main_frame, bg='#2b2b2b')
        extra_frame.pack(fill=tk.X, pady=(10, 0))
        
        btn_limpar = tk.Button(extra_frame, text="🧹 Limpar", font=("Arial", 9), bg='#404040', fg='white', relief=tk.FLAT, command=self.limpar_chat)
        btn_limpar.pack(side=tk.LEFT, padx=2, ipadx=5, ipady=2)
        
        btn_stats = tk.Button(extra_frame, text="📊 Stats", font=("Arial", 9), bg='#404040', fg='white', relief=tk.FLAT, command=self.mostrar_estatisticas)
        btn_stats.pack(side=tk.LEFT, padx=2, ipadx=5, ipady=2)
        
        btn_backup = tk.Button(extra_frame, text="💾 Backup", font=("Arial", 9), bg='#404040', fg='white', relief=tk.FLAT, command=self.backup_json)
        btn_backup.pack(side=tk.LEFT, padx=2, ipadx=5, ipady=2)
        
        self.atualizar_botoes_idioma('auto')
    
    def mensagem_boas_vindas(self):
        self.adicionar_mensagem("sistema", "="*50)
        self.adicionar_mensagem("sistema", "😈 HappyDemon - Poliglota Demoníaco")
        self.adicionar_mensagem("sistema", "🇧🇷 PT  🇺🇸 EN  🇪🇸 ES  — Clique nos botões para trocar o idioma")
        self.adicionar_mensagem("sistema", "🚫 Blacklist ativa | 📚 Aprendizado contínuo")
        self.adicionar_mensagem("sistema", "="*50)
    
    def adicionar_mensagem(self, tipo, msg):
        hora = datetime.datetime.now().strftime("%H:%M:%S")
        self.chat_area.insert(tk.END, f"[{hora}] ", "hora")
        if tipo == "user":
            self.chat_area.insert(tk.END, f"Você: ", "user")
            self.chat_area.insert(tk.END, f"{msg}\n\n")
        elif tipo == "bot":
            self.chat_area.insert(tk.END, f"HappyDemon: ", "bot")
            self.chat_area.insert(tk.END, f"{msg}\n\n")
        elif tipo == "aprendizado":
            self.chat_area.insert(tk.END, f"📚 ", "aprendizado")
            self.chat_area.insert(tk.END, f"{msg}\n\n")
        elif tipo == "blacklist":
            self.chat_area.insert(tk.END, f"🚫 ", "blacklist")
            self.chat_area.insert(tk.END, f"{msg}\n\n")
        else:
            self.chat_area.insert(tk.END, f"{msg}\n", "sistema")
        self.chat_area.see(tk.END)
    
    def enviar_mensagem(self):
        msg = self.entrada_var.get().strip()
        if not msg:
            return
        self.entrada_var.set("")
        
        idioma = self.detectar_idioma(msg)
        self.ultimo_idioma = idioma
        
        contem, palavra = self.blacklist_contem(msg, idioma)
        if contem:
            self.adicionar_mensagem("blacklist", f"Conteúdo bloqueado: '{palavra}'")
            return
        
        self.adicionar_mensagem("user", f"[{idioma.upper()}] {msg}")
        self.processar(msg.lower(), idioma)
    
    def processar(self, msg, idioma):
        if self.modo_aprendizado and self.ultima_pergunta:
            contem, palavra = self.blacklist_contem(msg, idioma)
            if contem:
                self.adicionar_mensagem("blacklist", f"Não posso aprender '{palavra}'")
                self.modo_aprendizado = False
                self.ultima_pergunta = None
                self.atualizar_status()
                return
            
            if self.aprender_resposta(self.ultima_pergunta, msg, idioma):
                self.adicionar_mensagem("aprendizado", f"Aprendi uma nova resposta em {idioma.upper()}!")
            else:
                self.adicionar_mensagem("aprendizado", "Essa resposta já existia")
            
            respostas = {'pt': "Valeu 😈", 'en': "Thanks 😈", 'es': "Gracias 😈"}
            self.adicionar_mensagem("bot", respostas.get(idioma, "Thanks"))
            self.modo_aprendizado = False
            self.ultima_pergunta = None
            self.atualizar_status()
            return
        
        resposta, score = self.encontrar_resposta(msg, idioma)
        if resposta:
            self.adicionar_mensagem("bot", f"{resposta}  ({score:.0f}% match)")
            return
        
        # Não sabe responder
        self.modo_aprendizado = True
        self.ultima_pergunta = msg
        self.atualizar_status()
        textos = {
            'pt': (f"Não sei o que dizer para '{msg}'...", "Me ensina a resposta!"),
            'en': (f"I don't know what to say to '{msg}'...", "Teach me the answer!"),
            'es': (f"No sé qué decir para '{msg}'...", "¡Enséñame la respuesta!")
        }
        t1, t2 = textos.get(idioma, textos['pt'])
        self.adicionar_mensagem("aprendizado", t1)
        self.adicionar_mensagem("bot", t2)
    
    def atualizar_status(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM conhecimento')
        total = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(DISTINCT pergunta) FROM conhecimento')
        perg = cursor.fetchone()[0]
        conn.close()
        self.status_label.config(text=f"📚 {perg} perguntas | {total} respostas | {'APRENDENDO' if self.modo_aprendizado else 'CONVERSA'}")
    
    def limpar_chat(self):
        self.chat_area.delete(1.0, tk.END)
        self.mensagem_boas_vindas()
    
    def mostrar_estatisticas(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT idioma, COUNT(*) FROM conhecimento GROUP BY idioma')
        stats = cursor.fetchall()
        conn.close()
        texto = "📊 Estatísticas:\n"
        for idioma, qtd in stats:
            nome = {'pt':'Português','en':'English','es':'Español'}.get(idioma, idioma)
            texto += f"   {nome}: {qtd} respostas\n"
        self.adicionar_mensagem("sistema", texto)
    
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
        
        backup_path = os.path.join(os.path.dirname(__file__), 'backup_happydemon.json')
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(export, f, indent=4, ensure_ascii=False)
        self.adicionar_mensagem("sistema", f"💾 Backup salvo: backup_happydemon.json")

# ========== PONTO DE ENTRADA PRINCIPAL ==========
if __name__ == "__main__":
    root = tk.Tk()
    app = HappyDemon(root)
    
    # Tenta esconder o terminal (só funciona quando é .exe)
    if sys.platform == 'win32' and getattr(sys, 'frozen', False):
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass
    
    root.mainloop()
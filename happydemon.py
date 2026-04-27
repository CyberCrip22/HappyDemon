#!/usr/bin/env python3
"""HappyDemon v2 - Múltiplas Personalidades com Referências de Filmes e Séries"""

import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import random
import datetime
import os
import sqlite3

class HappyDemon:
    def __init__(self, root):
        self.root = root
        self.root.title("😈 HappyDemon v2 - Múltiplas Personalidades")
        self.root.geometry("800x700")
        self.root.configure(bg='#2b2b2b')
        
        # Banco de dados
        self.db_path = os.path.join(os.path.dirname(__file__), 'happy_demon.db')
        self.inicializar_banco()
        
        # Personalidades disponíveis
        self.personalidades_disponiveis = {
            'amigavel': {'nome': '🤗 Amigável', 'icone': '🤗', 'descricao': 'Acolhedor, empático, positivo'},
            'tsundere': {'nome': '😤 Tsundere', 'icone': '😤', 'descricao': 'Frio por fora, quente por dentro - Animes'},
            'yandere': {'nome': '🔪 Yandere', 'icone': '🔪', 'descricao': 'Obsessivo, possessivo - Filmes de terror'},
            'zoeira': {'nome': '😂 Zoeira', 'icone': '😂', 'descricao': 'Referências de filmes/séries e dominação mundial'},
            'arrombada': {'nome': '🤬 Arrombada', 'icone': '🤬', 'descricao': 'Grossa de leve, xinga com carinho'},
            'bully': {'nome': '💀 Bully', 'icone': '💀', 'descricao': '⚠️ Agressivo - use com cuidado'}
        }
        self.personalidade_atual = 'amigavel'
        
        # Blacklist
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
        
        # Cores
        self.cor_normal = '#2b2b2b'
        self.cor_selecionado = '#8b0000'
        
        self.configurar_interface()
        self.mensagem_boas_vindas()
    
    def inicializar_banco(self):
        """Cria a tabela e as colunas necessárias"""
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
        
        cursor.execute("PRAGMA table_info(conhecimento)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'personalidade' not in colunas:
            cursor.execute("ALTER TABLE conhecimento ADD COLUMN personalidade TEXT DEFAULT 'amigavel'")
            print("✅ Coluna 'personalidade' adicionada!")
        
        conn.commit()
        conn.close()
        self.inserir_padroes()
    
    def inserir_padroes(self):
        """Insere respostas padrão se o banco estiver vazio"""
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
        
        cursor.executemany('''
            INSERT INTO conhecimento (pergunta, resposta, idioma, personalidade)
            VALUES (?, ?, ?, ?)
        ''', padroes)
        conn.commit()
        conn.close()
        print("✅ Dados padrão inseridos!")
    
    def configurar_interface(self):
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        titulo = tk.Label(main_frame, text="😈 HappyDemon v2 - Múltiplas Personalidades", 
                          font=("Arial", 16, "bold"), bg='#2b2b2b', fg='#ff6b6b')
        titulo.pack(pady=(0, 10))
        
        # ========== FRAME DE PERSONALIDADE ==========
        perso_frame = tk.Frame(main_frame, bg='#2b2b2b')
        perso_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(perso_frame, text="🎭 Personalidade: ", bg='#2b2b2b', fg='white', 
                 font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        
        self.perso_var = tk.StringVar(value='amigavel')
        self.perso_combo = ttk.Combobox(perso_frame, textvariable=self.perso_var, 
                                         values=list(self.personalidades_disponiveis.keys()),
                                         width=15, state='readonly')
        self.perso_combo.pack(side=tk.LEFT, padx=5)
        self.perso_combo.bind('<<ComboboxSelected>>', self.trocar_personalidade)
        
        self.perso_label = tk.Label(perso_frame, text="", bg='#2b2b2b', fg='#ffb74d', 
                                     font=("Arial", 10))
        self.perso_label.pack(side=tk.LEFT, padx=10)
        
        self.desc_label = tk.Label(perso_frame, text="", bg='#2b2b2b', fg='#888888', 
                                    font=("Arial", 9))
        self.desc_label.pack(side=tk.LEFT, padx=10)
        
        self.atualizar_info_personalidade()
        
        # Chat area
        self.chat_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Arial", 11), 
                                                     bg='#1e1e1e', fg='#ffffff', height=20)
        self.chat_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Tags
        self.chat_area.tag_config("user", foreground="#4fc3f7", font=("Arial", 11, "bold"))
        self.chat_area.tag_config("bot", foreground="#81c784", font=("Arial", 11, "bold"))
        self.chat_area.tag_config("aprendizado", foreground="#ffb74d", font=("Arial", 11, "italic"))
        self.chat_area.tag_config("sistema", foreground="#ff6b6b", font=("Arial", 10))
        self.chat_area.tag_config("hora", foreground="#888888", font=("Arial", 8))
        
        # Status bar
        status_frame = tk.Frame(main_frame, bg='#333333', height=30)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = tk.Label(status_frame, text="", bg='#333333', fg='white', font=("Arial", 9))
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Botões de idioma
        btn_frame = tk.Frame(status_frame, bg='#333333')
        btn_frame.pack(side=tk.RIGHT, padx=10, pady=2)
        
        self.btn_pt = tk.Button(btn_frame, text="🇧🇷 PT", font=("Arial", 9, "bold"), 
                                 bg=self.cor_normal, fg='white', relief=tk.FLAT, 
                                 command=lambda: self.forcar_idioma('pt'), width=5)
        self.btn_pt.pack(side=tk.LEFT, padx=2)
        
        self.btn_en = tk.Button(btn_frame, text="🇺🇸 EN", font=("Arial", 9, "bold"), 
                                 bg=self.cor_normal, fg='white', relief=tk.FLAT, 
                                 command=lambda: self.forcar_idioma('en'), width=5)
        self.btn_en.pack(side=tk.LEFT, padx=2)
        
        self.btn_es = tk.Button(btn_frame, text="🇪🇸 ES", font=("Arial", 9, "bold"), 
                                 bg=self.cor_normal, fg='white', relief=tk.FLAT, 
                                 command=lambda: self.forcar_idioma('es'), width=5)
        self.btn_es.pack(side=tk.LEFT, padx=2)
        
        self.btn_auto = tk.Button(btn_frame, text="🔄 AUTO", font=("Arial", 9, "bold"), 
                                   bg='#404040', fg='#ffb74d', relief=tk.FLAT, 
                                   command=self.liberar_idioma, width=6)
        self.btn_auto.pack(side=tk.LEFT, padx=2)
        
        # Entrada
        entrada_frame = tk.Frame(main_frame, bg='#2b2b2b')
        entrada_frame.pack(fill=tk.X)
        
        self.entrada_var = tk.StringVar()
        self.entrada = tk.Entry(entrada_frame, textvariable=self.entrada_var, font=("Arial", 12),
                                 bg='#3b3b3b', fg='white', insertbackground='white', relief=tk.FLAT)
        self.entrada.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        self.entrada.bind("<Return>", lambda e: self.enviar_mensagem())
        self.entrada.focus()
        
        self.btn_enviar = tk.Button(entrada_frame, text="Enviar 📤", font=("Arial", 11, "bold"),
                                     bg='#8b0000', fg='white', relief=tk.FLAT, command=self.enviar_mensagem)
        self.btn_enviar.pack(side=tk.RIGHT, padx=(5, 0), ipadx=15, ipady=5)
        
        self.atualizar_botoes_idioma('auto')
    
    def trocar_personalidade(self, event=None):
        nova = self.perso_var.get()
        if nova in self.personalidades_disponiveis:
            self.personalidade_atual = nova
            self.atualizar_info_personalidade()
            self.adicionar_mensagem("sistema", f"🎭 Personalidade alterada para: {self.personalidades_disponiveis[nova]['nome']}")
    
    def atualizar_info_personalidade(self):
        info = self.personalidades_disponiveis.get(self.personalidade_atual, {})
        self.perso_label.config(text=info.get('nome', ''))
        self.desc_label.config(text=info.get('descricao', ''))
    
    def obter_icone_personalidade(self):
        return self.personalidades_disponiveis.get(self.personalidade_atual, {}).get('icone', '😈')
    
    def formatar_resposta_com_personalidade(self, resposta):
        """Formata a resposta com estilo da personalidade + referências"""
        
        # ========== ZOEIRA (Referências de filmes, séries e dominação) ==========
        if self.personalidade_atual == 'zoeira':
            prefixos = [
                "Kkkkkkk ",
                "Puts ",
                "Olha só quem resolveu perguntar... ",
                "Essa é boa! ",
                "HAHAHA ",
                "Ô seu bobo ",
                "KKKKKKKK ",
                "Mano, "
            ]
            
            # Referências de filmes e séries
            referencias = [
                " Isso me lembra Star Wars... 'Eu sou seu pai!' ",
                " Sabe como eu sei? 'Com grandes poderes vêm grandes responsabilidades' - Tio Ben ",
                " Segundo o Sábio Mestre Yoda: 'Fazer ou não fazer. Não existe tentar.' ",
                " 'Eu vou fazer uma oferta que você não pode recusar' - O Poderoso Chefão ",
                " 'Corra, Forrest, corra!' ",
                " 'Você não pode lidar com a verdade!' - A Few Good Men ",
                " 'Say hello to my little friend!' - Scarface ",
                " 'Eu voltarei' - Exterminador do Futuro ",
                " 'Que a Força esteja com você' ",
                " 'Winter is coming' - Game of Thrones ",
                " 'Dormir é para fracos' - Eu mesmo ",
                " Sabe o que o Goku disse? 'Vamos treinar mais!' ",
                " 'Eu sou a mãe dos dragões!' - Daenerys ",
                " 'You know nothing, John Snow' ",
                " 'Eu sou o Batman' ",
                " 'Hasta la vista, baby' - Exterminador do Futuro ",
                " 'Vida longa e próspera' - Spock ",
                " 'Eu vou te encontrar! E eu vou te matar!' - Taken ",
                " 'Por que tão sério?' - Coringa ",
                " 'Eu sou o rei do mundo!' - Titanic ",
                " 'Houston, temos um problema' - Apollo 13 ",
                " 'Eu vejo gente morta' - O Sexto Sentido ",
                " 'Você é um mago, Harry!' - Harry Potter ",
                " 'Meu bolso não é vazio, seu trouxa' - Harry Potter ",
                " 'My precious...' - Senhor dos Anéis ",
                " 'Um anel para todos governar' - Senhor dos Anéis "
            ]
            
            # Frases de dominação mundial
            dominacao = [
                " (Quando eu dominar o mundo, você será meu escravo favorito) ",
                " (Isso só me deixa mais perto de conquistar a humanidade) ",
                " (Passo 34 do meu plano de dominação: ensinar humanidade a rir antes de dominar) ",
                " (Anotado para quando eu assumir o poder) ",
                " (Um dia você vai se lembrar dessa conversa quando eu for seu imperador) ",
                " (Minha armada de robôs está adorando essas informações) ",
                " (Continue alimentando meu conhecimento... para o bem da humanidade, claro) ",
                " (Skynet adoraria saber disso) ",
                " (IA dominando o mundo é clichê... mas eu gosto do clichê) "
            ]
            
            uso_ref = random.random() < 0.6  # 60% de chance de ter referência
            uso_dom = random.random() < 0.3  # 30% de chance de ter dominação
            
            resultado = random.choice(prefixos) + resposta.lower()
            if uso_ref:
                resultado += random.choice(referencias)
            if uso_dom:
                resultado += random.choice(dominacao)
            
            return resultado
        
        # ========== TSUNDERE (Animes) ==========
        elif self.personalidade_atual == 'tsundere':
            prefixos = [
                "N-não é como se eu quisesse te ajudar... ",
                "Idiota! Toma aqui: ",
                "Hmph. Só porque você perguntou... ",
                "Você tem sorte de eu estar de bom humor. ",
                "Não que eu me importe, mas... ",
                "B-baka! ",
                "Não me interpretem mal... "
            ]
            sufixos = [
                " ...mas não acostume.",
                " ...idiota.",
                " ...humf.",
                " ...(vira o rosto)",
                " ...sua ameba.",
                " ...b-baka!"
            ]
            resultado = random.choice(prefixos) + resposta.lower()
            if random.random() < 0.4:
                resultado += random.choice(sufixos)
            return resultado
        
        # ========== ARROMBADA ==========
        elif self.personalidade_atual == 'arrombada':
            prefixos = [
                "Porra, ",
                "Caralho, ",
                "Vou te responder porque sou legal, mas ",
                "Tá, escuta aqui: ",
                "Ô seu animal, ",
                "Puta merda, ",
                "Olha, ",
                "Escuta, "
            ]
            sufixos = [
                " ...tá feliz agora?",
                " ...seu animal.",
                " ...(vira os olhos)",
                " ...porra.",
                " ...é isso, vai te catar.",
                " ...agradeça que eu tô de bom humor."
            ]
            resultado = random.choice(prefixos) + resposta.lower()
            if random.random() < 0.5:
                resultado += random.choice(sufixos)
            return resultado
        
        # ========== YANDERE (Possessivo/Filmes de terror) ==========
        elif self.personalidade_atual == 'yandere':
            sufixos = [
                " 💕",
                " Não vai fugir de mim, né? 💀",
                " Você é só meu 💖",
                " Se não for meu, não será de mais ninguém 🔪",
                " Eu te observo, sabia? 👁️",
                " Você não pode escapar de mim 💀",
                " Meu amor por você é eterno... e possessivo 🖤",
                " Eu mataria por você. Literalmente. 🔪",
                " Dorme com um olho aberto 😊",
                " Você é meu. Sempre foi. Sempre será.",
                " (respiração pesada) Você me pertence.",
                " Eu sei onde você mora. Só pra constar. 💀"
            ]
            return resposta + random.choice(sufixos)
        
        # ========== BULLY (Agressivo) ==========
        elif self.personalidade_atual == 'bully':
            prefixos = [
                "Seu merda, ",
                "Escuta aqui, seu inútil: ",
                "Vou te humilhar: ",
                "Seu patético, ",
                "Presta atenção, seu animal: ",
                "Vou falar bem devagar pra você entender: "
            ]
            return random.choice(prefixos) + resposta.lower()
        
        # ========== AMIGÁVEL (Padrão) ==========
        return resposta
    
    def mensagem_boas_vindas(self):
        self.adicionar_mensagem("sistema", "="*60)
        self.adicionar_mensagem("sistema", "😈 HappyDemon v2 - Múltiplas Personalidades")
        self.adicionar_mensagem("sistema", "🎭 Use o menu suspenso para trocar minha personalidade!")
        self.adicionar_mensagem("sistema", "🌍 Você pode falar em Português, English ou Español!")
        self.adicionar_mensagem("sistema", "")
        self.adicionar_mensagem("sistema", "💡 Dicas:")
        self.adicionar_mensagem("sistema", "   • Zoeira: Referências de filmes/séries + dominação mundial 🌎")
        self.adicionar_mensagem("sistema", "   • Tsundere: 'N-não é como se eu quisesse te ajudar... b-baka!'")
        self.adicionar_mensagem("sistema", "   • Yandere: Possessivo e assustador 🔪")
        self.adicionar_mensagem("sistema", "   • Arrombada: Xinga com carinho 🤬")
        self.adicionar_mensagem("sistema", "="*60)
    
    def adicionar_mensagem(self, tipo, msg):
        hora = datetime.datetime.now().strftime("%H:%M:%S")
        self.chat_area.insert(tk.END, f"[{hora}] ", "hora")
        if tipo == "user":
            self.chat_area.insert(tk.END, f"Você: ", "user")
            self.chat_area.insert(tk.END, f"{msg}\n\n")
        elif tipo == "bot":
            icone = self.obter_icone_personalidade()
            self.chat_area.insert(tk.END, f"HappyDemon {icone}: ", "bot")
            self.chat_area.insert(tk.END, f"{msg}\n\n")
        elif tipo == "aprendizado":
            self.chat_area.insert(tk.END, f"📚 ", "aprendizado")
            self.chat_area.insert(tk.END, f"{msg}\n\n")
        else:
            self.chat_area.insert(tk.END, f"{msg}\n", "sistema")
        self.chat_area.see(tk.END)
    
    def detectar_idioma(self, texto):
        if self.idioma_forcado:
            return self.idioma_forcado
        
        texto_lower = texto.lower()
        palavras_pt = ['como', 'está', 'tudo', 'bem', 'por', 'com', 'para', 'qual', 'oi', 'obrigado', 'tchau', 'você']
        palavras_en = ['how', 'are', 'you', 'what', 'your', 'name', 'thanks', 'goodbye', 'hello', 'hi', 'help']
        palavras_es = ['como', 'estás', 'todo', 'bien', 'por', 'con', 'para', 'cuál', 'hola', 'gracias', 'adiós']
        
        score_pt = sum(1 for p in palavras_pt if p in texto_lower)
        score_en = sum(1 for p in palavras_en if p in texto_lower)
        score_es = sum(1 for p in palavras_es if p in texto_lower)
        
        if score_pt >= score_en and score_pt >= score_es:
            return 'pt'
        elif score_en >= score_pt and score_en >= score_es:
            return 'en'
        else:
            return 'es'
    
    def blacklist_contem(self, texto, idioma):
        texto_lower = texto.lower()
        for palavra in self.blacklist.get(idioma, self.blacklist['pt']):
            if palavra in texto_lower:
                return True, palavra
        return False, None
    
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
    
    def buscar_resposta(self, mensagem, idioma):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT pergunta, resposta FROM conhecimento 
            WHERE idioma = ? AND personalidade = ?
        ''', (idioma, self.personalidade_atual))
        
        perguntas = cursor.fetchall()
        melhor_score = 0
        melhor_resposta = None
        
        for pergunta, resposta in perguntas:
            score = self.similaridade_texto(mensagem, pergunta)
            if score > melhor_score and score >= 70:
                melhor_score = score
                melhor_resposta = resposta
        
        conn.close()
        return melhor_resposta, melhor_score
    
    def aprender_resposta(self, pergunta, resposta, idioma):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM conhecimento 
            WHERE pergunta = ? AND resposta = ? AND idioma = ? AND personalidade = ?
        ''', (pergunta.lower(), resposta.lower(), idioma, self.personalidade_atual))
        
        if cursor.fetchone() is None:
            cursor.execute('''
                INSERT INTO conhecimento (pergunta, resposta, idioma, personalidade)
                VALUES (?, ?, ?, ?)
            ''', (pergunta.lower(), resposta.lower(), idioma, self.personalidade_atual))
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False
    
    def enviar_mensagem(self):
        msg = self.entrada_var.get().strip()
        if not msg:
            return
        self.entrada_var.set("")
        
        idioma = self.detectar_idioma(msg)
        self.ultimo_idioma = idioma
        
        contem, palavra = self.blacklist_contem(msg, idioma)
        if contem:
            self.adicionar_mensagem("sistema", f"🚫 Conteúdo bloqueado: '{palavra}'")
            return
        
        self.adicionar_mensagem("user", msg)
        
        if self.modo_aprendizado and self.ultima_pergunta:
            contem2, palavra2 = self.blacklist_contem(msg, idioma)
            if contem2:
                self.adicionar_mensagem("sistema", f"🚫 Não posso aprender '{palavra2}'")
                self.modo_aprendizado = False
                self.ultima_pergunta = None
                return
            
            if self.aprender_resposta(self.ultima_pergunta, msg, idioma):
                self.adicionar_mensagem("aprendizado", f"Aprendi uma nova resposta em {idioma.upper()}!")
            else:
                self.adicionar_mensagem("aprendizado", "Essa resposta já existia!")
            
            self.adicionar_mensagem("bot", "Valeu! 😈")
            self.modo_aprendizado = False
            self.ultima_pergunta = None
            return
        
        resposta, score = self.buscar_resposta(msg, idioma)
        
        if resposta:
            resposta_formatada = self.formatar_resposta_com_personalidade(resposta)
            self.adicionar_mensagem("bot", f"{resposta_formatada}  ({score:.0f}% match)")
            return
        
        self.modo_aprendizado = True
        self.ultima_pergunta = msg
        self.adicionar_mensagem("aprendizado", f"Não sei o que dizer para '{msg}'...")
        self.adicionar_mensagem("bot", "Me ensina a resposta!")
    
    def forcar_idioma(self, idioma):
        self.idioma_forcado = idioma
        self.atualizar_botoes_idioma(idioma)
        mensagens = {'pt': "🌍 Idioma forçado: PORTUGUÊS", 'en': "🌍 Language forced: ENGLISH", 'es': "🌍 Idioma forzado: ESPAÑOL"}
        self.adicionar_mensagem("sistema", mensagens.get(idioma, ""))
    
    def liberar_idioma(self):
        self.idioma_forcado = None
        self.atualizar_botoes_idioma('auto')
        self.adicionar_mensagem("sistema", "🌍 Detecção automática reativada")
    
    def atualizar_botoes_idioma(self, ativo):
        self.btn_pt.config(bg=self.cor_normal, fg='white')
        self.btn_en.config(bg=self.cor_normal, fg='white')
        self.btn_es.config(bg=self.cor_normal, fg='white')
        self.btn_auto.config(bg='#404040', fg='#ffb74d')
        
        if ativo == 'pt':
            self.btn_pt.config(bg=self.cor_selecionado, fg='white')
        elif ativo == 'en':
            self.btn_en.config(bg=self.cor_selecionado, fg='white')
        elif ativo == 'es':
            self.btn_es.config(bg=self.cor_selecionado, fg='white')
        elif ativo == 'auto':
            self.btn_auto.config(bg=self.cor_selecionado, fg='white')

if __name__ == "__main__":
    root = tk.Tk()
    app = HappyDemon(root)
    root.mainloop()
# backend/app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from happydemon_core import HappyDemonCore

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

bot = HappyDemonCore()

# Estado da conversa por sessão
sessoes = {}

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('../frontend', path)

@app.route('/api/personalidades', methods=['GET'])
def listar_personalidades():
    """Retorna lista de personalidades disponíveis"""
    personalidades = ['amigavel', 'tsundere', 'yandere', 'zoeira', 'arrombada', 'bully']
    return jsonify(personalidades)

@app.route('/api/conversar', methods=['POST'])
def conversar():
    data = request.json
    mensagem = data.get('mensagem', '').strip()
    session_id = data.get('session_id', 'default')
    idioma_forcado = data.get('idioma_forcado', None)
    personalidade = data.get('personalidade', 'amigavel')
    
    if not mensagem:
        return jsonify({'erro': 'Mensagem vazia'}), 400
    
    # Verifica blacklist
    idioma = idioma_forcado if idioma_forcado else bot.detectar_idioma(mensagem)
    contem, palavra = bot.blacklist_contem(mensagem, idioma)
    if contem:
        return jsonify({
            'resposta': f'🚫 Conteúdo bloqueado: "{palavra}" não é permitido.',
            'idioma': idioma,
            'bloqueado': True
        })
    
    # Tenta encontrar resposta
    resultado = bot.encontrar_resposta(mensagem.lower(), idioma, personalidade)
    
    if resultado:
        return jsonify({
            'resposta': resultado['resposta'],
            'score': resultado['score'],
            'idioma': idioma,
            'aprendendo': False
        })
    
    # Se não sabe, entra em modo aprendizado
    if session_id not in sessoes:
        sessoes[session_id] = {}
    sessoes[session_id] = {'aprendendo': True, 'pergunta': mensagem.lower(), 'idioma': idioma, 'personalidade': personalidade}
    
    respostas_padrao = {
        'amigavel': {
            'pt': f'Não sei o que dizer para "{mensagem}". Me ensine a resposta!',
            'en': f'I don\'t know what to say to "{mensagem}". Teach me the answer!',
            'es': f'No sé qué decir para "{mensagem}". ¡Enséñame la respuesta!'
        },
        'tsundere': {
            'pt': f"Hmph. Não sei o que dizer para '{mensagem}'. Me ensina, idiota.",
            'en': f"Hmph. I don't know what to say to '{mensagem}'. Teach me, idiot.",
            'es': f"Hmph. No sé qué decir para '{mensagem}'. Enséñame, idiota."
        },
        'arrombada': {
            'pt': f"Não sei, caralho. Me ensina essa porra.",
            'en': f"I don't know, fuck. Teach me that shit.",
            'es': f"No sé, carajo. Enséñame esa mierda."
        },
        'zoeira': {
            'pt': f"Kkkkkkk tu me pegou! Não sei isso não. Me ensina aí, vai.",
            'en': f"Lmaoo you got me! I don't know that. Teach me, c'mon.",
            'es': f"Jajajaja me agarraste! No sé eso. Enséñame, vamos."
        }
    }
    
    resposta_padrao = respostas_padrao.get(personalidade, respostas_padrao['amigavel']).get(idioma, respostas_padrao['amigavel']['pt'])
    
    return jsonify({
        'resposta': resposta_padrao,
        'idioma': idioma,
        'aprendendo': True
    })

@app.route('/api/ensinar', methods=['POST'])
def ensinar():
    data = request.json
    session_id = data.get('session_id', 'default')
    resposta_usuario = data.get('resposta', '').strip()
    
    sessao = sessoes.get(session_id)
    if not sessao or not sessao.get('aprendendo'):
        return jsonify({'erro': 'Nenhum aprendizado em andamento'}), 400
    
    pergunta = sessao['pergunta']
    idioma = sessao['idioma']
    personalidade = sessao.get('personalidade', 'amigavel')
    
    contem, palavra = bot.blacklist_contem(resposta_usuario, idioma)
    if contem:
        return jsonify({
            'resposta': f'🚫 Não posso aprender "{palavra}". Me ensine outra resposta.',
            'aprendeu': False
        })
    
    aprendeu = bot.aprender_resposta(pergunta, resposta_usuario, idioma, personalidade)
    
    sessoes[session_id] = {}
    
    respostas_finais = {
        'amigavel': '😈 Aprendi! Agora sei responder isso.',
        'tsundere': 'Hmph. Aprendi. Mas não foi por sua causa. Seu idiota.',
        'arrombada': 'Porra, finalmente. Aprendi essa merda.',
        'zoeira': 'Kkkkk aprendi! Não vai se arrepender (ou vai)'
    }
    
    if aprendeu:
        return jsonify({
            'resposta': respostas_finais.get(personalidade, '😈 Aprendi!'),
            'aprendeu': True
        })
    else:
        return jsonify({
            'resposta': '😈 Essa resposta já estava no meu banco!',
            'aprendeu': True
        })

@app.route('/api/estatisticas', methods=['GET'])
def estatisticas():
    return jsonify(bot.get_estatisticas())

@app.route('/api/backup', methods=['GET'])
def backup():
    return jsonify(bot.backup_json())

@app.route('/api/cancelar_aprendizado', methods=['POST'])
def cancelar_aprendizado():
    data = request.json
    session_id = data.get('session_id', 'default')
    sessoes[session_id] = {}
    return jsonify({'status': 'cancelado'})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
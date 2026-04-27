#!/usr/bin/env python3
"""HappyDemon v2 - Múltiplas Personalidades"""

import sys
from personalidades.amigavel import Amigavel

def main():
    print("🐍 HappyDemon v2 - Múltiplas Personalidades")
    print("-" * 40)
    
    # Carrega personalidade padrão (por enquanto)
    bot = Amigavel()
    
    print(f"Personalidade atual: {bot.nome}")
    print(f"Descrição: {bot.descricao}")
    print("Digite 'sair' para encerrar.\n")
    
    while True:
        try:
            usuario = input("Você: ").strip()
            if usuario.lower() in ['sair', 'exit', 'quit']:
                print("HappyDemon: Até logo! 👋")
                break
            
            resposta = bot.processar(usuario)
            print(f"{bot.nome}: {resposta}\n")
            
            # Aprende com o usuário se ele quiser ensinar
            if "ensinar" in usuario.lower() or "aprender" in usuario.lower():
                print("(Modo aprendizado ativado!)")
                nova_resp = input("O que eu deveria responder? ")
                if nova_resp.strip():
                    bot.aprender(usuario, nova_resp)
                    print("Aprendizado concluído! 📚\n")
                    
        except KeyboardInterrupt:
            print("\nHappyDemon: Até mais!")
            break
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    main()
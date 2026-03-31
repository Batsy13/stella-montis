import asyncio
import os
from datetime import datetime


async def display_timer_google_finance(interval, market_data):
    """
    Dashboard para Google Finance: Limpa o terminal e exibe
    os valores reais extraídos dos atributos de dados.
    """
    while True:
        # 1. Limpa o terminal para o efeito de "App"
        os.system('cls' if os.name == 'nt' else 'clear')

        # 2. Cabeçalho com timestamp atual
        agora = datetime.now().strftime('%H:%M:%S')
        print(f"=== 📈 GOOGLE FINANCE MONITOR | {agora} ===")
        print(f"Atualizando a cada: {interval}s\n")

        if not market_data:
            print("⏳ Sincronizando com o DOM do Google Finance...")
        else:
            # 3. Tabela formatada
            # Alinhamentos: Nome (25 chars), Preço (12 chars), Moeda (8 chars)
            print(f"{'ATIVO':<25} | {'PREÇO':<12} | {'MOEDA':<8}")
            print("-" * 50)

            for name, info in market_data.items():
                price = info.get('price', 'N/A')
                currency = info.get('currency', '---')

                # Exibição dos dados capturados via data-last-price
                print(f"{name[:25]:<25} | {price:<12} | {currency:<8}")

        print("\n" + "=" * 50)

        # 4. Aguarda o intervalo solicitado
        await asyncio.sleep(interval)

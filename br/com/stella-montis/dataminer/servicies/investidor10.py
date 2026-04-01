import asyncio
import os
from datetime import datetime


async def display_timer_investidor10(interval, market_data):
    """Dashboard focado nos dados do Investidor10."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        agora = datetime.now().strftime('%H:%M:%S')
        print(f"=== 💹 INVESTIDOR10 MONITOR | {agora} ===")

        if not market_data:
            print("⏳ Aguardando dados do ticker...")
        else:
            print(f"{'TICKER':<10} | {'PREÇO':<12} | {'MOEDA':<6} | {'REF'}")
            print("-" * 50)
            for ticker, info in list(market_data.items()):
                print(f"{ticker:<10} | {info['price']:<12} | {info['currency']:<6}")

        print("\n" + "=" * 50)
        print("💡 Dica: Ao trocar de ação no site, o terminal limpa o antigo.")
        await asyncio.sleep(interval)
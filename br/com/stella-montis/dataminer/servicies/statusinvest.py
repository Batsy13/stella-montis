import asyncio
import os
from datetime import datetime

async def display_timer_status_invest(interval, market_data):
    """Dashboard para o Status Invest."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        agora = datetime.now().strftime('%H:%M:%S')
        print(f"=== 📊 STATUS INVEST MONITOR | {agora} ===")

        if not market_data:
            print("⏳ Aguardando carregamento dos dados da ação...")
        else:
            print(f"{'ATIVO':<25} | {'PREÇO':<12} | {'REF'}")
            print("-" * 55)
            for name, info in list(market_data.items()):
                print(f"{name:<25} | {info['price']:<12} | {info['ref']}")

        print("\n" + "=" * 55)
        await asyncio.sleep(interval)
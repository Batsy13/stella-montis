import asyncio
import os
from datetime import datetime


async def display_timer_tradingview(interval, market_data):
    """Dashboard limpo que atualiza a cada X segundos."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"=== 🕒 MONITOR DE MERCADO DINÂMICO | {datetime.now().strftime('%H:%M:%S')} ===")

        if not market_data:
            print("⏳ Aguardando primeira captura de dados...")
        else:
            print(f"{'ATIVO':<20} | {'PREÇO':<15} | {'MOEDA':<10}")
            print("-" * 50)
            for name, info in market_data.items():
                print(f"{name:<20} | {info['price']:<15} | {info['currency']:<10}")

        await asyncio.sleep(interval)

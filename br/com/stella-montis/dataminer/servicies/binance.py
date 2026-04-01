import asyncio
import os
from datetime import datetime


async def display_timer_binance(interval, market_data):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"=== 🕒 MONITOR BINANCE (DOM) | {datetime.now().strftime('%H:%M:%S')} ===")

        if not market_data:
            print("⏳ Aguardando carregamento da página...")
        else:
            # Cabeçalho da tabela
            print(f"{'ATIVO':<12} | {'DESCRIÇÃO':<20} | {'PREÇO ATUAL':<15}")
            print("-" * 55)
            for key, info in market_data.items():
                print(f"{info['symbol']:<12} | {info['label']:<20} | {info['price']:<15}")

        await asyncio.sleep(interval)
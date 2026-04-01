import asyncio
import os
from datetime import datetime

async def display_timer_infomoney(interval, maket_data):
    """Dashboard para InfoMoney."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        agora = datetime.now().strftime('%H:%M:%S')
        print(f"=== 📈 INFOMONEY MONITOR | {agora} ===")

        if not maket_data:
            print("⏳ Aguardando carregamento da cotação...")
        else:
            print(f"{'ATIVO':<20} | {'PREÇO (R$)':<15}")
            print("-" * 40)
            for name, info in list(maket_data.items()):
                print(f"{name:<20} | {info['price']:<15}")

        print("\n" + "=" * 40)
        await asyncio.sleep(interval)


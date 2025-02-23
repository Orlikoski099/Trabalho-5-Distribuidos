import subprocess
import time

# Lista dos serviços a serem iniciados
services = [
    ("Agência de Viagens", "agencia.py"),
    ("Companhia Aérea", "companhia_aerea.py"),
    ("Hotel", "hotel.py"),
    ("Locadora de Carro", "locadora_carro.py"),
]

# Dicionário para armazenar os processos
processes = {}

try:
    for name, script in services:
        print(f"Iniciando {name}...")
        processes[name] = subprocess.Popen(
            ["python", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        time.sleep(5)  # Pequeno delay para evitar sobrecarga inicial

    print("\nTodos os serviços foram iniciados!\nPressione CTRL+C para parar.\n")

    # Exibir logs em tempo real
    while True:
        for name, process in processes.items():
            output = process.stdout.readline()
            if output:
                print(f"[{name}] {output.strip()}")

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nEncerrando os serviços...")
    for name, process in processes.items():
        process.terminate()
        print(f"{name} encerrado.")

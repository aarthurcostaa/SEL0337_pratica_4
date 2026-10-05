#!/usr/bin/env python3
"""
SEL0337 - Pratica 4 - Checkpoint 3 (opcional) - passo 2 de 3
Le a tag RFID e mostra o ID (codificacao unica) e o texto gravado.
Anote o ID exibido: ele sera cadastrado em cp3_controle_acesso.py.

Ctrl+C encerra o programa.
"""

from time import sleep

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

GPIO.setwarnings(False)

leitor = SimpleMFRC522()

try:
    print("Aproxime a tag do leitor para leitura.")
    while True:
        id_tag, texto = leitor.read()        # bloqueia ate detectar uma tag
        print(f"ID: {id_tag}\nTexto: {texto.strip()}")
        sleep(3)                             # evita leituras repetidas da mesma tag
except KeyboardInterrupt:
    print("\nEncerrado pelo usuario.")
finally:
    GPIO.cleanup()

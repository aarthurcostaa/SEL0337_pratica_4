#!/usr/bin/env python3
"""
SEL0337 - Pratica 4 - Checkpoint 3 (opcional) - passo 1 de 3
Grava um texto (numero USP da dupla) na tag RFID usando o modulo MFRC522 (SPI).

Antes de rodar:
  sudo raspi-config -> Interface Options -> SPI -> Enable
  pip3 install mfrc522
"""

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

GPIO.setwarnings(False)


TEXTO = "NUSP1/NUSP2"

leitor = SimpleMFRC522()

try:
    print("Aproxime a tag do leitor para gravar.")
    leitor.write(TEXTO)          # bloqueia ate uma tag entrar no campo do leitor
    print(f"Concluido! Texto gravado: {TEXTO}")
finally:
    GPIO.cleanup()

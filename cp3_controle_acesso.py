#!/usr/bin/env python3
"""
SEL0337 - Pratica 4 - Checkpoint 3 (opcional) - passo 3 de 3
Controle de acesso via tag RFID (modulo MFRC522, protocolo SPI).

  Tag cadastrada     -> LED verde    + "acesso liberado"
  Tag nao cadastrada -> LED vermelho + "acesso negado"

LEDs (cada um com resistor de 220 a 330 ohms em serie, catodo no GND):
  LED verde    -> pino fisico 11 (GPIO 17)
  LED vermelho -> pino fisico 13 (GPIO 27)

Ctrl+C encerra o programa.
"""

from time import sleep

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

GPIO.setwarnings(False)

# SUBSTITUA pelo(s) ID(s) mostrado(s) por cp3_ler_tag.py
TAGS_CADASTRADAS = {
    123456789012: "Dupla SEL0337",
}

TEMPO_SINALIZACAO_S = 2

# O leitor precisa ser criado antes de configurar os LEDs: a biblioteca
# mfrc522 escolhe a numeracao dos pinos (normalmente BOARD = pinos fisicos)
leitor = SimpleMFRC522()

if GPIO.getmode() == GPIO.BCM:
    LED_VERDE, LED_VERMELHO = 17, 27     # numeracao GPIO
else:
    LED_VERDE, LED_VERMELHO = 11, 13     # numeracao fisica (mesmos pinos)

GPIO.setup(LED_VERDE, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LED_VERMELHO, GPIO.OUT, initial=GPIO.LOW)

try:
    print("Controle de acesso ativo. Aproxime a tag do leitor.")
    while True:
        id_tag, texto = leitor.read()        # bloqueia ate detectar uma tag

        if id_tag in TAGS_CADASTRADAS:
            print(f"acesso liberado - {TAGS_CADASTRADAS[id_tag]} "
                  f"(ID {id_tag}, texto: {texto.strip()})")
            led = LED_VERDE
        else:
            print(f"acesso negado - tag nao cadastrada (ID {id_tag})")
            led = LED_VERMELHO

        GPIO.output(led, GPIO.HIGH)
        sleep(TEMPO_SINALIZACAO_S)
        GPIO.output(led, GPIO.LOW)
except KeyboardInterrupt:
    print("\nEncerrado pelo usuario.")
finally:
    GPIO.cleanup()

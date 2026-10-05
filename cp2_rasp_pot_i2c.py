#!/usr/bin/env python3
"""
SEL0337 - Pratica 4 - Checkpoint 2
Raspberry Pi como controlador I2C: requisita ao Arduino a leitura do
potenciometro (10 bits) e reconstroi o valor a partir de 2 bytes.

Formato combinado com o Arduino (big-endian):
  dados[0] = byte mais significativo (bits 9..8)
  dados[1] = byte menos significativo (bits 7..0)
  valor    = (dados[0] << 8) | dados[1]      -> 0 a 1023

Ctrl+C encerra o programa.
"""

from time import sleep

try:
    from smbus import SMBus
except ImportError:              # caso so a smbus2 esteja instalada
    from smbus2 import SMBus

ENDERECO_ARDUINO = 0x08          # mesmo endereco definido no sketch
BARRAMENTO_I2C = 1               # /dev/i2c-1 (GPIO 2 = SDA, GPIO 3 = SCL)
REG_POTENCIOMETRO = 0x02         # byte de "registrador"; o Arduino o ignora
N_BYTES = 2
INTERVALO_S = 0.5
V_REF = 5.0                      # referencia do ADC do Arduino Uno
ADC_MAX = 1023                   # 2^10 - 1


def ler_potenciometro(bus):
    """Requisita 2 bytes ao Arduino e devolve (valor, byte_alto, byte_baixo)."""
    dados = bus.read_i2c_block_data(ENDERECO_ARDUINO, REG_POTENCIOMETRO, N_BYTES)
    byte_alto, byte_baixo = dados[0], dados[1]
    valor = (byte_alto << 8) | byte_baixo    # desloca 8 bits e junta os dois bytes
    return valor, byte_alto, byte_baixo


def main():
    bus = SMBus(BARRAMENTO_I2C)
    print("Lendo o potenciometro via I2C (Ctrl+C para sair)")

    try:
        while True:
            try:
                valor, alto, baixo = ler_potenciometro(bus)
            except OSError as erro:
                # Erro 121 (Remote I/O) = o Arduino nao respondeu
                print(f"Falha na comunicacao I2C: {erro}")
                sleep(1)
                continue

            if valor > ADC_MAX:
                print(f"Valor fora da faixa de 10 bits: {valor} "
                      f"(bytes 0x{alto:02X} 0x{baixo:02X}) - confira a ordem dos bytes")
            else:
                tensao = valor * V_REF / ADC_MAX
                print(f"Valor recebido: {valor:4d}  "
                      f"(high = 0x{alto:02X}, low = 0x{baixo:02X})  "
                      f"~ {tensao:.2f} V")

            sleep(INTERVALO_S)
    except KeyboardInterrupt:
        print("\nEncerrado pelo usuario.")
    finally:
        bus.close()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
SEL0337 - Pratica 4 - Checkpoint 1
Raspberry Pi como controlador I2C: envia 1 ou 0 ao Arduino para acender
ou apagar o LED onboard. Qualquer outro valor encerra o programa.

Antes de rodar:
  sudo raspi-config  -> Interface Options -> I2C -> Enable
  sudo i2cdetect -y 1   (deve aparecer 08 na linha 00, coluna 8)
"""

try:
    from smbus import SMBus
except ImportError:              # caso so a smbus2 esteja instalada
    from smbus2 import SMBus

ENDERECO_ARDUINO = 0x08          # mesmo endereco definido no sketch
BARRAMENTO_I2C = 1               # /dev/i2c-1 (GPIO 2 = SDA, GPIO 3 = SCL)


def main():
    bus = SMBus(BARRAMENTO_I2C)
    print("Digite 1 para acender o LED, 0 para apagar ou outro valor para sair.")

    try:
        while True:
            entrada = input(">> ").strip()

            if entrada == "1":
                bus.write_byte(ENDERECO_ARDUINO, 1)
                print("Enviado: 1 (LED aceso)")
            elif entrada == "0":
                bus.write_byte(ENDERECO_ARDUINO, 0)
                print("Enviado: 0 (LED apagado)")
            else:
                print("Encerrando o programa.")
                break
    except OSError as erro:
        # Erro 121 (Remote I/O) = o Arduino nao respondeu no endereco
        print(f"Falha na comunicacao I2C: {erro}")
        print("Confira as ligacoes e rode: sudo i2cdetect -y 1")
    except (KeyboardInterrupt, EOFError):
        print("\nEncerrado pelo usuario.")
    finally:
        bus.close()


if __name__ == "__main__":
    main()

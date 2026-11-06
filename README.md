## SEL0337_pratica_4

Esta prática consiste em 3 etapas que terão seus códigos explicados abaixo.

## Checkpoint 1
Teste de comunicação serial utilizando os arquivos : cp1_arduino_led_i2c.ino e cp1_rasp_led_i2c.py

O I2C usa duas linhas, SDA (dados, bidirecional) e SCL (clock). 

A comunicação é síncrona entre um controlador e um ou mais responders, cada um identificado por um endereço de 7 bits.

Aqui a Raspberry Pi é o controlador e o Arduino é o responder no endereço 0x08.

A Raspberry Pi opera em 3,3 V e o Arduino em 5 V, por isso as linhas passam por um level-shifter bidirecional, uma saída de 5 V nunca pode chegar a um pino da Raspberry Pi.

As ligações físicas são as descritas abaixo: 

| Sinal | Raspberry Pi | Level-shifter | Arduino |
|---|---|---|---|
| SDA | GPIO 2 (pino 3) | LV3 ↔ HV3 | A4 |
| SCL | GPIO 3 (pino 5) | LV4 ↔ HV4 | A5 |
| Alimentação | 3,3 V (pino 1) → LV | HV ← 5V | 5V |
| GND | GND | GND (dos dois lados) | GND |


<img width="1600" height="1200" alt="WhatsApp Image 2026-11-05 at 21 12 22" src="https://github.com/user-attachments/assets/dea7d7ae-ef6e-49a7-9d88-7f033b402ae8" />


# Arduino (cp1_arduino_led_i2c.ino)

Wire.begin(0x08) coloca o Arduino no barramento como responder. 

Wire.onReceive(aoReceber) registra a função chamada a cada escrita da Raspberry Pi.

aoReceber() roda na interrupção do I2C, guarda o byte recebido e sinaliza com uma flag. 

Transações sem dados, como as do i2cdetect, são ignoradas.

O loop() copia o comando com as interrupções desligadas, aciona o LED_BUILTIN e informa o comando no monitor serial. 

O Serial.print fica fora da interrupção para mantê-la curta.

# Raspberry Pi (cp1_rasp_led_i2c.py)

SMBus(1) abre o barramento /dev/i2c-1, e bus.write_byte(0x08, valor) envia um byte.

O valor enviado é o número 1 ou 0 (0x01 ou 0x00), não o caractere ASCII. Por isso o Arduino compara direto com 1 e 0.

Um OSError (erro 121, Remote I/O) indica que nenhum dispositivo respondeu no endereço. Nesse caso o script mostra a falha e sugere o i2cdetect.

O Arduino aparece na linha 00, coluna 8 do `i2cdetect`:

```text
$ sudo i2cdetect -y 1
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- 08 -- -- -- -- -- -- --
```

https://github.com/user-attachments/assets/27d5d785-9b45-4d56-8e97-48223f0e13f4



## Checkpoint 2
Leitura de sinal analógico pela raspi utilizando o arduíno como intermediário : cp2_arduino_pot_i2c.ino e cp2_rasp_pot_i2c.py

O ADC do ATmega328P tem 10 bits (0 a 5 V → 0 a 1023), mas o I2C transfere bytes. Por isso o valor é dividido em dois bytes, enviados do mais significativo para o menos significativo (big-endian):

| Byte | Conteúdo | Faixa |
|---|---|---|
| `dados[0]` | `highByte(valor)`: bits 9 e 8 | 0x00 a 0x03 |
| `dados[1]` | `lowByte(valor)`: bits 7 a 0 | 0x00 a 0xFF |

Reconstrução na Raspberry Pi: `valor = (dados[0] << 8) | dados[1]`. Por exemplo, os bytes `0x02` e `0x9A` dão 2 × 256 + 154 = **666**, cerca de 3,26 V.

São as mesmas do Checkpoint 1, mais o potenciômetro: extremos em 5V e GND do Arduino e terminal central em **A0**. A4 e A5 ficam ocupados pelo I2C.

<img width="1600" height="792" alt="WhatsApp Image 2026-11-05 at 21 20 17" src="https://github.com/user-attachments/assets/df9cd9ce-aacc-4c7b-abfe-b553fbf98309" />

# Arduino (`cp2_arduino_pot_i2c.ino`)

`analogRead(A0)` roda no `loop()` e guarda o resultado em um `uint16_t`, já que um `byte` limitaria o valor a 0–255. A escrita é protegida por `noInterrupts()`: no AVR de 8 bits, uma variável de 16 bits é gravada em duas instruções, e a interrupção do I2C poderia ler um valor pela metade.

`Wire.onRequest(aoRequisitar)` responde a cada requisição. A função copia a leitura uma única vez e envia `{highByte, lowByte}` em um só `Wire.write(pacote, 2)`, então os dois bytes sempre vêm da mesma amostra.

O comportamento do Checkpoint 1 foi mantido: `aoReceber()` ainda trata 1 e 0 como comandos de LED e ignora qualquer outro byte.

O valor enviado é impresso no monitor serial pelo `loop()`, fora da interrupção.

# Raspberry Pi (`cp2_rasp_pot_i2c.py`)

A cada 0,5 s, `bus.read_i2c_block_data(0x08, 0x02, 2)` escreve o byte de "registrador" `0x02` (ignorado pelo Arduino) e lê 2 bytes na mesma transação.

O script reconstrói o valor com bit shift, converte em tensão (`valor * 5.0 / 1023`) e avisa se o resultado passar de 1023, o que indicaria bytes trocados.

Uma falha de comunicação não encerra o programa: o script espera 1 s e tenta de novo.

> O byte de registrador não pode ser `0x00` nem `0x01`. Ele chega ao `aoReceber()` em toda leitura e seria interpretado como comando de LED.

O valor impresso no monitor serial é igual ao recebido na Raspberry Pi em toda a faixa de 0 a 1023.

```text
# Raspberry Pi
Valor recebido:  666  (high = 0x02, low = 0x9A)  ~ 3.26 V

# Monitor serial do Arduino
Valor enviado: 666  (high = 0x2, low = 0x9A)
```

A montagem do circuito e o funcionamento do sistema podem ser vistos abaixo:

https://github.com/user-attachments/assets/7296b3d6-511d-41d6-a123-877f3b083871

# Desafio extra 
Leitura de cartão magnético : cp3_controle_acesso.py, cp3_gravar_tag.py, cp3_ler_tag.py

O MFRC522 lê e grava tags de 13,56 MHz e se comunica com a Raspberry Pi por SPI. O SPI é um barramento síncrono, também com controlador e dispositivo controlado, que usa quatro linhas: MOSI (controlador → dispositivo), MISO (dispositivo → controlador), SCK (clock) e SS/CS (seleção do dispositivo). Em relação ao I2C, é mais rápido, mas exige mais fios e alcança distâncias menores.

### Ligações

| Componente | Raspberry Pi |
|---|---|
| MFRC522 SDA (SS) | GPIO 8 / CE0 (pino 24) |
| MFRC522 SCK | GPIO 11 (pino 23) |
| MFRC522 MOSI | GPIO 10 (pino 19) |
| MFRC522 MISO | GPIO 9 (pino 21) |
| MFRC522 IRQ | não usado |
| MFRC522 GND | GND |
| MFRC522 RST | GPIO 25 (pino 22) |
| MFRC522 3.3V | 3,3 V (nunca 5 V) |
| LED verde | GPIO 17 (pino 11), com resistor de 220–330 Ω até o GND |
| LED vermelho | GPIO 27 (pino 13), com resistor de 220–330 Ω até o GND |

### Implementação

Os três scripts usam a classe `SimpleMFRC522` da biblioteca `mfrc522` e são executados nesta ordem:

1. **`cp3_gravar_tag.py`** grava `"13751207"` com `leitor.write()` e lê a tag de volta para confirmar. A confirmação é necessária porque `write()` retorna mesmo quando a autenticação falha; nesse caso a biblioteca só imprime `AUTH ERROR!!`.
2. **`cp3_ler_tag.py`** mostra em laço o ID e o texto da tag, com `sleep(3)` para evitar leituras repetidas. O ID exibido vai para o cadastro.
3. **`cp3_controle_acesso.py`** compara o ID lido com o dicionário `TAGS_CADASTRADAS` e acende o LED correspondente por 2 s.

Pontos importantes:
- O **ID** é o número de série (UID) da tag convertido em inteiro, e é só ele que decide o acesso. O **texto** fica em 3 blocos de memória da tag (até 48 caracteres ASCII) e é completado com espaços, daí o `.strip()` na leitura.
- A biblioteca define a numeração dos pinos (`GPIO.BOARD`) ao criar o leitor. Por isso o leitor é criado antes de configurar os LEDs, e o script escolhe os pinos 11/13 (BOARD) ou 17/27 (BCM) conforme `GPIO.getmode()`, sem conflito de modo.
- O `GPIO.cleanup()` no `finally` libera os pinos ao encerrar com Ctrl+C.

Para cadastrar outra tag, adicione o ID ao dicionário como inteiro, sem aspas:

```python
TAGS_CADASTRADAS = {
    13189451320: "Arthur e Raphael",
}
```

A montagem do circuito e o funcionamento do sistema podem ser vistos abaixo:


https://github.com/user-attachments/assets/dc6f9626-f136-4a79-a203-d0596d7a22c8

<img width="1200" height="1600" alt="WhatsApp Image 2026-11-05 at 21 22 29" src="https://github.com/user-attachments/assets/ecc5585a-7c48-4f0c-815a-7bd39ffc897c" />

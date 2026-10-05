/*
 * SEL0337 - Pratica 4 - Checkpoint 2
 * Arduino Uno como responder I2C: le um potenciometro (ADC de 10 bits)
 * e devolve o valor a Raspberry Pi em 2 bytes, a cada requisicao.
 *
 * Formato da resposta (big-endian, byte mais significativo primeiro):
 *   byte 0 = highByte(valor)  -> bits 9..8 (vale de 0 a 3)
 *   byte 1 = lowByte(valor)   -> bits 7..0 (vale de 0 a 255)
 * Reconstrucao na Raspberry Pi: valor = (byte0 << 8) | byte1
 *
 * O comportamento do Checkpoint 1 foi mantido: escrever 1 ou 0 no
 * endereco ainda acende/apaga o LED_BUILTIN. Qualquer outro byte recebido
 * (como o "registrador" 0x02 enviado antes da leitura) e ignorado.
 *
 * Ligacoes: A4 = SDA, A5 = SCL (via level-shifter)
 *           Potenciometro: extremos em 5V e GND, terminal central em A0
 */

#include <Wire.h>

const uint8_t ENDERECO_I2C = 0x08;
const uint8_t PINO_POT     = A0;     // nao usar A4/A5: sao os pinos do I2C

// Compartilhadas entre as interrupcoes do I2C e o loop()
volatile uint16_t leituraAtual = 0;      // ultima conversao A/D (0 a 1023)
volatile uint16_t valorEnviado = 0;      // copia do que foi para o barramento
volatile bool     houveEnvio   = false;
volatile bool     houveComando = false;
volatile uint8_t  comandoLed   = 0;

// Raspberry Pi pediu dados (leitura): responde com os 2 bytes.
// uint16_t e obrigatorio aqui: um "byte" guardaria so 0 a 255.
void aoRequisitar() {
  uint16_t valor = leituraAtual;
  uint8_t pacote[2] = { highByte(valor), lowByte(valor) };
  Wire.write(pacote, 2);             // uma unica chamada com o pacote inteiro

  valorEnviado = valor;
  houveEnvio = true;
}

// Raspberry Pi escreveu dados: trata os comandos de LED do Checkpoint 1.
void aoReceber(int quantidade) {
  if (quantidade < 1) {
    return;
  }
  uint8_t recebido = 0;
  while (Wire.available()) {
    recebido = Wire.read();
  }
  if (recebido == 0 || recebido == 1) {
    digitalWrite(LED_BUILTIN, recebido);
    comandoLed = recebido;
    houveComando = true;
  }
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  Serial.begin(9600);

  Wire.begin(ENDERECO_I2C);
  Wire.onRequest(aoRequisitar);
  Wire.onReceive(aoReceber);

  Serial.print(F("Arduino pronto. Endereco I2C: 0x"));
  Serial.println(ENDERECO_I2C, HEX);
}

void loop() {
  // A conversao A/D fica no loop para manter as interrupcoes do I2C curtas
  uint16_t leitura = analogRead(PINO_POT);

  noInterrupts();                    // escrita de 16 bits nao e atomica no AVR
  leituraAtual = leitura;
  interrupts();

  if (houveEnvio) {
    noInterrupts();
    uint16_t v = valorEnviado;
    houveEnvio = false;
    interrupts();

    Serial.print(F("Valor enviado: "));
    Serial.print(v);
    Serial.print(F("  (high = 0x"));
    Serial.print(highByte(v), HEX);
    Serial.print(F(", low = 0x"));
    Serial.print(lowByte(v), HEX);
    Serial.println(F(")"));
  }

  if (houveComando) {
    noInterrupts();
    uint8_t c = comandoLed;
    houveComando = false;
    interrupts();

    Serial.print(F("Comando de LED recebido: "));
    Serial.println(c);
  }
}

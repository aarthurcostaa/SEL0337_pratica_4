/*
 * SEL0337 - Pratica 4 - Checkpoint 1
 * Arduino Uno (ATmega328P) como dispositivo controlado (responder) I2C.
 *
 * Recebe 1 byte da Raspberry Pi:
 *   1 -> acende o LED_BUILTIN
 *   0 -> apaga  o LED_BUILTIN
 * e informa no monitor serial (9600 baud) o comando recebido.
 *
 * Ligacoes (via level-shifter): A4 = SDA, A5 = SCL, 5V = HV, GND = GND.
 */

#include <Wire.h>

const uint8_t ENDERECO_I2C = 0x08;   // mesmo endereco usado no script Python

// Variaveis compartilhadas entre a interrupcao do I2C e o loop()
volatile bool    novoComando = false;
volatile uint8_t comando     = 0;

// Chamada pela biblioteca Wire (dentro de uma interrupcao) sempre que a
// Raspberry Pi escreve neste endereco. Deve ser curta: so guarda o dado.
void aoReceber(int quantidade) {
  if (quantidade < 1) {
    return;                          // i2cdetect so "toca" no endereco, sem dados
  }
  while (Wire.available()) {
    comando = Wire.read();           // fica com o ultimo byte recebido
  }
  novoComando = true;
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  Serial.begin(9600);

  Wire.begin(ENDERECO_I2C);          // entra no barramento como responder
  Wire.onReceive(aoReceber);         // registra a funcao de recepcao

  Serial.print(F("Arduino pronto. Endereco I2C: 0x"));
  Serial.println(ENDERECO_I2C, HEX);
}

void loop() {
  if (novoComando) {
    // Copia o dado com as interrupcoes desligadas para nao ser alterado no meio
    noInterrupts();
    uint8_t c = comando;
    novoComando = false;
    interrupts();

    if (c == 1) {
      digitalWrite(LED_BUILTIN, HIGH);
      Serial.println(F("Comando recebido: 1 -> LED aceso"));
    } else if (c == 0) {
      digitalWrite(LED_BUILTIN, LOW);
      Serial.println(F("Comando recebido: 0 -> LED apagado"));
    } else {
      Serial.print(F("Comando desconhecido recebido: "));
      Serial.println(c);
    }
  }
}

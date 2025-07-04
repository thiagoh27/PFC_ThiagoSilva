const int ENA = 25;
const int pinSensor = 35;

float setpoint = 2.5;
float Kp = 1.0, Ki = 0.0, Kd = 0.0;
float erro_anterior = 0.0, integral = 0.0;

const float referenciaADC = 3.3;
const int resolucaoADC = 4095;

int pwmManual = 0;

void setup() {
  Serial.begin(115200);
  analogWriteFrequency(ENA, 1000);
  analogWriteResolution(ENA, 8);
  pinMode(pinSensor, INPUT);
  delay(1000);
}

float lerTensaoGerada() {
  int valorADC = analogRead(pinSensor);
  return (valorADC * referenciaADC) / resolucaoADC;
}

bool flagAutomatico = false;
bool modo_automatico_anterior = false;  // novo

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.indexOf(';') > 0) {

      int idx1 = input.indexOf(';');
      int idx2 = input.indexOf(';', idx1 + 1);
      int idx3 = input.indexOf(';', idx2 + 1);
      int idx4 = input.indexOf(';', idx3 + 1);
      pwmManual = input.substring(0, idx1).toInt();
      setpoint = input.substring(idx1 + 1, idx2).toFloat();
      Kp = input.substring(idx2 + 1, idx3).toFloat();
      Ki = input.substring(idx3 + 1, idx4).toFloat();
      Kd = input.substring(idx4 + 1).toFloat();

      flagAutomatico = (pwmManual == 0);
      if (flagAutomatico && !modo_automatico_anterior) {
        integral = 0.0;
        erro_anterior = 0.0;
      }

      modo_automatico_anterior = flagAutomatico;
    }
  }

  float tensao = lerTensaoGerada();
  int pwmAplicado = pwmManual;

  if (flagAutomatico) {
    float erro = setpoint - tensao;
    integral += erro * 0.01;  
    float derivada = (erro - erro_anterior) / 0.5;
    erro_anterior = erro;

    float saida = Kp * erro + Ki * integral + Kd * derivada;
    pwmAplicado = constrain((int)saida, 0, 255);
  }

  analogWrite(ENA, pwmAplicado);

  Serial.print(pwmAplicado);
  Serial.print(",");
  Serial.print(tensao, 2);
  Serial.print(",");
  Serial.println(setpoint, 2);

  delay(10);
}

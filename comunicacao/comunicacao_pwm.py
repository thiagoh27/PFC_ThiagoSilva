import serial
import time

PORTA = 'COM8'          # porta em que o ESP-32 se encontra
BAUDRATE = 115200       # velocidade de transmissão dos dados

class SerialPWM:
    def __init__(self):             #método construtor da conexão serial
        try:
            self.conexaoSerial = serial.Serial(PORTA, BAUDRATE, timeout=1)
            time.sleep(2)       #tempo comum para esperar a leitura do ESP-32
            print(f"[INFO] Conectado ao ESP32 em {PORTA}")
        except Exception as e:
            print(f"[ERRO] Falha na conexão serial: {e}")
            self.conexaoSerial = None

    def enviar_pwm(self, valor):    # método que envia o valor de pwm para o ESP-32 (valor varia de 0 a 255)
        if self.conexaoSerial and 0 <= valor <= 255:
            comando = f"{valor}\n".encode()     # .enconde() codifica o valor em bytes, porque a comunicação serial só acontece em bytes e não em string
            self.conexaoSerial.write(comando)   # escreve diretamente na porta serial
            print(f"[ENVIADO] PWM = {valor}")

    def ler_dados(self):
        if self.conexaoSerial and self.conexaoSerial.in_waiting:
            try:
                return self.conexaoSerial.readline().decode('utf-8').strip()
            except:
                return None
        return None


    def fechar(self):
        if self.conexaoSerial:
            self.conexaoSerial.close()
            print("[INFO] Conexão serial encerrada.")

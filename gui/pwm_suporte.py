# código de suporte da interface da IHM, criado com o software Page (arraste e solte) adaptado para envio de dados ao ESP-32

#! /usr/bin/env python3
#  -*- coding: utf-8 -*-
# Support module generated by PAGE version 8.0

import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *

from gui import PythonGUI


#necessário para o gráfico em tempo real
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#Necessário para a comunicação serial
from comunicacao.comunicacao_pwm import SerialPWM
from tkinter import messagebox

pwm_serial = SerialPWM()
dados_pwm = []
dados_tensao = []
Ki = 0.0
Kd = 0.0
integral = 0.0
erro_anterior = 0.0
dados_setpoint = []
setpoint_tensao = 2.5
gerandoGrafico = True
amostragem_ms = 500
modo_malha_fechada = False
Kp = 0.0

pwm_atual = 0 

def iniciar_grafico(frame_tk, entry_setpoint, entry_kp, entry_ki, entry_kd,btn_malha_aberta, btn_malha_fechada, entry_pwm_manual):
    global figura, eixo, eixo2, canvas, log_text, btn_toggle, entry_set, entry_kp_var, entry_ki_var, entry_kd_var, entry_pwm, botao_malha_aberta, botao_malha_fechada

    entry_set = entry_setpoint
    entry_kp_var = entry_kp
    entry_ki_var = entry_ki
    entry_kd_var = entry_kd
    entry_pwm = entry_pwm_manual
    botao_malha_aberta = btn_malha_aberta
    botao_malha_fechada = btn_malha_fechada

    figura = plt.Figure(figsize=(5, 4), dpi=100)
    eixo = figura.add_subplot(111)
    eixo2 = eixo.twinx()

    canvas = FigureCanvasTkAgg(figura, master=frame_tk)
    canvas.get_tk_widget().pack(fill='both', expand=True)

    btn_toggle = tk.Button(frame_tk, text="Pausar", command=alternar_grafico)
    btn_toggle.pack(pady=2)

    log_text = tk.Text(frame_tk, height=7, width=70, bg="#f0f0f0", fg="black")
    log_text.pack(fill='both', expand=False)

    atualizar_grafico()

def alternar_grafico():
    global gerandoGrafico
    gerandoGrafico = not gerandoGrafico
    btn_toggle.config(text="Iniciar" if not gerandoGrafico else "Pausar")

def atualizar_grafico():
    global integral, erro_anterior

    if gerandoGrafico:
        linha = pwm_serial.ler_dados()
        if linha:
            try:
                pwm_str, tensao_str, setpoint_str = linha.strip().split(',')
                tensao = float(tensao_str)
                pwm = int(pwm_str)
                setpoint = float(setpoint_str)
            except ValueError:
                return
        else:
            return

        dados_pwm.append(pwm)
        dados_tensao.append(tensao)
        dados_setpoint.append(setpoint)

        if len(dados_pwm) > 20:
            dados_pwm.pop(0)
            dados_tensao.pop(0)
            dados_setpoint.pop(0)

        eixo.clear()
        eixo2.clear()

        eixo.plot(dados_tensao, label="Tensão Lida (V)", color='blue')
        eixo.plot(dados_setpoint, label="Setpoint (V)", color='green')
        eixo.set_ylim(0, 5)
        eixo.set_ylabel("Tensão (V)")

        eixo2.plot(dados_pwm, label="PWM", color='orange')
        eixo2.set_ylim(0, 255)
        eixo2.set_ylabel("PWM")

        linhas1, labels1 = eixo.get_legend_handles_labels()
        linhas2, labels2 = eixo2.get_legend_handles_labels()
        eixo.legend(linhas1 + linhas2, labels1 + labels2, loc="upper right")

        canvas.draw()

        log_text.delete('1.0', tk.END)
        for i in range(-10, 0):
            if abs(i) <= len(dados_pwm):
                idx = i % len(dados_pwm)
                linha = f"{len(dados_pwm) + i}: PWM = {dados_pwm[idx]} | Tensão = {dados_tensao[idx]:.2f} V | Setpoint = {dados_setpoint[idx]:.2f} V\n"
                log_text.insert(tk.END, linha)

    canvas.get_tk_widget().after(amostragem_ms, atualizar_grafico)

def enviar_todos():
    global modo_malha_fechada, pwm_atual
    try:
        pwm_manual = int(entry_pwm.get())
        setpoint = float(entry_set.get())
        kp = float(entry_kp_var.get())
        ki = float(entry_ki_var.get())
        kd = float(entry_kd_var.get())

        if 0 <= pwm_manual <= 255:
            comando = f"{pwm_manual};{setpoint};{kp};{ki};{kd}\n"
            pwm_serial.conexaoSerial.write(comando.encode())
            pwm_atual = pwm_manual
            print(f"[ENVIADO] {comando.strip()}")
        else:
            messagebox.showwarning("Valor inválido", "O PWM deve estar entre 0 e 255.")
    except ValueError:
        messagebox.showerror("Erro", "Valor inválido. Digite inteiros.")

def enviar_pwm(valor):
    global modo_malha_fechada, pwm_atual
    modo_malha_fechada = False
    try:
        pwm = int(valor)
        pwm_atual = pwm
        if 0 <= pwm <= 255:
            setpoint = entry_set.get()
            kp = entry_kp_var.get()
            ki = entry_ki_var.get()
            kd = entry_kd_var.get()
            comando = f"{pwm};{setpoint};{kp};{ki};{kd}\n"
            pwm_serial.conexaoSerial.write(comando.encode())
        else:
            messagebox.showwarning("Valor inválido", "Digite um valor entre 0 e 255.")
    except:
        messagebox.showerror("Erro", "Valor inválido. Digite inteiros.")

def ativar_malha_fechada():
    global modo_malha_fechada
    modo_malha_fechada = True
    entry_pwm.delete(0, tk.END)
    pwm = 0
    setpoint = entry_set.get()
    kp = entry_kp_var.get()
    ki = entry_ki_var.get()
    kd = entry_kd_var.get()
    comando = f"{pwm};{setpoint};{kp};{ki};{kd}\n"
    pwm_serial.conexaoSerial.write(comando.encode())

def ativar_malha_aberta():
    global modo_malha_fechada, pwm_atual
    modo_malha_fechada = False
    valor = entry_pwm.get()
    enviar_pwm(valor if valor else pwm_atual)

def main(*args):
    global root
    root = tk.Tk()
    root.protocol('WM_DELETE_WINDOW', root.destroy)
    global _top1, _w1
    _top1 = root
    _w1 = PythonGUI.Toplevel1(_top1)
    root.mainloop()

if __name__ == '__main__':
    PythonGUI.start_up()

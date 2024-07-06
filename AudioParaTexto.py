import subprocess
import speech_recognition as sr
import os
import language_tool_python
import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog
import threading
from datetime import timedelta

def converter_audio_para_wav(caminho_entrada, caminho_saida):
    comando = ['ffmpeg', '-i', caminho_entrada, caminho_saida]
    subprocess.run(comando, check=True)

def converter_audio_para_texto(caminho_audio, output_widget):
    extensoes_entrada = ['.m4a', '.m4p', '.mp3', '.aac', '.ogg', '.flac', '.wav']
    caminho_wav = caminho_audio
    for ext in extensoes_entrada:
        if caminho_audio.endswith(ext):
            caminho_wav = caminho_audio.replace(ext, '.wav')
            break

    converter_audio_para_wav(caminho_audio, caminho_wav)
    reconhecedor = sr.Recognizer()
    
    with sr.AudioFile(caminho_wav) as fonte:
        duracao_audio = fonte.DURATION
        duracao_segmento = 60
        texto = ""
        
        for i in range(0, int(duracao_audio), duracao_segmento):
            segmento_audio = reconhecedor.record(fonte, duration=duracao_segmento)
            timestamp = str(timedelta(seconds=i))
            try:
                texto_segmento = reconhecedor.recognize_google(segmento_audio, language="pt-BR")
                texto += f"[{timestamp}] {texto_segmento} "
                output_widget.insert(tk.END, f"[{timestamp}] {texto_segmento}\n")
                output_widget.yview(tk.END)
            except sr.UnknownValueError:
                texto += f"[{timestamp}] [inaudível] "
                output_widget.insert(tk.END, f"[{timestamp}] [inaudível]\n")
                output_widget.yview(tk.END)
            except sr.RequestError as e:
                texto += f"[{timestamp}] [erro na requisição ao serviço de reconhecimento de fala; {e}] "
                output_widget.insert(tk.END, f"[{timestamp}] [erro na requisição ao serviço de reconhecimento de fala; {e}]\n")
                output_widget.yview(tk.END)

        return texto.strip()

def corrigir_texto(texto):
    tool = language_tool_python.LanguageTool('pt-BR')
    matches = tool.check(texto)
    texto_corrigido = language_tool_python.utils.correct(texto, matches)
    return texto_corrigido

def processar_audio(caminho_audio, output_widget):
    texto = converter_audio_para_texto(caminho_audio, output_widget)
    texto_corrigido = corrigir_texto(texto)
    output_widget.insert(tk.END, f"Texto corrigido: {texto_corrigido}\n")

def selecionar_arquivo():
    caminho_audio = filedialog.askopenfilename(filetypes=[("Audio Files", "*.m4a *.m4p *.mp3 *.aac *.ogg *.flac *.wav")])
    entrada_arquivo.delete(0, tk.END)
    entrada_arquivo.insert(0, caminho_audio)

def iniciar_processamento():
    caminho_audio = entrada_arquivo.get()
    threading.Thread(target=processar_audio, args=(caminho_audio, saida_texto)).start()

def limpar_tudo():
    entrada_arquivo.delete(0, tk.END)
    saida_texto.delete(1.0, tk.END)

def salvar_texto():
    texto = saida_texto.get(1.0, tk.END)
    caminho_texto_saida = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if caminho_texto_saida:
        with open(caminho_texto_saida, 'w', encoding='utf-8') as arquivo:
            arquivo.write(texto)
        print(f"Texto salvo em: {caminho_texto_saida}")

janela = tk.Tk()
janela.title("Conversor de Áudio para Texto")

tk.Label(janela, text="Caminho do Arquivo de Áudio:").pack(pady=5)
entrada_arquivo = tk.Entry(janela, width=50)
entrada_arquivo.pack(pady=5)
entrada_arquivo.bind("<Button-1>", lambda event: selecionar_arquivo())

botao_iniciar = tk.Button(janela, text="Iniciar", command=iniciar_processamento)
botao_iniciar.pack(pady=5)

botao_limpar = tk.Button(janela, text="Limpar Tudo", command=limpar_tudo)
botao_limpar.pack(pady=5)

botao_salvar = tk.Button(janela, text="Salvar Texto", command=salvar_texto)
botao_salvar.pack(pady=5)

saida_texto = scrolledtext.ScrolledText(janela, width=80, height=20)
saida_texto.pack(pady=5)

janela.mainloop()

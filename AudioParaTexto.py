import subprocess
import speech_recognition as sr
import os

def converter_audio_para_wav(caminho_entrada, caminho_saida):
    comando = ['ffmpeg', '-i', caminho_entrada, caminho_saida]
    subprocess.run(comando, check=True)

def converter_audio_para_texto(caminho_audio):
    caminho_wav = caminho_audio.replace('.m4a', '.wav').replace('.m4p', '.wav')
    converter_audio_para_wav(caminho_audio, caminho_wav)
    reconhecedor = sr.Recognizer()
    
    with sr.AudioFile(caminho_wav) as fonte:
        duracao_audio = fonte.DURATION
        duracao_segmento = 60
        texto = ""
        
        for i in range(0, int(duracao_audio), duracao_segmento):
            segmento_audio = reconhecedor.record(fonte, duration=duracao_segmento)
            
            try:
                texto_segmento = reconhecedor.recognize_google(segmento_audio, language="pt-BR")
                texto += texto_segmento + " "
            except sr.UnknownValueError:
                texto += "[inaudível] "
            except sr.RequestError as e:
                texto += f"[erro na requisição ao serviço de reconhecimento de fala; {e}] "

        return texto.strip()

def salvar_texto_em_arquivo(texto, caminho_saida):
    with open(caminho_saida, 'w', encoding='utf-8') as arquivo:
        arquivo.write(texto)


arquivo_audio = "C:\\Users\\maest\\OneDrive\\Área de Trabalho\\bucho\\André_Neto fumo.mp4"
texto = converter_audio_para_texto(arquivo_audio)

arquivo_texto_saida = arquivo_audio.replace('.m4a', '.txt').replace('.m4p', '.txt')
salvar_texto_em_arquivo(texto, arquivo_texto_saida)
print(f"Texto salvo em: {arquivo_texto_saida}")

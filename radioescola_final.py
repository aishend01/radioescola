import os
import random
import pygame
import time
from moviepy.editor import AudioFileClip
from pytube import Playlist
import re
from datetime import datetime

# Configurações
music_folder = r'./musicas'

# Lista de horários
schedules = [
    ("07:30", "08:30"),
    ("09:20", "9:30"),
    ("10:20", "10:40"),
    ("11:36", "11:38"),
    ("11:39", "11:41"),
    ("13:25", "13:30"),
    ("14:20", "14:30"),
    ("15:20", "15:30"),
    ("16:20", "16:40"),
    ("17:30", "17:35")
]

# Adicionando um controle de estado para a reprodução de música
music_playing = False

def remove_non_mp3_files(folder):
    for file in os.listdir(folder):
        if not file.endswith('.mp3'):
            file_path = os.path.join(folder, file)
            os.remove(file_path)
            print(f'Arquivo {file} removido.')

def play_music(end_time_str):
    global music_playing
    music_list = os.listdir(music_folder)
    chosen_music = random.choice(music_list)
    music_path = os.path.join(music_folder, chosen_music)

    pygame.mixer.init()
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(1)  # Volume máximo

    pygame.mixer.music.play()

    # Obter o tempo de término
    end_time = datetime.strptime(end_time_str, "%H:%M")

    fade_duration = 5  # Tempo em segundos para o fade-out
    fade_step = 0.05  # Passo de ajuste do volume (0.05 significa 5% de mudança)

    # Aguarde a música terminar ou até que o tempo de término seja alcançado
    while pygame.mixer.music.get_busy():
        current_time = datetime.now().time()
        if current_time > end_time.time():
            # Gradualmente diminua o volume
            for i in range(int(1 / fade_step)):
                pygame.mixer.music.set_volume(1 - i * fade_step)
                time.sleep(fade_duration / (1 / fade_step))

            pygame.mixer.music.stop()
            break

    music_playing = False


def download_and_convert_music(playlist_url, destination_path):
    # Baixa a playlist
    playlist = Playlist(playlist_url)

    os.makedirs(destination_path, exist_ok=True)

    # Obtém os títulos dos vídeos na playlist
    playlist_titles = [re.sub(r'[^\w\s]', '', video.title) for video in playlist.videos]
    global music_playing
    music_playing = False
    for video in playlist.videos:
        try:
            video_title = re.sub(r'[^\w\s]', '', video.title)
            mp3_path = os.path.join(destination_path, f'{video_title}.mp3')

            if os.path.exists(mp3_path):
                print(f'O arquivo MP3 para "{video_title}" já existe. Pulando...')
                continue

            audio_stream = video.streams.filter(only_audio=True).first()
            audio_stream.download(output_path=destination_path, filename=video_title + ".webm")

            print(f'Áudio para o vídeo "{video_title}" baixado com sucesso!')
        except Exception as e:
            print(f'Erro ao baixar o áudio para o vídeo "{video_title}": {e}')

    # Remove arquivos MP3 que não correspondem aos títulos na playlist
    for file_name in os.listdir(destination_path):
        if file_name.endswith('.mp3'):
            video_title = os.path.splitext(file_name)[0]
            if re.sub(r'[^\w\s]', '', video_title) not in playlist_titles:
                os.remove(os.path.join(destination_path, file_name))
                print(f'Arquivo "{file_name}" removido.')

    for file_name in os.listdir(destination_path):
        if file_name.endswith('.webm'):
            video_title = os.path.splitext(file_name)[0]
            if re.sub(r'[^\w\s]', '', video_title) not in playlist_titles:
                os.remove(os.path.join(destination_path, file_name))
                print(f'Arquivo "{file_name}" removido.')

            webm_path = os.path.join(destination_path, file_name)
            mp3_path = os.path.join(destination_path, f'{video_title}.mp3')

            audio_clip = AudioFileClip(webm_path)
            audio_clip.write_audiofile(mp3_path)

            os.remove(webm_path)

            print(f'Arquivo "{file_name}" convertido para MP3, arquivo webm removido.')

    print('Conversão concluída!')

def read_url_from_file():
    with open('playlist.txt', 'r') as file:
        return file.readline().strip()
    
def convert_str_to_time(time_str):
    return datetime.strptime(time_str, "%H:%M")

if __name__ == "__main__":
    playlist_url = read_url_from_file()
    print(f"Playlist URL: {playlist_url}")
    destination_path = r'./musicas'

    download_and_convert_music(playlist_url, destination_path)

    while True:
        current_time = datetime.now().time()
        current_time_str = current_time.strftime("%H:%M")
        print(f"Aguardando o horário... Horário atual: {current_time_str}")

        for start_time, end_time in schedules:
            start_time = convert_str_to_time(start_time)
            end_time = convert_str_to_time(end_time)

            now = datetime.now()

            if start_time.time() <= now.time() < end_time.time():
                print("Horário de início alcançado!")

                while start_time.time() <= now.time() < end_time.time():
                    if not music_playing:
                        print("Tocando música")
                        play_music(end_time.strftime("%H:%M"))

                    now = datetime.now()
                    time.sleep(0.3)

            else:
                time.sleep(0.3)

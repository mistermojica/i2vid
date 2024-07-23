import requests
from moviepy.editor import *
import os
from dotenv import load_dotenv, find_dotenv
import math
from PIL import Image
import numpy as np

# Asegúrate de tener la configuración correcta para acceder a Amazon Polly
import boto3

# Cargar variables de entorno
load_dotenv(find_dotenv())

voices = [
    {"Engine": "generative", "LanguageCode": "en-US", "VoiceId": "Matthew", "Gender": "Male", "TextType": "text", "Newscaster": ""},
    {"Engine": "generative", "LanguageCode": "en-US", "VoiceId": "Ruth", "Gender": "Female", "TextType": "text", "Newscaster": ""},
    {"Engine": "long-form", "LanguageCode": "en-US", "VoiceId": "Danielle", "Gender": "Female", "TextType": "text", "Newscaster": ""},
    {"Engine": "long-form", "LanguageCode": "en-US", "VoiceId": "Gregory", "Gender": "Male", "TextType": "text", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Danielle", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Gregory", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Ivy", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Joanna", "Gender": "Female", "TextType": "ssml", "Newscaster": "news"},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Kendra", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Kimberly", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Salli", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Joey", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Justin", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Kevin", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Matthew", "Gender": "Male", "TextType": "ssml", "Newscaster": "news"},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Ruth", "Gender": "Female", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "en-US", "VoiceId": "Stephen", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "neural", "LanguageCode": "es-US", "VoiceId": "Lupe", "Gender": "Female", "TextType": "ssml", "Newscaster": "news"},
    {"Engine": "neural", "LanguageCode": "es-US", "VoiceId": "Pedro", "Gender": "Male", "TextType": "ssml", "Newscaster": ""},
    {"Engine": "standard", "LanguageCode": "es-US", "VoiceId": "Miguel", "Gender": "Male", "TextType": "ssml", "Newscaster": ""}
]

def get_polly_response(engine, voiceid, text, prosodyrate="90%"):
    print("get_polly_response:", engine, voiceid, text, prosodyrate)

    # Coloca tu lista de voces aquí
    voice = next((v for v in voices if v["Engine"] == engine and v["VoiceId"] == voiceid), None)
    
    print(voice)
        
    if not voice:
        raise ValueError(f"Voice with Engine '{engine}' and VoiceId '{voiceid}' not found.")
    
    text_type = voice["TextType"]
    language_code = voice["LanguageCode"]
    newscaster = voice["Newscaster"]

    if text_type == "text":
        polly_text = text
    elif text_type == "ssml":
        if newscaster == "news":
            polly_text = f'<speak><prosody rate="{prosodyrate}"><amazon:domain name="news">{text}</amazon:domain></prosody></speak>'
        else:
            polly_text = f'<speak><prosody rate="{prosodyrate}">{text}</prosody></speak>'
    else:
        raise ValueError("Invalid TextType")

    polly_client = boto3.Session(profile_name='doccumi', region_name="us-east-1").client("polly")
    
    print("polly_client:", polly_client)
    print("get_polly_response 2:", engine, "mp3", polly_text, text_type, voiceid, language_code)
    
    response = polly_client.synthesize_speech(
        Engine=engine,
        OutputFormat="mp3",
        Text=polly_text,
        TextType=text_type,
        VoiceId=voiceid,
        LanguageCode=language_code,
    )
    
    return response

def text_to_speech_polly(text, output_filename, voz):
    response = get_polly_response("neural", voz, text, "90%")
    audio_data = response["AudioStream"].read()
    
    with open(output_filename, "wb") as out:
        out.write(audio_data)

    return output_filename

def download_image(url, output_filename):
    response = requests.get(url)
    with open(output_filename, 'wb') as file:
        file.write(response.content)
    return output_filename

def process_images_and_audios(data):
    data = data[:4]

    images = []
    audios = []

    for idx, item in enumerate(data):
        img_filename = f"image_{idx}.jpg"
        audio_filename = f"audio_{idx}.mp3"

        download_image(item["url"], img_filename)
        text_to_speech_polly(item["description"], audio_filename, "Pedro")

        images.append(img_filename)
        audios.append(audio_filename)

    return images, audios

# def create_video(images, audios, output_filename):
#     clips = []
#     for img, audio in zip(images, audios):
#         audio_clip = AudioFileClip(audio)
#         img_clip = ImageClip(img, duration=audio_clip.duration).set_audio(audio_clip)

#         # Asegurar que el video sea vertical y la imagen horizontal se mueva de izquierda a derecha
#         img_clip = img_clip.resize(height=1920).crop(x1=0, y1=0, width=1080, height=1920)
#         img_clip = img_clip.set_position(lambda t: ('center', 0)) \
#                            .set_duration(audio_clip.duration) \
#                            .set_audio(audio_clip) \
#                            .fx(vfx.crop, width=1080, height=1920, x_center=img_clip.w/2, y_center=img_clip.h/2)
#         clips.append(img_clip)

#     final_clip = concatenate_videoclips(clips, method="compose")

#     # Agregar transiciones horizontales entre las fotos
#     def add_transitions(clips, transition_duration=1):
#         new_clips = []
#         for i in range(len(clips) - 1):
#             new_clips.append(clips[i])
#             transition = clips[i].crossfadeout(transition_duration).set_start(clips[i].duration - transition_duration)
#             new_clips.append(transition)
#         new_clips.append(clips[-1])
#         return concatenate_videoclips(new_clips, method="compose")

#     final_clip_with_transitions = add_transitions(clips)

#     # Cambiar el tamaño del video a 720x1280 para generarlo más rápido
#     # final_clip_with_transitions = final_clip_with_transitions.resize(width=720, height=1280)

#     final_clip_with_transitions.write_videofile(output_filename, fps=24, codec='libx264', audio_codec='aac', threads=4)

def zoom_in_effect(clip, zoom_ratio=0.04):
    def effect(get_frame, t):
        img = Image.fromarray(get_frame(t))
        base_size = img.size

        new_size = [
            math.ceil(img.size[0] * (1 + (zoom_ratio * t))),
            math.ceil(img.size[1] * (1 + (zoom_ratio * t)))
        ]

        # The new dimensions must be even.
        new_size[0] = new_size[0] + (new_size[0] % 2)
        new_size[1] = new_size[1] + (new_size[1] % 2)

        img = img.resize(new_size, Image.LANCZOS)

        x = math.ceil((new_size[0] - base_size[0]) / 2)
        y = math.ceil((new_size[1] - base_size[1]) / 2)

        img = img.crop([
            x, y, new_size[0] - x, new_size[1] - y
        ]).resize(base_size, Image.LANCZOS)

        result = np.array(img)
        img.close()

        return result

    return clip.fl(effect)

def create_video(images, audios, output_filename):
    clips = []
    num_images = len(images)
    num_audios = len(audios)

    if num_images < 2 or num_audios < 1:
        raise ValueError("Debe haber al menos 2 imágenes y 1 audio.")

    for i in range(0, min(num_images, num_audios * 2), 2):
        audio_clip1 = AudioFileClip(audios[i // 2])
        audio_clip2 = AudioFileClip(audios[i // 2 + 1]) if (i // 2 + 1) < num_audios else None

        img_clip1 = ImageClip(images[i]).set_duration(audio_clip1.duration + (audio_clip2.duration if audio_clip2 else 0)).set_audio(audio_clip1)
        img_clip1 = img_clip1.resize(width=1080)
        
        img_clip2 = ImageClip(images[i + 1]).set_duration(audio_clip1.duration + (audio_clip2.duration if audio_clip2 else 0)) if i + 1 < num_images else None
        if img_clip2:
            img_clip2 = img_clip2.resize(width=1080)

        img_clip1 = zoom_in_effect(img_clip1).set_position(("center", "top"))
        if img_clip2:
            img_clip2 = zoom_in_effect(img_clip2).set_position(("center", "bottom"))

        if img_clip2:
            combined_duration = audio_clip1.duration + (audio_clip2.duration if audio_clip2 else 0)
            video = CompositeVideoClip([img_clip1, img_clip2], size=(1080, 1920)).set_duration(combined_duration)
            if audio_clip2:
                combined_audio = concatenate_audioclips([audio_clip1, audio_clip2])
                video = video.set_audio(combined_audio)
            else:
                video = video.set_audio(audio_clip1)
        else:
            video = CompositeVideoClip([img_clip1], size=(1080, 1920)).set_duration(audio_clip1.duration).set_audio(audio_clip1)

        clips.append(video)

    final_clip = concatenate_videoclips(clips, method="compose").resize(width=720, height=1280)
    
    final_clip.write_videofile(
        output_filename,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        audio_bitrate='64k',
        threads=4
    )



# def create_video(images, audios, output_filename):
#     clips = []
#     for img, audio in zip(images, audios):
#         audio_clip = AudioFileClip(audio)
#         img_clip = ImageClip(img).set_duration(audio_clip.duration).set_audio(audio_clip)

#         # Asegurar que el video sea vertical
#         img_clip = img_clip.resize(height=1920)

#         # Movimiento de izquierda a derecha o derecha a izquierda
#         img_clip = img_clip.set_position(lambda t: ((t * img_clip.w / audio_clip.duration) % img_clip.w, 'center'))

#         # Composición del video con la imagen y el audio
#         video = CompositeVideoClip([img_clip], size=(1080, 1920)).set_duration(audio_clip.duration).set_audio(audio_clip)
#         clips.append(video)

#     final_clip = concatenate_videoclips(clips, method="compose")

#     # Cambiar el tamaño del video a 720x1280 para generarlo más rápido
#     final_clip = final_clip.resize(width=720, height=1280)
    
#     # Reducir la calidad del audio (bitrate)
#     audio_codec = 'aac'
#     audio_bitrate = '64k'  # Reducir el bitrate del audio para mayor rapidez

#     # Generar el video con menor FPS
#     final_clip.write_videofile(
#         output_filename, 
#         fps=24,  # Puedes bajar a 15 para mayor rapidez
#         codec='libx264', 
#         audio_codec=audio_codec, 
#         audio_bitrate=audio_bitrate, 
#         threads=4
#     )


def main():
    data = [{'url': 'https://www.kayak.com/rimg/himg/96/37/f6/leonardo-61201-156718556-840444.jpg', 'description': 'Un lujoso vestíbulo de hotel con columnas de mármol, elegantes candelabros, muebles modernos y una elegante área de bar en el fondo.'}, {'url': 'https://www.kayak.com/rimg/himg/26/3b/88/leonardo-61201-150608796-348102.jpg', 'description': 'Lujoso salón moderno con muebles elegantes, grandes ventanas y sofisticadas luminarias.'}, {'url': 'https://www.kayak.com/rimg/himg/7e/08/a2/leonardo-61201-150608800-357201.jpg', 'description': 'Bar moderno y elegante con iluminación ambiental, muebles elegantes y un mostrador bien surtido.'}, {'url': 'https://www.kayak.com/rimg/himg/b9/fe/97/leonardo-61201-175638799-708213.jpg', 'description': 'Habitaciones de hotel modernas y bien iluminadas con una cama grande, una chaise longue, un escritorio y un televisor de pantalla plana, decorada en tonos azules y blancos.'}, {'url': 'https://www.kayak.com/rimg/himg/8c/44/2a/leonardo-61201-150608726-212706.jpg', 'description': 'Baño lujoso con una encimera de mármol, una gran bañera y elegantes paredes de azulejos.'}, {'url': 'https://www.kayak.com/rimg/himg/0a/63/79/leonardo-61201-150608662-076980.jpg', 'description': 'Sala de estar moderna y elegantemente amueblada con una alfombra de patrones azules y blancos, un televisor grande y un dormitorio adyacente.'}, {'url': 'https://www.kayak.com/rimg/himg/1d/43/a7/leonardo-61201-161945129-589254.jpg', 'description': 'El vestíbulo moderno y elegante con un mostrador de recepción de mármol, un candelabro, dos sillones con cojines azules y grandes ventanas que ofrecen una vista de la vegetación exterior.'}, {'url': 'https://www.kayak.com/rimg/himg/34/16/a2/expedia_group-61201-426f25-766110.jpg', 'description': 'Lujoso salón decorado opulentamente con sofás de terciopelo púrpura, acentos dorados, cojines de estampado de leopardo, candelabros de cristal y un bar bien surtido.'}, {'url': 'https://www.kayak.com/rimg/himg/7b/8d/19/leonardo-61201-150608750-267125.jpg', 'description': 'Área de salón moderna y elegantemente decorada con un buffet, asientos cómodos, mesas adornadas con flores moradas y arte contemporáneo en la pared.'}, {'url': 'https://www.kayak.com/rimg/himg/f3/5b/ba/leonardo-61201-153565370-885773.jpg', 'description': 'Y  área de patio exterior bien mantenida con sillas de salón, una fuente y varias disposiciones de asientos rodeadas de vegetación y edificios altos en el fondo.'}]
    
    images, audios = process_images_and_audios(data)
    create_video(images, audios, "output_video.mp4")

if __name__ == "__main__":
    main()
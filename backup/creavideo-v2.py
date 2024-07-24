import requests
from moviepy.editor import *
import moviepy.video.fx.all as vfx
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

def get_polly_response(engine, voiceid, text, prosodyrate="100%"):
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
            polly_text = f'<speak><prosody rate="{prosodyrate}"><amazon:domain name="conversational">{text}</amazon:domain></prosody></speak>'
        else:
            polly_text = f'<speak><prosody rate="{prosodyrate}">{text}</prosody></speak>'
    else:
        raise ValueError("Invalid TextType")

    polly_client = boto3.Session(profile_name='doccumi', region_name="us-east-1").client("polly")
    
    print("get_polly_response:", polly_text, text_type, voiceid, language_code)
    
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
    response = get_polly_response("neural", voz, text, "100%")
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
    # data = data[:2]

    images = []
    audios = []

    for idx, item in enumerate(data):
        img_filename = f"image_{idx}.jpg"
        audio_filename = f"audio_{idx}.mp3"

        download_image(item["url"], img_filename)
        text_to_speech_polly(item["description"], audio_filename, "Joanna")

        images.append(img_filename)
        audios.append(audio_filename)

    return images, audios

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


def create_video(num_elements, output_filename):
    clips = []

    if num_elements < 2:
        raise ValueError("Debe haber al menos 2 elementos.")

    for i in range(0, num_elements, 2):
        # Leer los audios
        audio_clip1 = AudioFileClip(f"audio_{i}.mp3")
        audio_clip2 = AudioFileClip(f"audio_{i + 1}.mp3") if (i + 1) < num_elements else None

        # Duración combinada de los audios
        combined_duration = audio_clip1.duration + (audio_clip2.duration if audio_clip2 else 0)

        # Leer las imágenes
        img_clip1 = ImageClip(f"image_{i}.jpg").set_duration(combined_duration).resize(width=1080)
        img_clip2 = ImageClip(f"image_{i + 1}.jpg").set_duration(combined_duration) if audio_clip2 else None
        if img_clip2:
            img_clip2 = img_clip2.resize(width=1080)

        # Posicionar las imágenes
        img_clip1 = zoom_in_effect(img_clip1).set_position(("center", "top"))
        if img_clip2:
            img_clip2 = zoom_in_effect(img_clip2).set_position(("center", "bottom"))

        # Crear la escena con las imágenes y el audio
        if img_clip2:
            video = CompositeVideoClip([img_clip1, img_clip2], size=(1080, 1920)).set_duration(combined_duration)
            combined_audio = concatenate_audioclips([audio_clip1, audio_clip2]) if audio_clip2 else audio_clip1
            video = video.set_audio(combined_audio)
        else:
            video = CompositeVideoClip([img_clip1], size=(1080, 1920)).set_duration(combined_duration).set_audio(audio_clip1)

        clips.append(video)

    # Concatenar todas las escenas
    final_clip = concatenate_videoclips(clips, method="compose").resize(width=720, height=1280)
    
    # Cargar la imagen centralizada y establecer la duración total del video
    total_duration = final_clip.duration
    centered_img_clip = ImageClip("LuxuryRoamersHDTransparente.png").set_duration(total_duration)
    centered_img_clip = centered_img_clip.resize(width=final_clip.w * 0.9).set_position("center")
    
    # Superponer la imagen sobre el video final
    final_clip = CompositeVideoClip([final_clip, centered_img_clip])

    # Guardar el video final
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
    data = [{'url': 'https://www.kayak.com/rimg/himg/17/76/2c/booking-3989982-257263533-043832.jpg', 'description': 'A luxurious, well-lit house with arched windows, a grand entrance, and a gated courtyard surrounded by lush greenery and tall trees.'}, {'url': 'https://www.kayak.com/rimg/himg/97/73/c7/booking-3989982-257263588-299448.jpg', 'description': 'A grand staircase with ornate railings and statues leads to an upper level in an elegant, spacious interior with warm-toned walls and decorative elements.'}, {'url': 'https://www.kayak.com/rimg/himg/21/16/65/booking-3989982-257263572-216394.jpg', 'description': 'A spacious, well-lit kitchen with modern appliances, granite countertops, dark cabinetry, and an arched entryway leading to a grand hallway.'}, {'url': 'https://www.kayak.com/rimg/himg/50/e3/c8/booking-3989982-257263543-083612.jpg', 'description': 'A luxurious bedroom features a four-poster bed, a cozy seating area with ornate furniture, a large TV, and eclectic decor including a plush rug and animal figurines.'}, {'url': 'https://www.kayak.com/rimg/himg/f1/0f/8b/booking-3989982-257263555-150000.jpg', 'description': 'A cozy, well-decorated living room features a fireplace, elegant seating, framed artwork, and a floor lamp with multiple globes.'}, {'url': 'https://www.kayak.com/rimg/himg/36/10/ec/booking-3989982-257263552-131976.jpg', 'description': 'The image shows a luxurious bathroom featuring a large glass-enclosed shower and a separate bathtub area with arched windows and elegant tile work.'}, {'url': 'https://www.kayak.com/rimg/himg/14/cd/e2/booking-3989982-257263561-169186.jpg', 'description': 'A luxurious dining room with ornate furniture, a chandelier, medieval shields on the wall, and a classical statue in an alcove.'}, {'url': 'https://www.kayak.com/rimg/himg/8a/ee/e5/booking-3989982-257263570-205725.jpg', 'description': 'A serene pool area with a small waterfall, decorative bridge, and lush greenery under a purple-hued sky.'}, {'url': 'https://www.kayak.com/rimg/himg/ed/f0/4a/booking-3989982-257263582-272624.jpg', 'description': 'A serene outdoor spa area features a small pool with pink lighting, surrounded by tropical plants, a waterfall, and a classical statue under a pergola.'}, {'url': 'https://www.kayak.com/rimg/himg/13/93/3a/booking-3989982-257263567-188337.jpg', 'description': 'The image shows an outdoor patio area with a pergola, equipped with a ceiling fan, string lights, a barbecue grill, and metal patio furniture.'}]
    
    images, audios = process_images_and_audios(data)
    num_elements = len(images)
    create_video(num_elements, "output_video.mp4")

if __name__ == "__main__":
    main()
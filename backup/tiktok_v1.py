# import requests

# # Configura tus credenciales
# client_key = 'sbawvvmoh9wen4iy9t'
# client_secret = 'By54nIYiGeTuCxBZoIbH5nqBGAK9PFI8'

# redirect_uri = 'https://r3pmxssr-8012.use2.devtunnels.ms/'
# auth_code = '_BNe579gOO7trTziglyplBttGpXqNsrLvAnaSN4DJ1-OGHO_jz_vX1Wns5ZjKjIytaWKXxHxwv1c9-gzMrSiBM3TEXv2kOAEX26wMasbUb-tqEE6NY8ouLudCfRd7gUBOdEN0WdPulLlDirCb0CxEGAGUpr6NA8JMF9jWUniUWutYJokCNGrY0WJtdqmjA8vDac2gbljQpr8BPyAveOVQg*3!4679.va'

# # Paso 1: Obtener el access token
# token_url = 'https://open.tiktokapis.com/v2/oauth/token/'
# token_data = {
#     'client_key': client_key,
#     'client_secret': client_secret,
#     'code': auth_code,
#     'grant_type': 'authorization_code',
#     'redirect_uri': redirect_uri
# }
# token_response = requests.post(token_url, data=token_data)

# print(token_response.json())

# # access_token = token_response.json().get('data', {}).get('access_token')
# access_token = token_response.json().get('access_token')

# print("===========================")
# print(f"Access Token: {access_token}")
# print("===========================")

# if not access_token:
#     print("Error obteniendo el token de acceso")
#     exit()

# # # Paso 2: Obtener información del creador
# creator_info_url = 'https://open.tiktokapis.com/v2/post/publish/creator_info/query/'

# print("===========================")
# print(f"creator_info_url: {creator_info_url}")
# print("===========================")

# headers = {
#     'Authorization': f'Bearer {access_token}',
#     'Content-Type': 'application/json; charset=UTF-8'
# }

# print("===========================")
# print("headers 1:", headers)
# print("===========================")

# response = requests.post(creator_info_url, headers=headers)
# creator_info = response.json()
# print(creator_info)

# # Paso 3: Iniciar la subida del video
# video_init_url = 'https://open.tiktokapis.com/v2/post/publish/video/init/'
# post_info = {
#     "title": "Este será un video divertido de #gatos en tu @tiktok #fyp",
#     "privacy_level": "PUBLIC_TO_EVERYONE",
#     "disable_duet": False,
#     "disable_comment": False,
#     "disable_stitch": False,
#     "video_cover_timestamp_ms": 1000
# }
# source_info = {
#     "source": "FILE_UPLOAD",
#     "video_size": 22578376,  # Tamaño del video en bytes
#     "chunk_size": 10000000,  # Tamaño del chunk en bytes
#     "total_chunk_count": 2.2578376   # Número total de chunks
# }
# data = {
#     "post_info": post_info,
#     "source_info": source_info
# }

# print("===========================")
# print("headers 2:", headers)
# print("===========================")

# response = requests.post(video_init_url, headers=headers, json=data)
# upload_data = response.json()

# print("===========================")
# print("upload_data:", upload_data)
# print("===========================")

# upload_url = upload_data['data']['upload_url']
# publish_id = upload_data['data']['publish_id']

# print("===========================")
# print("upload_data:", upload_data)
# print("===========================")

# # Paso 4: Subir el video en chunks
# video_file_path = '/Users/omarmojica/proyectos/openai/python/t2yt/videos/5-Minute Morning Meditation With God - Transform Your Life.mp4'

# with open(video_file_path, 'rb') as video_file:
#     for chunk_index in range(source_info['total_chunk_count']):
#         chunk_start = chunk_index * source_info['chunk_size']
#         chunk_end = min(chunk_start + source_info['chunk_size'], source_info['video_size']) - 1
#         video_file.seek(chunk_start)
#         chunk_data = video_file.read(chunk_end - chunk_start + 1)
        
#         headers.update({
#             'Content-Type': 'video/mp4',
#             'Content-Range': f'bytes {chunk_start}-{chunk_end}/{source_info["video_size"]}'
#         })
        
#         upload_response = requests.put(upload_url, headers=headers, data=chunk_data)
#         print(upload_response.json())

# # Paso 5: Verificar el estado de la publicación
# status_url = 'https://open.tiktokapis.com/v2/post/publish/status/fetch/'
# status_data = {
#     'publish_id': publish_id
# }
# status_response = requests.post(status_url, headers=headers, json=status_data)
# print(status_response.json())


import requests
import time
import math

# Configura tus credenciales
client_key = 'sbawvvmoh9wen4iy9t'
client_secret = 'By54nIYiGeTuCxBZoIbH5nqBGAK9PFI8'
redirect_uri = 'https://r3pmxssr-5012.use2.devtunnels.ms/callback'
auth_code = '2ABMBdi1S7O84kUV2GHG6hzB2Bv10B1VCS7dst-7yGsHqzu4O3nUsV2tv1eGgNNegoHth4sCSgp9xA1I5pqL0ApbpXrP35e_qBoxEAjGhHqnBOVx4qRCkjVRXnYECAxQA_J6zqO1oXPUurNGCo544hy54qUNGRyj3u1tagpNRVc2FjvFFmea_TvtEU4CE-YTQ5DUDU3IFa1WuhOWKWucXLeakXm_-mRiyljbxBJJgoM*3!4687.va'

def get_tokens(auth_code):
    token_url = 'https://open.tiktokapis.com/v2/oauth/token/'
    token_data = {
        'client_key': client_key,
        'client_secret': client_secret,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache'
    }
    
    token_response = requests.post(token_url, data=token_data, headers=headers)

    print("===========================")
    print("token_response:", token_response.json())
    print("===========================")
    
    tokens = token_response.json()
    
    print("===========================")
    print("tokens:", tokens)
    print("===========================")
    
    return tokens.get('access_token'), tokens.get('refresh_token')

def refresh_access_token(refresh_token):
    token_url = 'https://open.tiktokapis.com/v2/oauth/token/'
    token_data = {
        'client_key': client_key,
        'client_secret': client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache'
    }
    token_response = requests.post(token_url, data=token_data, headers=headers)
    
    tokens = token_response.json()
    
    print("===========================")
    print(f"refresh_access_token tokens: {tokens}")
    print("===========================")

    return tokens.get('access_token'), tokens.get('refresh_token')

# Obtener el access_token y refresh_token
access_token, refresh_token = get_tokens(auth_code)

if not access_token:
    print("Error obteniendo el token de acceso")
    exit()

print("===========================")
print(f"access_token: {access_token}")
print("===========================")
print(f"refresh_token: {refresh_token}")
print("===========================")

# Simulación de la lógica de refresco del token cuando sea necesario
def ensure_fresh_access_token():
    global access_token, refresh_token
    if access_token_expired():  # Esta es una función simulada. Implementa tu lógica para verificar la expiración
        access_token, refresh_token = refresh_access_token(refresh_token)
        
        print("===========================")
        print(f"ensure_fresh_access_token access_token: {access_token}")
        print("===========================")
        print(f"ensure_fresh_access_token refresh_token: {refresh_token}")
        print("===========================")

def access_token_expired():
    # Simulación de la verificación de expiración del token
    # En producción, verifica la validez del token, podría ser almacenando su tiempo de expiración y comparándolo
    return False

# Asegúrate de tener un token fresco antes de cada solicitud
ensure_fresh_access_token()

# Paso 2: Obtener información del creador
creator_info_url = 'https://open.tiktokapis.com/v2/post/publish/creator_info/query/'
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json; charset=UTF-8'
}

response = requests.post(creator_info_url, headers=headers)
creator_info = response.json()

print("===========================")
print("creator_info:", creator_info)
print("===========================")

# Paso 3: Iniciar la subida del video
video_init_url = 'https://open.tiktokapis.com/v2/post/publish/video/init/'
post_info = {
    "title": "Este será un video divertido de #gatos en tu @tiktok #fyp",
    "privacy_level": "SELF_ONLY", #PUBLIC_TO_EVERYONE
    "disable_duet": False,
    "disable_comment": False,
    "disable_stitch": False,
    "video_cover_timestamp_ms": 1000
}

# Tamaño del archivo de video en bytes
video_size = 50000123  # Tamaño real del archivo de video
# Tamaño del fragmento (chunk) en bytes
chunk_size = 10000000  # TikTok recomienda 10MB

total_chunk_count = 5

print("===========================")
print("total_chunk_count:", total_chunk_count)
print("===========================")

source_info = {
    "source": "FILE_UPLOAD",
    "video_size": video_size,  # Tamaño del video en bytes
    "chunk_size": chunk_size,  # Tamaño del chunk en bytes
    "total_chunk_count": total_chunk_count   # Número total de chunks, redondeado al entero más cercano
}
data = {
    "post_info": post_info,
    "source_info": source_info
}

response = requests.post(video_init_url, headers=headers, json=data)
upload_data = response.json()

print("===========================")
print("upload_data:", upload_data)
print("===========================")

upload_url = upload_data['data']['upload_url']
publish_id = upload_data['data']['publish_id']

# Paso 4: Subir el video en chunks
video_file_path = '/Users/omarmojica/proyectos/openai/python/t2yt/videos/5-Minute Morning Meditation With God - Transform Your Life.mp4'

with open(video_file_path, 'rb') as video_file:
    for chunk_index in range(source_info['total_chunk_count']):
        chunk_start = chunk_index * source_info['chunk_size']
        chunk_end = min(chunk_start + source_info['chunk_size'], source_info['video_size']) - 1
        video_file.seek(chunk_start)
        chunk_data = video_file.read(chunk_end - chunk_start + 1)
        
        headers.update({
            'Content-Type': 'video/mp4',
            'Content-Range': f'bytes {chunk_start}-{chunk_end}/{source_info["video_size"]}'
        })
        
        upload_response = requests.put(upload_url, headers=headers, data=chunk_data)
        print(upload_response.json())

# Paso 5: Verificar el estado de la publicación
status_url = 'https://open.tiktokapis.com/v2/post/publish/status/fetch/'
status_data = {
    'publish_id': publish_id
}
status_response = requests.post(status_url, headers=headers, json=status_data)
print(status_response.json())

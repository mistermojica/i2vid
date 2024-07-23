import requests
import time
import os

try:
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
except Exception as err:
    print(err)
    
META_FB_PAGE_ID = os.environ.get("META_FB_PAGE_ID", "")
META_FB_API_VERSION = os.environ.get("META_FB_API_VERSION", "")
META_USER_ACCESS_TOKEN = os.environ.get("META_USER_ACCESS_TOKEN", "")

# Definir variables globales
api_version = META_FB_API_VERSION  # Por ejemplo, "v12.0"
page_id = META_FB_PAGE_ID  # ID de la página de Facebook
user_access_token = META_USER_ACCESS_TOKEN
video_url = "https://drive.usercontent.google.com/u/0/uc?id=1W2zgeR8G2yPnG9G4QV0TiwlNEbsWeCIm&export=download"  # URL del video que deseas subir

def get_page_info():
    url = f"https://graph.facebook.com/{api_version}/{page_id}"
    params = {
        "fields": "name,access_token,instagram_business_account",
        "access_token": user_access_token
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.json()}

def upload_video_to_ig(ig_user_id, page_access_token):
    url = f"https://graph.facebook.com/{api_version}/{ig_user_id}/media"
    params = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": "Hello World!",
        "share_to_feed": True,
        "access_token": page_access_token
    }
    
    response = requests.post(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.json()}

def check_video_status(ig_container_id, page_access_token):
    url = f"https://graph.facebook.com/{api_version}/{ig_container_id}"
    params = {
        "fields": "status_code,status",
        "access_token": page_access_token
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.json()}

def publish_video(ig_user_id, ig_container_id, page_access_token):
    url = f"https://graph.facebook.com/{api_version}/{ig_user_id}/media_publish"
    params = {
        "creation_id": ig_container_id,
        "access_token": page_access_token
    }
    
    response = requests.post(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.json()}

def main():
    # Obtener la información de la página
    page_info = get_page_info()
    
    print(page_info)
    
    if "error" in page_info:
        print("Error obteniendo la información de la página:", page_info["error"])
        return
    
    # Extraer el token de acceso de la página y el ID de la cuenta de Instagram
    page_access_token = page_info["access_token"]
    ig_user_id = page_info["instagram_business_account"]["id"]
    
    # Subir el video a Instagram Reels
    upload_response = upload_video_to_ig(ig_user_id, page_access_token)
    
    if "error" in upload_response:
        print("Error subiendo el video a Instagram:", upload_response["error"])
        return
    else:
        ig_container_id = upload_response.get("id")
        print("Video subido exitosamente. Comprobando estado...")
    
    # Verificar el estado del video subido cada 10 segundos
    while True:
        status_response = check_video_status(ig_container_id, page_access_token)
        
        if "error" in status_response:
            print("Error verificando el estado del video:", status_response["error"])
        else:
            print("Estado del video:", status_response)
            if status_response.get("status_code") == "FINISHED":
                print("El video ha sido subido exitosamente.")
                
                # Publicar el video en Instagram
                publish_response = publish_video(ig_user_id, ig_container_id, page_access_token)
                
                if "error" in publish_response:
                    print("Error publicando el video en Instagram:", publish_response["error"])
                else:
                    print("Video publicado exitosamente en Instagram:", publish_response)
                break
        
        time.sleep(10)  # Esperar 10 segundos antes de la siguiente verificación

# Ejecuta la función principal
main()

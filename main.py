import asyncio
import os
import requests
import json
import webbrowser
import time
import random
from openai import OpenAI
from playwright.async_api import async_playwright
from creavideo import create_video_main
from ig_uploader import upload_video_thread
import uuid
import threading
from flask import Flask, request, jsonify, render_template, send_from_directory, render_template_string
from loguru import logger
from PIL import Image
from datetime import datetime, timezone
from tinydb import TinyDB, Query

try:
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
except Exception as err:
    print(err)

import builtins

original_print = print
def omprint(*args, **kwargs):
    logger.info(" ".join(map(str, args)))
    original_print(*args, **kwargs)

builtins.print = omprint

PUBLIC_FOLDER = 'public'

PORT = os.environ.get("PORT", "")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

openai = OpenAI()

openai.api_key = OPENAI_API_KEY


async def download_image(url, download_path, filename):
    img_name = os.path.join(download_path, str(filename) + os.path.splitext(os.path.basename(url))[1])

    with open(img_name, 'wb') as f:
        f.write(requests.get(url).content)

    print(f'Descargada: {img_name}')
    return url  # Retornar la URL de la imagen descargada


async def scroll_down_in_div(page, div_selector, times=5, delay=3000):
    # Scroll down the specified div by simulating mouse wheel scroll.
    for _ in range(times):
        print("BAJANDO")
        await page.hover(div_selector)
        await page.mouse.wheel(0, 500)
        await page.wait_for_timeout(delay)


async def extract_property_data(url):
    property_image_urls = []

    async with async_playwright() as p:
        # Inicializar el navegador en modo headless
        browser = await p.firefox.launch(headless=True)  # Cambia a True si no necesitas ver el navegador
        page = await browser.new_page()

        # Navegar a la URL
        await page.goto(url)

        # Esperar que el contenedor 'c3xth-title' esté presente
        await page.wait_for_selector(".c3xth-title h1")

        property_name = await page.text_content(".c3xth-title h1")

        try:
            # Intenta hacer clic en el botón en inglés
            await page.get_by_role("button", name="View all photos").click()
        except:
            try:
                # Si no encuentra el botón en inglés, intenta hacer clic en el botón en español
                await page.get_by_role("button", name="Ver todas las fotos").click()
            except:
                print("No se encontró el botón en ninguno de los dos idiomas.")

        # Esperar que el contenedor 'AGBC-carousel-container' esté presente
        await page.wait_for_selector('div.AGBC-carousel-container')

        # Obtener las etiquetas <img> dentro del contenedor 'AGBC-carousel-container'
        carousel_div = await page.query_selector('div.AGBC-carousel-container')
        print("carousel_div:", carousel_div)
        img_elements = await carousel_div.query_selector_all('img.f800-image')
        print("img_elements:", img_elements)

        for img in img_elements:
            src = await img.get_attribute('src')
            print("src:", src)
            if src:
                full_url = f"https://www.kayak.com{src.split('.jpg')[0]}.jpg"
                print("full_url:", full_url)
                if full_url.endswith('.jpg'):
                    property_image_urls.append(full_url)

        # Cerrar el navegador
        await browser.close()

        property_data = {
            "property_name": property_name,
            "property_image_urls": property_image_urls
        }

        # print(property_data)

    return property_data


async def extract_property_data_trulia(url):
    # Crear la carpeta de descarga si no existe
    image_urls = []
    image_urls_network = []

    async with async_playwright() as p:
        # Inicializar el navegador en modo headless
        browser = await p.chromium.launch(headless=False)  # Cambia a True si no necesitas ver el navegador
        page = await browser.new_page()

        # # Función para manejar las respuestas de la red
        # async def handle_response(response):
        #     if response.request.resource_type == "image":
        #         image_urls_network.append(response.url)

        # Función para manejar las respuestas de la red
        async def handle_response(response):
            if response.request.resource_type == "image" and response.url.endswith(".jpg"):
                request = response.request
                frame = request.frame
                if frame:
                    img_elements = await frame.query_selector_all(f'img[src="{response.url}"]')
                    for img in img_elements:
                        large_attr = await img.get_attribute('large')
                        if large_attr:
                            image_urls.append(response.url)
                            break

        # Añadir un manejador para capturar las respuestas de la red
        page.on("response", handle_response)

        # Navegar a la URL
        await page.goto(url)

       # Esperar que el contenedor 'grid-gallery' esté presente
        await page.wait_for_selector('div[data-testid="grid-gallery"]')

        # Hacer scroll down en el div hasta el final
        await scroll_down_in_div(page, 'div[data-testid="grid-gallery"]', times=7, delay=2000)  # Ajusta el número de veces y el retraso según sea necesario

        # Obtener las etiquetas <picture> dentro del contenedor 'grid-gallery'
        gallery_div = await page.query_selector('div[data-testid="grid-gallery"]')
        pictures = await gallery_div.query_selector_all('picture')

        print("pictures:", len(pictures))
        
        picture = pictures[0]

        await picture.click()
        await page.wait_for_timeout(1000)
        
        counter = 0

        # Navegar por todas las imágenes usando el botón "Next image"
        next_button_selector = 'button[data-testid="media-next-button"]'
        while True:
            try:
                # Verificar si hemos descargado todas las imágenes
                if counter >= len(pictures):
                    break
                
                # Esperar a que el botón "Next image" esté presente y hacer clic
                next_button = await page.query_selector(next_button_selector)
                await next_button.click()
                await page.wait_for_timeout(1000)  # Esperar a que la siguiente imagen se cargue

                # Descargar la siguiente imagen
                img = await page.query_selector('img[data-testid^="media-carousel-image-"]')
                img_url = await img.get_attribute('large')
                if img_url:
                    image_urls.append(img_url)
                    counter += 1
            except:
                # Si no hay más imágenes, salir del bucle
                break

        # Cerrar el modal
        # await page.click('button[aria-label="Close"]')
        # await page.wait_for_timeout(1000)  # Esperar a que el modal se cierre

        # Cerrar el navegador
        await browser.close()
        
        print("image_urls_network:", image_urls_network)
    
    return image_urls


def analyze_single_image(image_url):
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": 'Analyze and describe what you see in this image in a single sentence, using language that allows sentences to interconnect and form a cohesive script, avoiding starting with articles like "a" or "an."',
                },
                {
                    "type": "image_url",
                    "image_url": {"url": image_url},
                },
            ],
        }
    ]

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.0,
    )

    description = response.choices[0].message.content.strip()
    return description


def analyze_images(image_urls, property_type, property_name, language, number_images, max_retries=7):
    analyzed_images = []
    
    for url in image_urls:
        attempt = 0
        success = False
        while not success and attempt < max_retries:
            try:
                description = analyze_single_image(url)
                imgdesc = {"url": url, "description": description}
                print("--------------------------------------------")
                print(imgdesc)
                print("--------------------------------------------")
                analyzed_images.append(imgdesc)
                success = True
            except Exception as e:
                attempt += 1
                print(f"Error on attempt {attempt} for URL {url}: {e}")
                time.sleep(1)  # Esperar un poco antes de reintentar
                
        if not success:
            raise Exception(f"Failed to analyze image after {max_retries} attempts for URL {url}")

    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": f"You are a useful virtual assistant who selects the best images that represent all the comforts of staying at the hotel, villa or property: {property_name}",
                },
            ],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Based on the descriptions in this array [{analyzed_images}], select the {number_images} images that best represent and cover all areas of a '{property_type}' at the '{property_name}', starting from the front and ending with the back if there is one. Return a JSON with a main property called 'selected_images' containing an array of objects, each with the URL and description in {language} of the selected images. The descriptions should be written in the style of a promotional video script to promote the sale or rental of the property where each description is part of a main script. Highlight the features of each space in a way that invites people to want to stay at this location. IMPORTANT: At the end of the last description, include a call to action inviting viewers to follow the account '@LuxuryRoamers' for more content like this.",
                },
            ],
        }
    ]

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.0,
        response_format={"type": "json_object"}
    )

    result = response.choices[0].message.content

    return json.loads(result)


def clear_directory(directory_path):
    # Elimina todos los archivos en la carpeta especificada.
    if os.path.exists(directory_path):
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    print(f'Eliminada: {file_path}')
            except Exception as e:
                print(f'Error al eliminar {file_path}: {e}')


def generate_html(images):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Image Gallery</title>
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .gallery img.thumbnail {
                width: 150px;
                cursor: pointer;
            }
            .modal-lg {
                max-width: 80%;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="my-4">Image Gallery</h1>
            <div class="row gallery">
    """

    for idx, image in enumerate(images):
        html_content += f"""
                <div class="col-md-6 mb-4">
                    <img src="{image['url']}" alt="{image['description']}" class="thumbnail" data-toggle="modal" data-target="#imageModal{idx}">
                    <p>{image['description']}</p>
                </div>

                <!-- Modal -->
                <div class="modal fade" id="imageModal{idx}" tabindex="-1" role="dialog" aria-labelledby="imageModalLabel{idx}" aria-hidden="true">
                    <div class="modal-dialog modal-lg" role="document">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="imageModalLabel{idx}">{image['description']}</h5>
                                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                    <span aria-hidden="true">&times;</span>
                                </button>
                            </div>
                            <div class="modal-body">
                                <img src="{image['url']}" class="img-fluid" alt="{image['description']}">
                            </div>
                        </div>
                    </div>
                </div>
        """

    html_content += """
            </div>
        </div>

        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.2/dist/umd/popper.min.js"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    </body>
    </html>
    """
    
    return html_content


def save_html_to_file(html_content, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html_content)


def open_html_in_browser(file_path):
    absolute_path = os.path.abspath(file_path)
    webbrowser.open(f"file://{absolute_path}")


async def download_images(selected_images, download_path):
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    filename = 0
    for image in selected_images:
        filename = filename + 1
        img_downloaded = await download_image(image["url"], download_path, filename)
        print("Imagen descargada:", img_downloaded)
    

def send_vehicle_data_to_instagram(ctx):
    # Extraer los valores del objeto ctx
    vehDueno = ctx.get("vehDueno", "Unknown Owner")
    arrFotosVehiculos = ctx.get("arrFotosVehiculos", [])
    vehMarca = ctx.get("vehMarca", "Unknown Brand")
    vehModelo = ctx.get("vehModelo", "Unknown Model")
    vehAnoFabricacion = ctx.get("vehAnoFabricacion", 0)
    vehTipoVehiculo = ctx.get("vehTipoVehiculo", "Unknown Type")
    vehColor = ctx.get("vehColor", "Unknown Color")
    vehTipoEmision = ctx.get("vehTipoEmision", "Unknown Fuel")
    vehLocation = ctx.get("vehLocation", "Unknown Location")

    # Construir el cuerpo de la solicitud
    data = {
        "dueno": vehDueno,
        "to": "instagram",
        "images": arrFotosVehiculos,
        "caption": f"{vehMarca} {vehModelo} {vehAnoFabricacion}\r\nTipo: {vehTipoVehiculo}\r\nColor: {vehColor}\r\nCombustible: {vehTipoEmision}\r\nPrecio: ${random.randint(10000, 40000)}",
        "location": vehLocation,
        "year": vehAnoFabricacion,
        "brand": vehMarca,
        "model": vehModelo,
        "show": True
    }

    print(data)

    # Realizar la solicitud POST
    response = requests.post("http://localhost:3002/publish", json=data)

    # Comprobar el estado de la respuesta
    if response.status_code == 200:
        print("Solicitud enviada con éxito.")
    else:
        print(f"Error al enviar la solicitud: {response.status_code}")
        print(response.text)


def upload_video(video_url, cover_url, property_name):
    # video_url = "https://videos.pexels.com/video-files/10780729/10780729-hd_1080_1920_30fps.mp4"
    video_type = "REELS"
    caption = f"{property_name}\n\nFollow @luxuryroamers for more!!!\n\n#luxuryroamers #luxuryhomes #luxuryproperties #luxurytravelers"
    share_to_feed = True

    def callback(response):
        print(response)
    
    # Crear y empezar el hilo
    thread = threading.Thread(target=upload_video_thread, args=(video_url, cover_url, video_type, caption, share_to_feed, callback))
    thread.start()


# Definir la función para ejecutar el servidor HTTP
# def run_http_server(port, directory):
#     class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
#         def translate_path(self, path):
#             # Redirigir todas las solicitudes al directorio especificado
#             path = super().translate_path(path)
#             return path.replace(self.directory, directory, 1)

#     Handler = SimpleHTTPRequestHandler
#     Handler.directory = directory

#     with socketserver.TCPServer(("", port), Handler) as httpd:
#         print(f"Serving at port {port}")
#         httpd.serve_forever()

def run_http_server(port, directory):
    from http.server import SimpleHTTPRequestHandler, HTTPServer
    os.chdir(directory)
    httpd = HTTPServer(('localhost', port), SimpleHTTPRequestHandler)
    httpd.serve_forever()


async def main(uuid4, url, language, voice, property_type, property_name_param, number_images):
    # Registrar el tiempo de inicio
    start_time = time.time()
    
    # Iniciar el servidor HTTP en un hilo separado
    directory = f'./{PUBLIC_FOLDER}'
    
    # url = 'https://www.trulia.com/home/282-s-95th-pl-chandler-az-85224-8207993?mid=0#lil-mediaTab'
    # url = 'https://www.trulia.com/builder-community-plan/Prestwick-Place-Huxley-2059141968?mid=0#lil-mediaTab'
    # url = 'https://www.kayak.com/hotels/The-Ritz-Carlton,San-Francisco,San-Francisco-p61403-h61201-details/2024-07-12/2024-07-19/2adults?psid=lBCEPnMis_&pm=daytaxes'
    # url = 'https://www.es.kayak.com/hotels/Villa-Gordal,Enormous-Villa-in-Las-Vegas-with-39-Sleeps,Las-Vegas-p61746-h3989982-details/2024-07-26/2024-07-31/2adults?psid=mRCEN4ta-l&pm=daybase'
    
    download_path = f'{directory}/{uuid4}'

    # Llamar a la función para borrar el contenido de la carpeta
    clear_directory(download_path)

    property_data = await extract_property_data(url)
    
    property_name = property_name_param or property_data["property_name"]

    property_image_urls = property_data["property_image_urls"]
    
    property_image_urls = property_image_urls[:number_images]

    print("Descarga completada.")

    print("====================")

    # property_image_urls = ['https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/91b73fe2202021a2964bb36b97249994-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/9f258c8f5ab68db6f4abc4d8e6f54447-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/3daf76584f9a9ce0965e63b9f600b56e-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/ff07e11caf675d5900542e2c8b0b2c49-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/51db899f3696572be90400c9486e26a7-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/0dd699514704fe97b7d287511ea89937-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/0ba415d329ced58f770b4de172458c18-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/ecd7de4af79221a1fdd11fd760cecbe1-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/47b97b89cea4b767c7fea7dad8325021-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/d4cc71fe120b3f57123abba22991b643-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/f3d8607693c1bb75a9d8d328438872ed-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/ea0bf10dd83246bc0c4d2f17dd0ed107-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/f749e6cafb9a971ea47870e447fc2a5e-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/14473d500e54d26ed87cb6e53ed9f9ac-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/2018635f31062e62d573a73f3b8e1cfa-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/e96aca746f5eacccd5d0615e01314ae6-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/15253619ac86b3012d9467905460b182-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/1bdd1dee728812806bc9be4f3f7f0cbb-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/093281b2d7462d627684db67d8538e1b-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/ef875ee1433d4cf70b6fbeb4a85f80c7-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/13a17d467b281ed2f4329ca096d7b37b-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/d47be64a6414e63d068f0624fc9b06fd-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/583a66a622ded9e574f29a7c0f558262-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/efb4d1793f991b10fe949853b5a33072-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/5ad9664ebcc35cd79e855d7ec999a5b5-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/6daaf60805e5712c489683be9288d155-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/edb08b6549d501713b06f25eddd7a6ef-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/85eb744d137483a6c7e72d6069431506-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/879acf110c91a5bfd581daa023b79339-full.jpg']
    
    print("property_image_urls:", property_image_urls)
    
    print("====================")

    # property_type = "villa accommodation"

    # property_name = "Villa Gordal, Las Vegas"

    response = analyze_images(property_image_urls, property_type, property_name, language, number_images) #[:5]

    selected_images = response["selected_images"]
    
    print("selected_images:", selected_images)
    
    print("====================")

    # await download_images(selected_images, download_path)

    # print(response)

    print("====================")

    # Generar el contenido HTML
    html_content = generate_html(selected_images)

    # Ruta donde se guardará el archivo HTML
    file_path = 'image_gallery.html'

    # Guardar el contenido HTML en un archivo
    save_html_to_file(html_content, file_path)

    # Abrir el archivo HTML en el navegador
    open_html_in_browser(file_path)

    print("====================")
    
    # selected_images = [{'url': 'https://www.kayak.com/rimg/himg/96/37/f6/leonardo-61201-156718556-840444.jpg', 'description': 'Un lujoso vestíbulo de hotel con columnas de mármol, elegantes candelabros, muebles modernos y una elegante área de bar en el fondo.'}, {'url': 'https://www.kayak.com/rimg/himg/26/3b/88/leonardo-61201-150608796-348102.jpg', 'description': 'Un lujoso salón moderno con muebles elegantes, grandes ventanas y sofisticadas luminarias.'}, {'url': 'https://www.kayak.com/rimg/himg/7e/08/a2/leonardo-61201-150608800-357201.jpg', 'description': 'Un bar moderno y elegante con iluminación ambiental, muebles elegantes y un mostrador bien surtido.'}, {'url': 'https://www.kayak.com/rimg/himg/b9/fe/97/leonardo-61201-175638799-708213.jpg', 'description': 'Una habitación de hotel moderna y bien iluminada con una cama grande, una chaise longue, un escritorio y un televisor de pantalla plana, decorada en tonos azules y blancos.'}, {'url': 'https://www.kayak.com/rimg/himg/8c/44/2a/leonardo-61201-150608726-212706.jpg', 'description': 'Un baño lujoso con una encimera de mármol, una gran bañera y elegantes paredes de azulejos.'}, {'url': 'https://www.kayak.com/rimg/himg/0a/63/79/leonardo-61201-150608662-076980.jpg', 'description': 'Una sala de estar moderna y elegantemente amueblada con una alfombra de patrones azules y blancos, un televisor grande y un dormitorio adyacente.'}, {'url': 'https://www.kayak.com/rimg/himg/1d/43/a7/leonardo-61201-161945129-589254.jpg', 'description': 'El vestíbulo moderno y elegante con un mostrador de recepción de mármol, un candelabro, dos sillones con cojines azules y grandes ventanas que ofrecen una vista de la vegetación exterior.'}, {'url': 'https://www.kayak.com/rimg/himg/34/16/a2/expedia_group-61201-426f25-766110.jpg', 'description': 'Un lujoso salón decorado opulentamente con sofás de terciopelo púrpura, acentos dorados, cojines de estampado de leopardo, candelabros de cristal y un bar bien surtido.'}, {'url': 'https://www.kayak.com/rimg/himg/7b/8d/19/leonardo-61201-150608750-267125.jpg', 'description': 'Un área de salón moderna y elegantemente decorada con un buffet, asientos cómodos, mesas adornadas con flores moradas y arte contemporáneo en la pared.'}, {'url': 'https://www.kayak.com/rimg/himg/f3/5b/ba/leonardo-61201-153565370-885773.jpg', 'description': 'Un área de patio exterior bien mantenida con sillas de salón, una fuente y varias disposiciones de asientos rodeadas de vegetación y edificios altos en el fondo.'}]

    # ctx = {
    #     "vehDueno": "John Doe",
    #     "arrFotosVehiculos": selected_images,
    #     "vehMarca": "Toyota",
    #     "vehModelo": "Corolla",
    #     "vehAnoFabricacion": 2021,
    #     "vehTipoVehiculo": "Sedán",
    #     "vehColor": "Rojo",
    #     "vehTipoEmision": "Gasolina",
    #     "vehLocation": "Santo Domingo"
    # }

    uploaded_video = f"{download_path}/videos/{uuid4}.mp4"

    create_video_main(selected_images, uploaded_video, voice, download_path, uuid4, property_name)

    # send_vehicle_data_to_instagram(ctx)
    
    server_url = f"https://i2vid.luxuryroamers.com"
    video_to_upload = f'{server_url}/{uuid4}/videos/{uuid4}.mp4'
    cover_url = f'{server_url}/{uuid4}/thumbnail/{uuid4}.jpg'
    
    print("video_to_upload:", video_to_upload)

    upload_video(video_to_upload, cover_url, property_name)
    
    # Registrar el tiempo de finalización
    end_time = time.time()
    
    # Calcular el tiempo de ejecución
    execution_time = end_time - start_time
    
    print(f"El script tomó {execution_time:.2f} segundos en ejecutarse.")
    
    return {"execution_time": execution_time}


app = Flask(__name__, static_folder=PUBLIC_FOLDER)

# Initialize TinyDB
db = TinyDB('luxuryroamers.json')
procesos_table = db.table('procesos')

process_lock = threading.Lock()

def save_to_db(process_id, url, language, voice, property_type, property_name, number_images):
    timestamp = datetime.now(timezone.utc).isoformat()
    proceso = {
        "uuid": process_id,
        "url": url,
        "language": language,
        "voice": voice,
        "property_type": property_type,
        "property_name": property_name,
        "number_images": number_images,
        "url_video": "",
        "fecha_creacion": timestamp,
        "fecha_modificacion": timestamp,
        "estado": "pendiente"
    }
    procesos_table.insert(proceso)
    return process_id


def update_process_status(process_id, status):
    url_video = f'https://llfgcl66-{PORT}.use2.devtunnels.ms/{process_id}/videos/{process_id}.mp4'
    Process = Query()
    procesos_table.update(
        {
            "estado": status, 
            "fecha_modificacion": datetime.now(timezone.utc).isoformat(),
            "url_video": url_video
        }, Process.uuid == process_id)


def delete_process(process_id):
    Process = Query()
    procesos_table.remove(Process.uuid == process_id)


def get_pending_processes():
    return procesos_table.search(Query().estado == 'pendiente')


def process_pending_tasks():
    if not process_lock.acquire(blocking=False):
        print("Ya hay un proceso en ejecución.")
        return
    
    try:
        while True:
            pending_processes = get_pending_processes()
            print("pending_processes:", pending_processes)
            if not pending_processes:
                print("No hay más procesos pendientes.")
                break

            for process in sorted(pending_processes, key=lambda x: x['fecha_creacion']):
                process_id = process['uuid']
                print(f"Ejecutando el proceso ID: {process_id}")
                try:
                    asyncio.run(main(
                        process['uuid'],
                        process['url'],
                        process['language'],
                        process['voice'],
                        process['property_type'],
                        process['property_name'],
                        process['number_images']
                    ))
                    update_process_status(process_id, 'completado')
                except Exception as e:
                    update_process_status(process_id, f'error: {e}')
                    print(f"Error al procesar el proceso ID: {process_id}, error: {e}")

            time.sleep(5)  # Espera antes de verificar nuevamente
    finally:
        process_lock.release()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process_request():
    data = request.json
    url = data.get('url')
    language = data.get('language', 'English')
    voice = data.get('voice', 'Joanna')
    property_type = data.get('property_type')
    property_name = data.get('property_name')
    number_images = int(data.get('number_images'))

    if not url or not property_type:
        return jsonify({"error": "Missing required parameters"}), 400

    process_id = str(uuid.uuid4())

    logger.add(f"./logs/file_{process_id}.log", rotation="1 day")

    save_to_db(process_id, url, language, voice, property_type, property_name, number_images)

    # Trigger the process_pending_tasks function
    threading.Thread(target=process_pending_tasks).start()

    return jsonify({"message": "Proceso registrado exitosamente.", "process_id": process_id}), 200


@app.route('/<path:path>', methods=['GET'])
def serve_file_or_directory(path):
    full_path = os.path.join(app.static_folder, path)
    if os.path.isdir(full_path):
        files = os.listdir(full_path)
        file_list_html = "<h1>Directory listing for {}</h1><ul>".format(path)
        for file in files:
            file_url = os.path.join(request.path, file)
            file_list_html += f"<li><a href='{file_url}'>{file}</a></li>"
        file_list_html += "</ul>"
        return render_template_string(file_list_html)
    else:
        return send_from_directory(app.static_folder, path)


@app.route('/properties', methods=['GET'])
def list_videos():
    video_files = []

    # Obtener todos los registros de la base de datos
    all_processes = procesos_table.all()

    # Filtrar solo los registros que tienen un url_video y estado 'completado'
    for process in all_processes:
        if 'url_video' in process and (process['estado'] == 'completado' or process['estado'] == 'pendiente'):
            video_files.append({
                "process_id": process['uuid'],
                "filename": process['url_video'],
                "modified": process['fecha_modificacion'],
                "status": process['estado']
            })

    # Ordenar los archivos por tiempo de modificación en orden descendente
    video_files.sort(key=lambda x: x["modified"], reverse=True)
    
    return jsonify(video_files)


@app.route('/properties/<process_id>', methods=['DELETE'])
def delete_process_endpoint(process_id):
    try:
        delete_process(process_id)
        return jsonify({"message": "Process deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def start_process_monitor():
    while True:
        process_pending_tasks()
        time.sleep(60)  # Esperar 1 minuto antes de verificar nuevamente


if __name__ == '__main__':
    print(f"--------------------------------------------")
    print(f"Servidor Flask corriendo en el puerto {PORT}")
    print(f"--------------------------------------------")
    threading.Thread(target=start_process_monitor).start()  # Iniciar el monitor de procesos en segundo plano
    app.run(host='0.0.0.0', port=PORT)

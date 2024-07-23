import asyncio
import os
import requests
import json
from openai import OpenAI
from playwright.async_api import async_playwright

try:
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
except Exception as err:
    print(err)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

openai = OpenAI()

openai.api_key = OPENAI_API_KEY

async def download_image(url, download_path):
    img_name = os.path.join(download_path, os.path.basename(url))
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


async def extract_images(url, download_path):
    # Crear la carpeta de descarga si no existe
    image_urls = []

    if not os.path.exists(download_path):
        os.makedirs(download_path)

    async with async_playwright() as p:
        # Inicializar el navegador en modo headless
        browser = await p.chromium.launch(headless=False)  # Cambia a True si no necesitas ver el navegador
        page = await browser.new_page()

        # Navegar a la URL
        await page.goto(url)

        # Esperar que el contenedor 'grid-gallery' esté presente
        await page.wait_for_selector('div[data-testid="grid-gallery"]')

        # Hacer scroll down en el div hasta el final
        await scroll_down_in_div(page, 'div[data-testid="grid-gallery"]', times=7, delay=2000)  # Ajusta el número de veces y el retraso según sea necesario

        # Obtener las etiquetas <picture> dentro del contenedor 'grid-gallery'
        gallery_div = await page.query_selector('div[data-testid="grid-gallery"]')
        pictures = await gallery_div.query_selector_all('picture')

        print("pictures:", pictures, len(pictures))
        
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
                    img_url_returned = await download_image(img_url, download_path)
                    image_urls.append(img_url_returned)
                    counter += 1
            except:
                # Si no hay más imágenes, salir del bucle
                break

        # Cerrar el modal
        # await page.click('button[aria-label="Close"]')
        # await page.wait_for_timeout(1000)  # Esperar a que el modal se cierre

        # Cerrar el navegador
        await browser.close()
    
    return image_urls


def analyze_single_image(image_url):
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Analyze and return what you see in this image in a single sentence.",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": image_url},
                },
            ],
        }
    ]

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.0,
    )

    description = response.choices[0].message.content.strip()
    return description


def analyze_images(image_urls):
    analyzed_images = []
    for url in image_urls:
        description = analyze_single_image(url)
        imgdesc = {"url": url, "description": description}
        print(imgdesc)
        analyzed_images.append(imgdesc)

    # Ahora envía el nuevo arreglo a OpenAI para seleccionar las 10 mejores imágenes
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Based on the provided descriptions [{analyzed_images}], choose the 10 images that best represent and cover all areas of the property, starting with the front and ending with the back if there is one. Return an array of url and description in JSON format with the chosen descriptions and urls.",
                },
                # *analyzed_images,
            ],
        }
    ]

    print(messages)

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.0,
        response_format={"type": "json_object"}
    )

    result = response.choices[0].message.content

    return json.loads(result)


# def analyze_images(image_urls):

#     messages = [
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "text",
#                     "text": f"Almacena en memoria todos estos url de imágenes {image_urls}. Analiza lo que ves en cada imagen provista en los parámetros 'image_url', luego en base a lo que viste en las imágenes elije las 10 imágenes que mejor representen y cubran todas las áreas de la propiedad, comenzando por el frente y terminando por la parte trasera si la hay. En tu respuesta agrega el url original que recibiste en el parámetro 'image_url' de cada imagen al lado de lo que viste en la imagen. Solo retorna las 10 imágenes que mejor cubran todos los espacios de la propiedad.",
#                     # "text": f"Almacena en memoria todos estos url de imágenes {image_urls}. Elije las 10 imágenes que mejor representen y cubran todas las áreas de la propiedad, comenzando por el frente y terminando por la parte trasera si la hay. Devuelve una matriz en formato JSON con las URLs originales de las 10 imágenes elegidas y la razón de su elección. ",
#                     # "text": "Choose the 10 images that best represent the property and cover all areas of the property, starting with the front and ending with the back if there is one. Return an arrah in JSON format with the original urls sent to you of your 10 images chosen.",
#                 }
#             ] + [
#                 {
#                     "type": "image_url",
#                     "image_url": {"url": url},
#                 }
#                 for url in image_urls
#             ],
#         }
#     ]

#     print(messages)

#     response = openai.chat.completions.create(
#         model="gpt-4o",
#         messages=messages,
#         temperature=0.0,
#         # response_format={"type": "json_object"}
#     )

#     respuesta = response.choices[0].message.content

#     # respuesta_arreglo = json.loads(respuesta)

#     return respuesta


def clear_directory(directory_path):
    """
    Elimina todos los archivos en la carpeta especificada.
    """
    if os.path.exists(directory_path):
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    print(f'Eliminada: {file_path}')
            except Exception as e:
                print(f'Error al eliminar {file_path}: {e}')


async def main():
    # url = 'https://www.trulia.com/home/282-s-95th-pl-chandler-az-85224-8207993?mid=0#lil-mediaTab'
    url = 'https://www.trulia.com/home/14277-sw-177th-st-miami-fl-33177-44340096?mid=0#lil-mediaTab'
    download_path = 'imagenes_trulia'

    # Llamar a la función para borrar el contenido de la carpeta
    clear_directory(download_path)

    # image_urls = await extract_images(url, download_path)
    print("Descarga completada.")

    print("====================")

    image_urls = ['https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/91b73fe2202021a2964bb36b97249994-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/9f258c8f5ab68db6f4abc4d8e6f54447-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/3daf76584f9a9ce0965e63b9f600b56e-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/ff07e11caf675d5900542e2c8b0b2c49-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/51db899f3696572be90400c9486e26a7-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/0dd699514704fe97b7d287511ea89937-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/0ba415d329ced58f770b4de172458c18-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/ecd7de4af79221a1fdd11fd760cecbe1-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/47b97b89cea4b767c7fea7dad8325021-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/d4cc71fe120b3f57123abba22991b643-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/f3d8607693c1bb75a9d8d328438872ed-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/ea0bf10dd83246bc0c4d2f17dd0ed107-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/f749e6cafb9a971ea47870e447fc2a5e-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/14473d500e54d26ed87cb6e53ed9f9ac-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/2018635f31062e62d573a73f3b8e1cfa-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/e96aca746f5eacccd5d0615e01314ae6-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/15253619ac86b3012d9467905460b182-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/1bdd1dee728812806bc9be4f3f7f0cbb-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/093281b2d7462d627684db67d8538e1b-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/ef875ee1433d4cf70b6fbeb4a85f80c7-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/13a17d467b281ed2f4329ca096d7b37b-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/d47be64a6414e63d068f0624fc9b06fd-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/583a66a622ded9e574f29a7c0f558262-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/efb4d1793f991b10fe949853b5a33072-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/5ad9664ebcc35cd79e855d7ec999a5b5-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/6daaf60805e5712c489683be9288d155-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/edb08b6549d501713b06f25eddd7a6ef-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/85eb744d137483a6c7e72d6069431506-full.jpg', 'https://www.trulia.com/pictures/thumbs_5/zillowstatic/fp/879acf110c91a5bfd581daa023b79339-full.jpg']
    print("URLs de las imágenes:", image_urls)

    print("====================")

    response = analyze_images(image_urls) #[:5]
    print(response)

    print("====================")


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import os
import requests
from playwright.async_api import async_playwright

def get_media_resolution(media):
    """
    Extract the resolution from the media attribute.
    """
    if not media:
        return 0
    if 'min-width' in media:
        width_str = media.split('min-width:')[1].split('px')[0]
        try:
            return int(width_str)
        except ValueError:
            return 0
    return 0

async def scroll_down_in_div(page, div_selector, times=5, delay=3000):
    """
    Scroll down the specified div by simulating mouse wheel scroll.
    """
    for _ in range(times):
        print("BAJANDO")
        await page.hover(div_selector)
        await page.mouse.wheel(0, 500)
        await page.wait_for_timeout(delay)
        
        # await page.eval_on_selector(div_selector, 'div => div.scrollBy(0, 1000)')
        # await page.wait_for_timeout(delay)

async def extract_images(url, download_path):
    # Crear la carpeta de descarga si no existe
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    async with async_playwright() as p:
        # Inicializar el navegador en modo headless
        browser = await p.firefox.launch(headless=False)  # Cambia a True si no necesitas ver el navegador
        page = await browser.new_page()

        # Navegar a la URL
        await page.goto(url)

        # Verificar si el elemento "Press & Hold" está presente
        # try:
        #     await page.wait_for_selector('text="Press & Hold"', timeout=10000)  # Espera 10 segundos
        #     print("El elemento 'Press & Hold' está presente. No se puede proceder.")
        #     return
        # except:
        #     print("El elemento 'Press & Hold' no está presente. Procediendo con la descarga de imágenes.")

        # Esperar que el contenedor 'grid-gallery' esté presente
        await page.wait_for_selector('div[data-testid="grid-gallery"]')

        # Hacer scroll down en el div hasta el final
        await scroll_down_in_div(page, 'div[data-testid="grid-gallery"]', times=7, delay=2000)  # Ajusta el número de veces y el retraso según sea necesario

        # Obtener las etiquetas <picture> dentro del contenedor 'grid-gallery'
        gallery_div = await page.query_selector('div[data-testid="grid-gallery"]')
        
        pictures = await gallery_div.query_selector_all('picture')
        
        print("pictures:", pictures, len(pictures))
        
        # Encontrar y descargar todas las imágenes con media min-width de 768px
        for picture in pictures:
            sources = await picture.query_selector_all('source[srcset$=".jpg"]')
            for source in sources:
                media = await source.get_attribute('media')
                resolution = get_media_resolution(media)
                img_url = await source.get_attribute('srcset')
                
                # if resolution == 768:
                if img_url:
                    img_name = os.path.join(download_path, os.path.basename(img_url))
                    with open(img_name, 'wb') as f:
                        f.write(requests.get(img_url).content)
                    print(f'Descargada: {img_name}')

        # Cerrar el navegador
        await browser.close()

if __name__ == "__main__":
    url = 'https://www.trulia.com/home/5287-treetops-dr-naples-fl-34113-43806037?mid=0#lil-mediaTab'
    download_path = 'imagenes_trulia'
    asyncio.run(extract_images(url, download_path))
    print("Descarga completada.")

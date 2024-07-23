import asyncio
import os
import requests
from playwright.async_api import async_playwright

async def download_image(url, download_path):
    img_name = os.path.join(download_path, os.path.basename(url))
    with open(img_name, 'wb') as f:
        f.write(requests.get(url).content)
    print(f'Descargada: {img_name}')


async def scroll_down_in_div(page, div_selector, times=5, delay=3000):
    """
    Scroll down the specified div by simulating mouse wheel scroll.
    """
    for _ in range(times):
        print("BAJANDO")
        await page.hover(div_selector)
        await page.mouse.wheel(0, 500)
        await page.wait_for_timeout(delay)


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
                    await download_image(img_url, download_path)
                    counter += 1
            except:
                # Si no hay más imágenes, salir del bucle
                break

        # Cerrar el modal
        await page.click('button[aria-label="Close"]')
        await page.wait_for_timeout(1000)  # Esperar a que el modal se cierre

        # Cerrar el navegador
        await browser.close()

if __name__ == "__main__":
    url = 'https://www.trulia.com/home/282-s-95th-pl-chandler-az-85224-8207993?mid=0#lil-mediaTab'
    download_path = 'imagenes_trulia'
    asyncio.run(extract_images(url, download_path))
    print("Descarga completada.")

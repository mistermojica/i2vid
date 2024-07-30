import feedparser
from tinydb import TinyDB, Query

# Inicializa la base de datos
db = TinyDB('PERIODICOS.JSON')
periodicos_table = db.table('periodicos')

# Lee todas las URLs de RSS de la tabla de periódicos
periodicos = periodicos_table.all()

# Función para descargar noticias de un feed RSS
def download_news(url):
    feed = feedparser.parse(url)
    news_items = []
    for entry in feed.entries:
        news = {
            'title': entry.title,
            'link': entry.link,
            'summary': entry.summary,
            'description': entry.description,
            'published': entry.published,
            'image': None  # Campo para la imagen
        }
        # Intentar obtener la imagen si está disponible
        if 'media_content' in entry:
            for media in entry.media_content:
                if 'url' in media:
                    news['image'] = media['url']
                    break
        elif 'media_thumbnail' in entry:
            news['image'] = entry.media_thumbnail[0]['url']
        elif 'enclosures' in entry:
            for enclosure in entry.enclosures:
                if 'type' in enclosure and enclosure['type'].startswith('image/'):
                    news['image'] = enclosure['url']
                    break
        print(news)
        news_items.append(news)
    return news_items

# Procesa cada periódico
for periodico in periodicos:
    nombre = periodico['nombre']
    url = periodico['url']
    news_table = db.table(nombre)
    
    # Descarga las noticias
    news_items = download_news(url)
    
    # Almacena las noticias en la tabla correspondiente
    for news in news_items:
        news_table.upsert(news, Query().link == news['link'])
    
    print(f"Noticias de {nombre} descargadas y almacenadas correctamente.")

print("Proceso completado.")

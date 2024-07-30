from tinydb import TinyDB, Query

# Inicializa la base de datos
db = TinyDB('PERIODICOS.JSON')
table = db.table('periodicos')

# Fuentes RSS de los periódicos dominicanos
rss_feeds = [
    {'nombre': 'DiarioLibre', 'url': 'https://www.diariolibre.com/rss/portada.xml'},
    {'nombre': 'Hoy', 'url': 'https://hoy.com.do/feed/'},
    {'nombre': 'ElDia', 'url': 'https://eldia.com.do/feed/'},
    {'nombre': 'ElCaribe', 'url': 'https://www.elcaribe.com.do/feed/'},
    {'nombre': 'ElNacional', 'url': 'https://elnacional.com.do/feed/'}
]

# Inserta las fuentes RSS en la tabla de periódicos
for feed in rss_feeds:
    table.upsert(feed, Query().nombre == feed['nombre'])

print("Fuentes RSS insertadas correctamente.")
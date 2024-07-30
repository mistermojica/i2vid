const express = require('express');
const RSSParser = require('rss-parser');
const path = require('path');
const cheerio = require('cheerio'); // Para parsear HTML y extraer imágenes

const app = express();
const port = 3000;

// Configuración de RSS Parser con campos personalizados
const parser = new RSSParser({
  customFields: {
    item: [
      ['media:content', 'mediaContent', { keepArray: true }],
      ['media:thumbnail', 'mediaThumbnail']
    ]
  }
});

// Fuentes RSS con nombres
const rssFeeds = [
  { url: 'https://www.diariolibre.com/rss/portada.xml', name: 'Diario Libre' },
  { url: 'https://elnuevodiario.com.do/feed', name: 'El Nuevo Diario' },
  { url: 'https://www.elcaribe.com.do/feed', name: 'El Caribe' }
];

// Función para truncar descripciones
function truncateText(text, maxLength = 100) {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

// Función para extraer la primera imagen del contenido HTML
function extractImageFromHtml(content) {
  const $ = cheerio.load(content);
  const img = $('img').first();
  return img.attr('src') || '';
}

// Función para extraer la imagen del tag <media:content>
function extractImageFromMediaContent(mediaContent) {
  if (Array.isArray(mediaContent) && mediaContent.length > 0) {
    // Asumimos que el primer elemento en el array es la imagen que queremos
    return mediaContent[0]['$'].url || '';
  }
  return '';
}

// Función para extraer la imagen del tag <media:thumbnail>
function extractImageFromMediaThumbnail(mediaThumbnail) {
  if (Array.isArray(mediaThumbnail) && mediaThumbnail.length > 0) {
    // Asumimos que el primer elemento en el array es la imagen que queremos
    return mediaThumbnail[0]['$'].url || '';
  }
  return '';
}

// Obtener noticias de todas las fuentes RSS
async function getNews() {
  const newsBySource = [];

  for (const { url, name } of rssFeeds) {
    const feed = await parser.parseURL(url);
    // Extraer y filtrar noticias que contengan imágenes
    newsBySource.push(feed.items
      .map(item => ({
        title: item.title,
        link: item.link,
        description: truncateText(item.contentSnippet, 100), // Truncar la descripción
        pubDate: item.pubDate,
        source: name,
        // Extraer la imagen entre mediaContent, mediaThumbnail y HTML
        image: extractImageFromMediaContent(item.mediaContent) ||
               extractImageFromMediaThumbnail(item.mediaThumbnail) ||
               extractImageFromHtml(item.content)
      }))
      .filter(news => news.image) // Filtrar solo las noticias que tienen una imagen
    );
  }

  // Mezclar las noticias de diferentes fuentes
  const mixedNews = [];
  const maxLength = Math.max(...newsBySource.map(news => news.length));

  for (let i = 0; i < maxLength; i++) {
    for (const news of newsBySource) {
      if (news[i]) {
        mixedNews.push(news[i]);
      }
    }
  }

  return mixedNews;
}

// Buscar noticias por texto y filtrar por fuente
async function searchNews(query, source) {
  const allNews = await getNews();
  return allNews.filter(news => 
    news.title.toLowerCase().includes(query.toLowerCase()) &&
    (source === 'all' || news.source === source)
  );
}

// Endpoint para obtener noticias mezcladas en formato JSON
app.get('/api/news', async (req, res) => {
  try {
    const news = await getNews();
    res.json(news);
  } catch (error) {
    res.status(500).send('Error al obtener noticias');
  }
});

// Endpoint para buscar noticias con filtro
app.get('/api/search', async (req, res) => {
  const { query, source } = req.query;
  try {
    const news = await searchNews(query || '', source || 'all');
    res.json(news);
  } catch (error) {
    res.status(500).send('Error al buscar noticias');
  }
});

// Servir archivos estáticos desde el folder 'public'
app.use(express.static(path.join(__dirname, 'public')));

app.listen(port, () => {
  console.log(`Servidor escuchando en http://localhost:${port}`);
});

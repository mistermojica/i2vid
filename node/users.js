const express = require('express');
const cluster = require('cluster');
const { chromium } = require('playwright');
const fs = require('fs');
const os = require('os');
const app = express();
const port = 3000;

if (cluster.isMaster) {
    const numCPUs = os.cpus().length;

    // Crear workers.
    for (let i = 0; i < numCPUs; i++) {
        cluster.fork();
    }

    cluster.on('exit', (worker, code, signal) => {
        console.log(`Worker ${worker.process.pid} died`);
        cluster.fork(); // Reemplazar el worker caído
    });
} else {
    app.use((req, res, next) => {
        res.header('Access-Control-Allow-Origin', '*');
        res.header('Access-Control-Allow-Methods', 'GET,POST');
        res.header('Access-Control-Allow-Headers', 'Content-Type');
        next();
    });

    async function checkInstagramUsername(username) {
        const browser = await chromium.launch({ headless: false });
        const page = await browser.newPage();
        try {
            await page.goto(`https://www.instagram.com/${username}/`, { waitUntil: 'networkidle' });
            const pageContent = await page.content();
            await page.screenshot({ path: `screenshots/instagram-${username}.png` });
            let resultado = !pageContent.includes("Sorry, this page isn't available") && !pageContent.includes("Lo sentimos, esta página no está disponible");
            return resultado;
        } catch (error) {
            throw new Error('Error al verificar el usuario de Instagram: ' + error.message);
        } finally {
            await page.close();
            await browser.close();
        }
    }

    async function checkFacebookUsername(username) {
        const browser = await chromium.launch({ headless: false });
        const page = await browser.newPage();
        try {
            await page.goto(`https://www.facebook.com/${username}`, { waitUntil: 'networkidle' });
            const pageContent = await page.content();
            await page.screenshot({ path: `screenshots/facebook-${username}.png` });
            let resultado = !pageContent.includes("This content isn't available right now") && !pageContent.includes("Este contenido no está disponible en este momento");
            return resultado;
        } catch (error) {
            throw new Error('Error al verificar el usuario de Facebook: ' + error.message);
        } finally {
            await page.close();
            await browser.close();
        }
    }

    async function checkXUsername(username) {
      const browser = await chromium.launch({ headless: false });
      const page = await browser.newPage();
      try {
          await page.goto(`https://x.com/${username}`, { waitUntil: 'networkidle' });
        //   let login = await page.waitForSelector('span:has-text("Log in")');
          const pageContent = await page.content();
          await page.screenshot({ path: `screenshots/x-${username}.png` });
          // console.log(login);
          const accountNotExist = await page.waitForSelector(`span:has-text("This account doesn't exist")`, { timeout: 5000 });
          // let resultado = !pageContent.includes("This account doesn’t exist") && !pageContent.includes("Esta cuenta no existe");
          console.log({accountNotExist});
          
          return accountNotExist;
      } catch (error) {
          throw new Error('Error al verificar el usuario de X: ' + error.message);
      } finally {
          await page.close();
          await browser.close();
      }
  }

    app.get('/check-instagram/:username', async (req, res) => {
        const username = req.params.username;
        try {
            const instagramExists = await checkInstagramUsername(username);
            console.log({instagramExists});
            res.json({ exists: instagramExists });
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    });

    app.get('/check-facebook/:username', async (req, res) => {
        const username = req.params.username;
        try {
            const facebookExists = await checkFacebookUsername(username);
            console.log({facebookExists});
            res.json({ exists: facebookExists });
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    });

    app.get('/check-youtube/:username', async (req, res) => {
        const username = req.params.username;
        try {
            const response = await fetch(`https://www.youtube.com/user/${username}`, { method: 'HEAD' });
            res.json({ exists: response.status === 200 });
        } catch (error) {
            res.status(500).json({ error: 'Error al verificar el usuario de YouTube: ' + error.message });
        }
    });

    app.get('/check-x/:username', async (req, res) => {
      const username = req.params.username;
      try {
          const xExists = await checkXUsername(username);
          console.log({xExists});
          res.json({ exists: xExists });
      } catch (error) {
          res.status(500).json({ error: error.message });
      }
  });

    app.listen(port, async () => {
        console.log(`Server running at http://localhost:${port}`);

        // Crear la carpeta de screenshots si no existe
        if (!fs.existsSync('screenshots')) {
            fs.mkdirSync('screenshots');
        }
    });
}

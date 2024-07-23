const express = require('express');
const app = express();
const fetch = require('node-fetch');
const cookieParser = require('cookie-parser');
const cors = require('cors');

app.use(cookieParser());
app.use(cors());
app.listen(process.env.PORT || 5012)

const CLIENT_KEY = 'sbawvvmoh9wen4iy9t'

app.get('/callback', (req, res) => {
    res.status(200).send(req.query.code);
})

app.get('/oauth', (req, res) => {
    console.log("AUTORIZANDO...");

    const csrfState = Math.random().toString(36).substring(2);
    res.cookie('csrfState', csrfState, { maxAge: 60000 });

    let url = 'https://www.tiktok.com/v2/auth/authorize/';

    // the following params need to be in `application/x-www-form-urlencoded` format.
    url += `?client_key=${CLIENT_KEY}`;
    url += '&scope=user.info.basic,user.info.profile,user.info.stats,video.list,video.publish,video.upload';
    url += '&response_type=code';
    url += '&redirect_uri=https://6dd8-148-0-94-201.ngrok-free.app/callback';
    url += '&state=' + csrfState;

    console.log("AUTORIZANDO...", url);

    res.redirect(url);
})


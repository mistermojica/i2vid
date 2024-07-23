const express = require('express');
const fs = require('fs');
const path = require('path');
const helper = require("./helper.js");
const bodyParser = require('body-parser');

const app = express();
const port = 8012;

app.use(bodyParser.json());

// Dummy data for inventario and ctx
const inventario = {
  vehDueno: 'John Doe',
  vehMarca: 'Toyota',
  vehModelo: 'Corolla',
  vehAnoFabricacion: 2021,
  vehTipoVehiculo: 'Sedan',
  vehColor: 'Red',
  vehTipoEmision: 'Gasoline'
};

// Dummy function for publishToRRSS
const publishToRRSS = (ctx) => {
    var promise = new Promise(function (resolve, reject) {
  
        console.log('publishToRRSS:', {ctx});
  
        if (ctx.to === 'instagram') {
            helper.instagram(ctx)
            .then((resIG) => {
                resolve({
                success: true,
                message: `Publicación Instagram realizada de forma exitosa.`,
                result: resIG,
                });
            })
            .catch((errIG) => {
                console.log("result errIG:", errIG);
                reject({
                success: false,
                message: `Error inesperado al realizar Publicación en Instagram.`,
                result: errIG,
                });
            });
        }
    
        // if (ctx.to === 'marketplace' && ctx.conFBUsuario && ctx.conFBContrasena) {
        //     helper.marketplace(ctx)
        //     .then((resMP) => {
        //         resolve({
        //         success: true,
        //         message: `${entityName} en Market Place realizada de forma exitosa.`,
        //         result: resMP,
        //         });
        //     })
        //     .catch((errMP) => {
        //         console.log("result errMP:", errMP);
        //         reject({
        //         success: false,
        //         message: `Error inesperado al realizar ${entityName} en Market Place.`,
        //         result: errMP,
        //         });
        //     });
        // }
    });
  
    return promise;
};

app.post('/', (req, res) => {
  console.log(req.body);

  res.status(200).send(req.body);
});

app.get('/', (req, res) => {
  console.log(req.params);
  console.log(req.query);
  res.status(200).send({params: req.params, query: req.query});
});


// Endpoint to read files and send to publishToRRSS
app.post('/publish', (req, res) => {

  // const directoryPath = path.join(__dirname, '../imagenes_trulia'); // Path to the images folder

  // fs.readdir(directoryPath, (err, files) => {
    // if (err) {
    //   return res.status(500).send('Unable to scan directory: ' + err);
    // }

    // const arrFotosVehiculos = [];
    // files.forEach(file => {
    // //   if (arrFotosVehiculos.lenth <= 10){
    //     arrFotosVehiculos.push(path.join(directoryPath, file));
    // //   }
    // });

    console.log(req.body);

    const {
      dueno,
      to,
      images,
      caption,
      brand,
      model,
      year,
      location,
      show
    } = req.body;

    // Extraer solo las URLs de req.body.arrFotosVehiculos
    const imagesurls = images.map(foto => foto.url);

    // console.log(req.body);

    // Construir el contexto para enviar
    let ctxSend = {
      "dueno": dueno,
      "to": to,
      "image": imagesurls,
      "caption": caption,
      "location": location,
      "year": year,
      "brand": brand,
      "model": model,
      "show": show
    };

    console.log(ctxSend);

    publishToRRSS(ctxSend);

    // res.send('All images processed and sent to publishToRRSS.');
  // });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});

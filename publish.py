from flask import Flask, request, jsonify
import asyncio
import os
import json

from helper import helper_instagram  # Import the placeholder function

app = Flask(__name__)
port = 3002

# Dummy function for publishToRRSS
async def publish_to_rrss(ctx):
    print('publishToRRSS:', ctx)
    
    if ctx['to'] == 'instagram':
        try:
            res_ig = await helper_instagram(ctx)
            return {
                "success": True,
                "message": "Publicación Instagram realizada de forma exitosa.",
                "result": res_ig
            }
        except Exception as err_ig:
            print("result errIG:", err_ig)
            return {
                "success": False,
                "message": "Error inesperado al realizar Publicación en Instagram.",
                "result": err_ig
            }
    # You can add more conditions here if needed


@app.route('/publish', methods=['POST'])
def publish():
    try:
        data = request.json
        print(data)

        # Extract data from request
        dueno = data.get('dueno')
        to = data.get('to')
        images = data.get('images', [])
        caption = data.get('caption')
        brand = data.get('brand')
        model = data.get('model')
        year = data.get('year')
        location = data.get('location')
        show = data.get('show')

        # Extract only URLs from images
        images_urls = [foto['url'] for foto in images]

        # Build context to send
        ctx_send = {
            "dueno": dueno,
            "to": to,
            "image": images_urls,
            "caption": caption,
            "location": location,
            "year": year,
            "brand": brand,
            "model": model,
            "show": show
        }

        print(ctx_send)

        # Run the publish_to_rrss function
        result = asyncio.run(publish_to_rrss(ctx_send))
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=port)
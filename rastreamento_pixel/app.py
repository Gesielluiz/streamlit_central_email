from flask import Flask, request, send_file
import os
from pathlib import Path
from banco import salvar_rastreamento  # Certifique-se de existir essa função em banco.py


app = Flask(__name__)

# Caminho para o pixel transparente (coloque pixel.png dentro dessa mesma pasta)
BASE_DIR = Path(__file__).parent
TRANSPARENT_PIXEL_PATH = BASE_DIR / "pixel.png"

@app.route("/rastreamento")
def rastreamento():
    rastreio_id = request.args.get("id")
    ip = request.remote_addr or ""
    user_agent = request.headers.get("User-Agent", "")
    # Os dados de rastreamento serão salvos no banco:
    if rastreio_id:
        try:
            salvar_rastreamento(rastreio_id, ip, user_agent)
        except:
            pass

    # Retorna sempre o pixel transparente:
    return send_file(TRANSPARENT_PIXEL_PATH, mimetype="image/png")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)

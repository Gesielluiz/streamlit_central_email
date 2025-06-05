# gera_pixel.py

import os
import base64

# 1) Garante que a pasta rastreamento_pixel exista
os.makedirs("rastreamento_pixel", exist_ok=True)

# 2) Conteúdo base64 de um PNG transparente 1×1
b64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAA"
    "AAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)

# 3) Decodifica o base64 e grava como pixel.png dentro de rastreamento_pixel/
with open("rastreamento_pixel/pixel.png", "wb") as f:
    f.write(base64.b64decode(b64))

print("pixel.png (1×1 transparente) criado em rastreamento_pixel/pixel.png")


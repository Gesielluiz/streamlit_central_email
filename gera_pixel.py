# gera_pixel.py

from PIL import Image

# Cria uma imagem RGBA 1×1 completamente transparente
img = Image.new("RGBA", (1, 1), (255, 255, 255, 0))
img.save("rastreamento_pixel/pixel.png", "PNG")

print("pixel.png (1×1 transparente) gerado em rastreamento_pixel/pixel.png")

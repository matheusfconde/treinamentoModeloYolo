import os
import cairosvg

# --- Caminho do diretório de imagens ---
images_path = "dataset/images"

# --- 1️⃣ Encontrar arquivos SVG ---
svg_files = []
print(f"Buscando arquivos SVG em '{images_path}'...")
for dirpath, dirnames, filenames in os.walk(images_path):
    for filename in filenames:
        if filename.lower().endswith('.svg'):
            svg_files.append(os.path.join(dirpath, filename))

if not svg_files:
    print("Nenhum arquivo SVG encontrado. Nada para converter.")
else:
    print(f"Encontrados {len(svg_files)} arquivos SVG.")

# --- 2️⃣ Converter cada arquivo SVG para PNG ---
for svg_path in svg_files:
    # Define o caminho de saída para o novo arquivo PNG
    # Ele terá o mesmo nome e diretório, mas com a extensão .png
    png_path = os.path.splitext(svg_path)[0] + ".png"

    try:
        # Converte o SVG para PNG
        cairosvg.svg2png(url=svg_path, write_to=png_path)
        print(f"Conversão concluída: {svg_path} -> {png_path}")
    except Exception as e:
        print(f"Erro ao converter o arquivo '{svg_path}': {e}")

print("\nProcesso de conversão finalizado.")
import os
import cv2
import re

# --- Caminhos ---
images_path = "dataset/images"
labels_path = "dataset/labels"

# Cria os diretórios necessários
os.makedirs(images_path, exist_ok=True)
os.makedirs(labels_path, exist_ok=True)

# --- 1️⃣ Encontrar e preparar a lista de arquivos ---
all_png_files = []
# Percorre todas as pastas e subpastas para encontrar os arquivos .png
for dirpath, dirnames, filenames in os.walk(images_path):
    for filename in filenames:
        if filename.lower().endswith('.png'):
            all_png_files.append(os.path.join(dirpath, filename))

# --- 2️⃣ Criar class_map com a lógica de nome base ---
# Pegar nomes base únicos de todos os arquivos
class_names = set()
for full_path in all_png_files:
    filename = os.path.basename(full_path)
    
    # --- Lógica otimizada para determinar o nome base ---
    filename_without_ext = os.path.splitext(filename)[0]
    
    # Usa re.sub para remover os sufixos _dark ou _light
    base_name = re.sub(r'(_dark|_light)$', '', filename_without_ext, flags=re.IGNORECASE)
    
    class_names.add(base_name)

# Ordena os nomes para garantir que os IDs sejam consistentes
class_names = sorted(list(class_names))

# Gera ID único para cada classe
class_map = {name: idx for idx, name in enumerate(class_names)}

print("Classes detectadas:")
for name, idx in class_map.items():
    print(f"{idx}: {name}")

# --- 3️⃣ Gerar labels YOLO ---
for full_path in all_png_files:
    # Obtém o nome do arquivo e o diretório
    dir_name, filename = os.path.split(full_path)
    
    # --- Aplica a mesma lógica simplificada para o arquivo atual ---
    filename_without_ext = os.path.splitext(filename)[0]
    
    base_name = re.sub(r'(_dark|_light)$', '', filename_without_ext, flags=re.IGNORECASE)
    
    img = cv2.imread(full_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Erro ao ler {full_path}, pulando...")
        continue
    
    h, w = img.shape[:2]
    
    # Assumindo 1 objeto por imagem, bounding box ocupa toda a imagem
    x_center, y_center = 0.5, 0.5
    width_norm, height_norm = 1.0, 1.0
    
    # Descobre a classe pelo nome base
    class_id = class_map[base_name]
    label_line = f"{class_id} {x_center} {y_center} {width_norm} {height_norm}"
    
    # Salva o arquivo de label no diretório "labels"
    txt_path = os.path.join(labels_path, os.path.splitext(filename)[0] + ".txt")
    with open(txt_path, "w") as f:
        f.write(label_line)
    
    print(f"Label criado: {txt_path}")

# --- 4️⃣ Gerar arquivo com nomes das classes ---
names_array = [None] * len(class_map)
for name, idx in class_map.items():
    names_array[idx] = name

names_str = f"names: {names_array}\n"

# Salva o arquivo de classes no diretório raiz do dataset
classes_file = os.path.join("dataset", "classes.yaml")

with open(classes_file, "w", encoding="utf-8") as f:
    f.write(names_str)

print(f"\nArquivo de classes criado: {classes_file}")
print(names_str)

# --- 5️⃣ Exibir o total de classes ---
print(f"\nTotal de classes criadas: {len(class_map)}")
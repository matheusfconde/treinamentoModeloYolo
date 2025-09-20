import os
import shutil
import random
import math
from typing import List, Tuple, Dict
from collections import defaultdict, Counter
from PIL import Image, ImageDraw, ImageEnhance
from sklearn.model_selection import train_test_split
import yaml

# --- 1. DEFINIÇÃO DE CAMINHOS E PARÂMETROS ---
ICONS_DIR = 'dataset/images'
ICONS_LABELS_DIR = 'dataset/labels'
OUTPUT_DATASET_DIR = 'dataset/yolo'

# Parâmetros de geração de imagens sintéticas
# Cada classe terá este número de instâncias no conjunto TOTAL gerado
TARGET_OCCURRENCES_PER_CLASS = 50 
IMAGE_SIZE = (1200, 1000)
MIN_ICONS_PER_IMAGE = 3
MAX_ICONS_PER_IMAGE = 10
ICON_MIN_SIZE_RATIO = 0.05
ICON_MAX_SIZE_RATIO = 0.15

# Parâmetros para fundos com zonas e caixas
MIN_ZONES_PER_IMAGE = 1
MAX_ZONES_PER_IMAGE = 3
ZONE_MIN_COLOR_VARIATION = 30
ZONE_LINE_WIDTH = 3

# Parâmetros de divisão do dataset
SPLIT_RATIOS = {'train': 0.7, 'val': 0.15, 'test': 0.15}
RANDOM_STATE = 42
random.seed(RANDOM_STATE)

# --- 2. FUNÇÕES AUXILIARES ---

def generate_dynamic_background(size: Tuple[int, int]) -> Image.Image:
    color = (
        random.randint(150, 230),
        random.randint(150, 230),
        random.randint(150, 230)
    )
    return Image.new('RGB', size, color=color)

##TO DO PEGAR DA OUTRA PASTA QUEIRA ROTAÇÃO
def augment_icon(icon_img: Image.Image) -> Image.Image:
    # Não aplica rotação, só brilho/contraste
    enhancer = ImageEnhance.Brightness(icon_img)
    icon_img = enhancer.enhance(random.uniform(0.8, 1.2))
    enhancer = ImageEnhance.Contrast(icon_img)
    icon_img = enhancer.enhance(random.uniform(0.8, 1.2))
    return icon_img


def convert_bbox_coords(new_coords: Tuple[int, int, int, int], new_img_size: Tuple[int, int]) -> List[float]:
    x_min, y_min, x_max, y_max = new_coords
    img_width, img_height = new_img_size
    x_c = (x_min + x_max) / 2
    y_c = (y_min + y_max) / 2
    w = x_max - x_min
    h = y_max - y_min
    return [x_c / img_width, y_c / img_height, w / img_width, h / img_height]

def check_overlap(new_bbox, existing_bboxes, iou_threshold=0.1):
    x_min1, y_min1, x_max1, y_max1 = new_bbox
    for (x_min2, y_min2, x_max2, y_max2) in existing_bboxes:
        inter_xmin = max(x_min1, x_min2)
        inter_ymin = max(y_min1, y_min2)
        inter_xmax = min(x_max1, x_max2)
        inter_ymax = min(y_max1, y_max2)
        inter_area = max(0, inter_xmax - inter_xmin) * max(0, inter_ymax - inter_ymin)
        area1 = (x_max1 - x_min1) * (y_max1 - y_min1)
        area2 = (x_max2 - x_min2) * (y_max2 - y_min2)
        iou = inter_area / float(area1 + area2 - inter_area + 1e-6)
        if iou > iou_threshold:
            return True
    return False

def load_icons(icons_dir: str) -> List[Dict]:
    icons_data = []
    for filename in os.listdir(icons_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            base_name = os.path.splitext(filename)[0]
            label_path = os.path.join(ICONS_LABELS_DIR, base_name + '.txt')
            if os.path.exists(label_path):
                with open(label_path, 'r') as f:
                    label_content = f.readline().strip()
                if label_content:
                    class_id = int(label_content.split()[0])
                    icons_data.append({'path': os.path.join(icons_dir, filename), 'class_id': class_id})
    return icons_data

def connect_icons(draw_obj: ImageDraw.Draw, bboxes: List[Tuple[int,int,int,int]], color: Tuple[int,int,int]):
    if len(bboxes) < 2: return
    shuffled_bboxes = random.sample(bboxes, k=len(bboxes))
    for i in range(len(shuffled_bboxes) - 1):
        bbox1, bbox2 = shuffled_bboxes[i], shuffled_bboxes[i+1]
        center1 = ((bbox1[0]+bbox1[2])/2, (bbox1[1]+bbox1[3])/2)
        center2 = ((bbox2[0]+bbox2[2])/2, (bbox2[1]+bbox2[3])/2)
        draw_obj.line([center1, center2], fill=color, width=2)
        angle = math.atan2(center2[1]-center1[1], center2[0]-center1[0])
        arrow_x1 = center2[0] - 10 * math.cos(angle - math.pi/6)
        arrow_y1 = center2[1] - 10 * math.sin(angle - math.pi/6)
        arrow_x2 = center2[0] - 10 * math.cos(angle + math.pi/6)
        arrow_y2 = center2[1] - 10 * math.sin(angle + math.pi / 6)
        draw_obj.polygon([(center2[0], center2[1]), (arrow_x1, arrow_y1), (arrow_x2, arrow_y2)], fill=color)

def create_yolo_structure(output_dir: str):
    for subset in ['train', 'val', 'test']:
        os.makedirs(os.path.join(output_dir, subset, 'images'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, subset, 'labels'), exist_ok=True)

def create_data_yaml(class_names: List[str], output_dir: str):
    # Caminhos das pastas
    train_path = os.path.join('train', 'images').replace('/', '\\')
    val_path = os.path.join('val', 'images').replace('/', '\\')
    test_path = os.path.join('test', 'images').replace('/', '\\')

    yaml_content = (
        # f"path: {os.path.abspath(output_dir).replace('/', '\\')}\n"
        f"train: {train_path}\n"
        f"val: {val_path}\n"
        f"test: {test_path}\n"
        f"nc: {len(class_names)}\n"
        f"names: {class_names}\n"
    )

    with open(os.path.join(output_dir, 'data.yaml'), 'w') as f:
        f.write(yaml_content)

# --- 3. GERAÇÃO E DIVISÃO DO DATASET FINAL ---
def main():
    if os.path.exists(OUTPUT_DATASET_DIR):
        shutil.rmtree(OUTPUT_DATASET_DIR)
    
    icons_data = load_icons(ICONS_DIR)
    class_names_map = {icon['class_id']: os.path.splitext(os.path.basename(icon['path']))[0] for icon in icons_data}
    sorted_class_names = [class_names_map[i] for i in sorted(class_names_map.keys())]
    
    images_metadata = []
    
    print(f"Iniciando a geração de imagens sintéticas...")
    
    temp_dir = 'temp_synthetic'
    os.makedirs(os.path.join(temp_dir, 'images'), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, 'labels'), exist_ok=True)
    
    total_generated_images = 0

    # Loop principal para gerar imagens balanceadas para cada classe
    for class_id_to_focus in sorted(class_names_map.keys()):
        icons_for_focus_class = [icon for icon in icons_data if icon['class_id'] == class_id_to_focus]
        if not icons_for_focus_class:
            continue
        
        for _ in range(TARGET_OCCURRENCES_PER_CLASS):
            icon_info = random.choice(icons_for_focus_class)
            
            num_other_icons = random.randint(MIN_ICONS_PER_IMAGE - 1, MAX_ICONS_PER_IMAGE - 1)
            other_icons = random.sample([i for i in icons_data if i['class_id'] != class_id_to_focus], k=min(num_other_icons, len(icons_data) - 1))
            
            selected_icons = [icon_info] + other_icons
            
            # Lógica de geração da imagem com fundos dinâmicos e conexões
            bg_img = generate_dynamic_background(IMAGE_SIZE)
            draw = ImageDraw.Draw(bg_img)
            base_bg_color = bg_img.getpixel((0,0))
            
            synthetic_labels, existing_bboxes = [], []
            for icon_data in selected_icons:
                icon_img = Image.open(icon_data['path']).convert("RGBA")
                icon_img = augment_icon(icon_img)
                size_ratio = random.uniform(ICON_MIN_SIZE_RATIO, ICON_MAX_SIZE_RATIO)
                target_size = (int(IMAGE_SIZE[0]*size_ratio), int(IMAGE_SIZE[1]*size_ratio))
                icon_img_resized = icon_img.resize(target_size, Image.Resampling.LANCZOS)
                
                placed = False
                for _ in range(50):
                    x = random.randint(0, IMAGE_SIZE[0]-target_size[0])
                    y = random.randint(0, IMAGE_SIZE[1]-target_size[1])
                    bbox = (x, y, x+target_size[0], y+target_size[1])
                    if not check_overlap(bbox, existing_bboxes):
                        bg_img.paste(icon_img_resized, (x, y), icon_img_resized)
                        existing_bboxes.append(bbox)
                        bbox_yolo = convert_bbox_coords(bbox, IMAGE_SIZE)
                        synthetic_labels.append(f"{icon_data['class_id']} {' '.join(map(str,bbox_yolo))}")
                        placed = True
                        break
            
            if existing_bboxes:
                line_color = (255, 255, 255) if sum(base_bg_color) < 380 else (0, 0, 0)
                connect_icons(draw, existing_bboxes, line_color)

            if synthetic_labels:
                fname = f"synthetic_{total_generated_images:05d}.jpg"
                lfname = f"synthetic_{total_generated_images:05d}.txt"
                images_metadata.append({'image': fname, 'label': lfname, 'class_id': class_id_to_focus})
                bg_img.save(os.path.join(temp_dir, 'images', fname))
                with open(os.path.join(temp_dir, 'labels', lfname), 'w') as f:
                    f.write("\n".join(synthetic_labels))
                total_generated_images += 1
        
        print(f"Geradas {TARGET_OCCURRENCES_PER_CLASS} imagens para a classe {class_names_map[class_id_to_focus]}.")
    
    print(f"\n✅ Geração de {total_generated_images} imagens sintéticas concluída.")

    # --- DIVISÃO ESTRATIFICADA E LIMPEZA ---
    images_files = [m['image'] for m in images_metadata]
    labels_stratify = [m['class_id'] for m in images_metadata]
    
    create_yolo_structure(OUTPUT_DATASET_DIR)
    
    # Divide o dataset em treino, validação e teste de forma estratificada
    try:
        train_val_files, test_files, train_val_labels, test_labels = train_test_split(
            images_files, labels_stratify, test_size=SPLIT_RATIOS['test'],
            stratify=labels_stratify, random_state=RANDOM_STATE
        )

        train_files, val_files, _, _ = train_test_split(
            train_val_files, train_val_labels,
            test_size=SPLIT_RATIOS['val'] / (SPLIT_RATIOS['train'] + SPLIT_RATIOS['val']),
            stratify=train_val_labels, random_state=RANDOM_STATE
        )
    except ValueError as e:
        print("\n❌ ERRO FATAL: Falha na divisão estratificada.")
        print(f"Causa: {e}")
        print("A causa mais provável é que a proporção de divisão solicitada resulta em um subconjunto com poucas instâncias de alguma classe.")
        print("Tente ajustar as proporções de SPLIT_RATIOS para que sejam maiores ou gere mais imagens por classe.")
        raise e
    
    print(f"\nTotal de imagens geradas: {len(images_files)}")
    print(f"Total de imagens de treino: {len(train_files)}")
    print(f"Total de imagens de validação: {len(val_files)}")
    print(f"Total de imagens de teste: {len(test_files)}")

    for subset, files_list in [('train', train_files), ('val', val_files), ('test', test_files)]:
        for img_file in files_list:
            lbl_file = os.path.splitext(img_file)[0] + ".txt"
            shutil.copy(os.path.join(temp_dir, 'images', img_file), os.path.join(OUTPUT_DATASET_DIR, subset, 'images', img_file))
            shutil.copy(os.path.join(temp_dir, 'labels', lbl_file), os.path.join(OUTPUT_DATASET_DIR, subset, 'labels', lbl_file))

    shutil.rmtree(temp_dir)
    create_data_yaml(sorted_class_names, OUTPUT_DATASET_DIR)
    
    print("\n✅ Script finalizado! O novo dataset sintético está pronto para o treinamento.")

if __name__ == "__main__":
    main()
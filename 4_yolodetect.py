# # # import os
# # # from PIL import Image, ImageDraw, ImageFont
# # # from ultralytics import YOLO

# # # # Carregar o modelo treinado
# # # model_path = r'D:\_fiap\treinamentoModeloYolo\dataset\best.pt'
# # # try:
# # #     model = YOLO(model_path)
# # # except Exception as e:
# # #     print(f"Erro ao carregar o modelo YOLO. Verifique se o caminho está correto e o arquivo existe: {e}")
# # #     exit()

# # # # Definir os caminhos para as imagens de entrada
# # # image_paths = [
# # #     r'D:\_fiap\treinamentoModeloYolo\Arquiteturas Imagens\arch_azure.png',
# # #     r'D:\_fiap\treinamentoModeloYolo\Arquiteturas Imagens\arch_aws.png'
# # # ]

# # # # Definir a fonte e o tamanho do texto
# # # try:
# # #     font = ImageFont.truetype("arial.ttf", 20)
# # # except IOError:
# # #     font = ImageFont.load_default()

# # # # Mapear os IDs das classes para os nomes
# # # names_map = model.names

# # # # Iterar sobre cada imagem na lista
# # # for image_path in image_paths:
# # #     if not os.path.exists(image_path):
# # #         print(f"Aviso: Arquivo não encontrado em {image_path}. Pulando...")
# # #         continue

# # #     # Realiza a detecção de objetos na imagem
# # #     results = model.predict(source=image_path, conf=0.20, save=False, verbose=False)

# # #     # Carregar a imagem para processamento
# # #     img = Image.open(image_path).convert("RGB")
# # #     draw = ImageDraw.Draw(img)

# # #     legend_text = []

# # #     # Iterar sobre as detecções
# # #     for i, r in enumerate(results[0].boxes.data):
# # #         x1, y1, x2, y2, conf, cls_id = r
# # #         x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
# # #         cls_id = int(cls_id)
# # #         class_name = names_map[cls_id]
        
# # #         # Desenhar a bounding box e número
# # #         draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
# # #         draw.text((x1, y1 - 25), str(i + 1), fill="red", font=font)
        
# # #         # Adicionar legenda
# # #         legend_text.append(f"{i+1}: {class_name} ({conf:.2f})")

# # #     # Calcular altura extra necessária para as legendas
# # #     line_height = 30
# # #     extra_height = len(legend_text) * line_height + 20
    
# # #     # Criar nova imagem com espaço abaixo
# # #     img_width, img_height = img.size
# # #     new_img = Image.new("RGB", (img_width, img_height + extra_height), (255, 255, 255))
# # #     new_img.paste(img, (0, 0))
# # #     draw_new = ImageDraw.Draw(new_img)

# # #     # Desenhar legendas abaixo da imagem
# # #     y_offset = img_height + 10
# # #     for text in legend_text:
# # #         draw_new.text((20, y_offset), text, fill="black", font=font)
# # #         y_offset += line_height

# # #     # Salvar resultado com nome específico
# # #     base_filename = os.path.basename(image_path)
# # #     output_path = f"labeled_{base_filename}"
# # #     new_img.save(output_path)

# # #     print(f"Detecção concluída para '{base_filename}'! A imagem com as caixas e legendas foi salva em '{output_path}'.")


# # import os
# # from PIL import Image, ImageDraw, ImageFont
# # from ultralytics import YOLO
# # import numpy as np

# # # --- 1. Função para filtrar detecções duplicadas da mesma classe ---
# # def filtrar_deteccoes_por_classe(boxes, names_map, margem=50):
# #     """
# #     Remove detecções muito próximas da mesma classe.
# #     Mantém apenas a de maior confiança em cada região.

# #     Args:
# #         boxes: tensor do YOLO (x1, y1, x2, y2, conf, cls_id)
# #         names_map: mapeamento de IDs -> nomes das classes
# #         margem: distância mínima entre centros para considerar como detecção diferente
# #     """
# #     filtradas = []

# #     # Ordena por confiança (decrescente)
# #     sorted_boxes = sorted(boxes, key=lambda b: float(b[4]), reverse=True)

# #     for box in sorted_boxes:
# #         x1, y1, x2, y2, conf, cls_id = box
# #         cls_id = int(cls_id)
# #         class_name = names_map[cls_id]

# #         cx = (x1 + x2) / 2
# #         cy = (y1 + y2) / 2

# #         conflito = False
# #         for f in filtradas:
# #             fx1, fy1, fx2, fy2, fconf, fcls_id, fname = f
# #             if fname == class_name:
# #                 fx, fy = (fx1 + fx2) / 2, (fy1 + fy2) / 2
# #                 dist = np.sqrt((cx - fx) ** 2 + (cy - fy) ** 2)

# #                 if dist < margem:
# #                     conflito = True
# #                     break

# #         if not conflito:
# #             filtradas.append((x1, y1, x2, y2, conf, cls_id, class_name))

# #     return filtradas


# # # --- 2. Carregar modelo YOLO ---
# # model_path = r'D:\_fiap\treinamentoModeloYolo\dataset\best.pt'
# # try:
# #     model = YOLO(model_path)
# # except Exception as e:
# #     print(f"❌ Erro ao carregar o modelo YOLO: {e}")
# #     exit()

# # # --- 3. Caminhos de imagens ---
# # image_paths = [
# #     r'D:\_fiap\treinamentoModeloYolo\Arquiteturas Imagens\arch_azure.png',
# #     r'D:\_fiap\treinamentoModeloYolo\Arquiteturas Imagens\arch_aws.png'
# # ]

# # # --- 4. Fonte para textos ---
# # try:
# #     font = ImageFont.truetype("arial.ttf", 20)
# # except IOError:
# #     font = ImageFont.load_default()

# # # --- 5. Processar cada imagem ---
# # names_map = model.names

# # for image_path in image_paths:
# #     if not os.path.exists(image_path):
# #         print(f"⚠️ Arquivo não encontrado: {image_path}")
# #         continue

# #     # Realiza a detecção de objetos com NMS nativa
# #     results = model.predict(source=image_path, conf=0.20, iou=0.70, save=False, verbose=False)
# #     img = Image.open(image_path).convert("RGB")
# #     draw = ImageDraw.Draw(img)

# #     # Aplicar filtro anti-duplicação (opcional, já que o IOU está sendo usado)
# #     deteccoes = filtrar_deteccoes_por_classe(results[0].boxes.data.tolist(), names_map, margem=60)

# #     legend_text = []
# #     for i, (x1, y1, x2, y2, conf, cls_id, class_name) in enumerate(deteccoes, start=1):
# #         x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

# #         # Desenhar bounding box e número
# #         draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
# #         draw.text((x1, max(0, y1 - 25)), str(i), fill="red", font=font)

# #         # Adicionar legenda
# #         legend_text.append(f"{i}: {class_name} ({conf:.2f})")

# #     # Espaço extra para legenda
# #     line_height = 30
# #     extra_height = len(legend_text) * line_height + 20
# #     img_width, img_height = img.size

# #     new_img = Image.new("RGB", (img_width, img_height + extra_height), (255, 255, 255))
# #     new_img.paste(img, (0, 0))
# #     draw_new = ImageDraw.Draw(new_img)

# #     # Legendas abaixo da imagem
# #     y_offset = img_height + 10
# #     for text in legend_text:
# #         draw_new.text((20, y_offset), text, fill="black", font=font)
# #         y_offset += line_height

# #     # Salvar resultado
# #     base_filename = os.path.basename(image_path)
# #     output_path = f"labeled_{base_filename}"
# #     new_img.save(output_path)

# #     print(f"✅ Detecção concluída: {output_path}")

###### MENOS PIOR


import os
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO
import numpy as np

# --- 1. Função auxiliar para calcular IoU ---
def calcular_iou(box1, box2):
    """Calcula a Interseção sobre União (IoU) de duas bounding boxes."""
    # Coordenadas da área de interseção
    x_min_inter = max(box1[0], box2[0])
    y_min_inter = max(box1[1], box2[1])
    x_max_inter = min(box1[2], box2[2])
    y_max_inter = min(box1[3], box2[3])

    # Área de interseção
    inter_width = max(0, x_max_inter - x_min_inter)
    inter_height = max(0, y_max_inter - y_min_inter)
    intersection_area = inter_width * inter_height

    # Área de cada bounding box
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])

    # Área da união
    union_area = box1_area + box2_area - intersection_area

    if union_area == 0:
        return 0
    return intersection_area / union_area

# --- 2. Função para filtrar detecções sobrepostas ---
def filtrar_deteccoes_por_iou(boxes, names_map, iou_threshold=0.5):
    """
    Filtra detecções sobrepostas, mantendo a de maior confiança,
    independentemente da classe.
    """
    # Converte o tensor para lista e ordena por confiança (decrescente)
    sorted_boxes = sorted(boxes.tolist(), key=lambda b: float(b[4]), reverse=True)

    filtradas = []
    for box in sorted_boxes:
        is_overlapping = False
        # Verifica se a caixa atual se sobrepõe a alguma já filtrada
        for f_box in filtradas:
            iou = calcular_iou(box[:4], f_box[:4])
            if iou > iou_threshold:
                is_overlapping = True
                break
        
        # Se não houver sobreposição, adiciona à lista de resultados
        if not is_overlapping:
            # Adiciona a caixa original junto com o nome da classe
            conf = float(box[4])
            cls_id = int(box[5])
            class_name = names_map[cls_id]
            filtradas.append(box + [class_name])
    
    return filtradas

# --- 3. Carregar modelo YOLO ---
model_path = r'D:\_fiap\treinamentoModeloYolo\dataset\best.pt'
try:
    model = YOLO(model_path)
except Exception as e:
    print(f"❌ Erro ao carregar o modelo YOLO: {e}")
    exit()

# --- 4. Caminhos de imagens ---
image_paths = [
    r'D:\_fiap\treinamentoModeloYolo\Arquiteturas Imagens\arch_azure.png',
    r'D:\_fiap\treinamentoModeloYolo\Arquiteturas Imagens\arch_aws.png'
]

# --- 5. Fonte para textos ---
try:
    font = ImageFont.truetype("arial.ttf", 20)
except IOError:
    font = ImageFont.load_default()

# --- 6. Processar cada imagem ---
names_map = model.names

for image_path in image_paths:
    if not os.path.exists(image_path):
        print(f"⚠️ Arquivo não encontrado: {image_path}")
        continue

    # Realiza a detecção de objetos. O parâmetro IOU nativo pode ser mais eficaz,
    # mas a lógica de filtragem manual abaixo garante o comportamento solicitado.
    # results = model.predict(source=image_path, save=False, verbose=False)
    results = model.predict(source=image_path, conf=0.25, save=False, verbose=False)
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Aplica o filtro personalizado por IoU
    deteccoes = filtrar_deteccoes_por_iou(results[0].boxes.data, names_map, iou_threshold=0.5)

    legend_text = []
    for i, box_info in enumerate(deteccoes, start=1):
        x1, y1, x2, y2, conf, cls_id, class_name = box_info
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

        # Desenhar bounding box e número
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
        draw.text((x1, max(0, y1 - 25)), str(i), fill="red", font=font)

        # Adicionar legenda
        legend_text.append(f"{i}: {class_name} ({conf:.2f})")

    # Espaço extra para legenda
    line_height = 30
    extra_height = len(legend_text) * line_height + 20
    img_width, img_height = img.size

    new_img = Image.new("RGB", (img_width, img_height + extra_height), (255, 255, 255))
    new_img.paste(img, (0, 0))
    draw_new = ImageDraw.Draw(new_img)

    # Legendas abaixo da imagem
    y_offset = img_height + 10
    for text in legend_text:
        draw_new.text((20, y_offset), text, fill="black", font=font)
        y_offset += line_height

    # Salvar resultado
    base_filename = os.path.basename(image_path)
    output_path = f"labeled_{base_filename}"
    new_img.save(output_path)

    print(f"✅ Detecção concluída: {output_path}")
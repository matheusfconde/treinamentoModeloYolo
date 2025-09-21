import os
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
import numpy as np

# ======================
# 1. STRIDE Mapping
# ======================
stride_mapping = {
    "AWS-Backup": {
        "Spoofing": "Acesso indevido fingindo ser um sistema autorizado.",
        "Tampering": "Alteração ou exclusão de backups críticos.",
        "Repudiation": "Falta de rastreabilidade em operações de restauração.",
        "Information Disclosure": "Exposição de dados sensíveis em backups.",
        "Denial of Service": "Sobrecarga de processos de backup.",
        "Elevation of Privilege": "Usuário comum acessa backups de nível restrito."
    },
    "AWS-Category_Compute": {
        "Spoofing": "VMs falsas se passando por instâncias legítimas.",
        "Tampering": "Alteração da imagem base ou do código implantado.",
        "Repudiation": "Falta de registros de execução.",
        "Information Disclosure": "Dados em memória ou logs expostos.",
        "Denial of Service": "Exaustão de CPU/RAM por workloads maliciosos.",
        "Elevation of Privilege": "Exploração para acesso root/admin."
    },
    "AWS-Cloud-logo": {
        "Spoofing": "Uso de logotipo para phishing.",
        "Tampering": "Alteração não autorizada da identidade visual.",
        "Repudiation": "Dificuldade em provar autoria de modificações.",
        "Information Disclosure": "Exposição de design interno de marca.",
        "Denial of Service": "Uso abusivo para confundir usuários.",
        "Elevation of Privilege": "Uso indevido da marca para enganar stakeholders."
    },
    "AWS-CloudFront": {
        "Spoofing": "CDN falsa interceptando tráfego.",
        "Tampering": "Modificação de conteúdo em cache.",
        "Repudiation": "Logs de distribuição incompletos.",
        "Information Disclosure": "Cabeçalhos expondo origem ou tokens.",
        "Denial of Service": "Ataques volumétricos contra edge locations.",
        "Elevation of Privilege": "Configuração incorreta permite bypass de restrições."
    },
    "AWS-CloudTrail": {
        "Spoofing": "Logs forjados por invasores.",
        "Tampering": "Alteração ou deleção de trilhas de auditoria.",
        "Repudiation": "Falta de integridade em eventos registrados.",
        "Information Disclosure": "Exposição de logs com chaves/tokens.",
        "Denial of Service": "Sobrecarga por excesso de eventos.",
        "Elevation of Privilege": "Usuário malicioso desativa auditoria."
    },
    "AWS-CloudWatch": {
        "Spoofing": "Agente falso envia métricas manipuladas.",
        "Tampering": "Alteração de alarmes e dashboards.",
        "Repudiation": "Dificuldade em atribuir origem de métricas.",
        "Information Disclosure": "Logs contendo dados confidenciais.",
        "Denial of Service": "Excesso de métricas gerando custos altos.",
        "Elevation of Privilege": "Usuário comum altera alertas críticos."
    },
    "AWS-EFS": {
        "Spoofing": "Acesso indevido a sistemas de arquivos.",
        "Tampering": "Alteração maliciosa de arquivos compartilhados.",
        "Repudiation": "Dificuldade em rastrear modificações.",
        "Information Disclosure": "Arquivos confidenciais expostos.",
        "Denial of Service": "Bloqueio por consumo de IOPS.",
        "Elevation of Privilege": "Usuário sem permissão obtém leitura/escrita."
    },
    "AWS-ElastiCache": {
        "Spoofing": "Cliente falso acessa cache.",
        "Tampering": "Alteração de chaves e valores em cache.",
        "Repudiation": "Falta de trilhas de auditoria no cache.",
        "Information Disclosure": "Dados sensíveis armazenados sem criptografia.",
        "Denial of Service": "Exaustão de memória por chaves maliciosas.",
        "Elevation of Privilege": "Acesso root ao cluster Redis/Memcached."
    },
    "AWS-Key-Management-Service": {
        "Spoofing": "Solicitação falsa de chaves de criptografia.",
        "Tampering": "Alteração de políticas de chave.",
        "Repudiation": "Dificuldade em rastrear operações de chave.",
        "Information Disclosure": "Exposição de chaves privadas.",
        "Denial of Service": "Excesso de requisições KMS paralisa apps.",
        "Elevation of Privilege": "Usuário comum consegue gerar/excluir chaves."
    },
    "AWS-Private-subnet": {
        "Spoofing": "Máquina maliciosa dentro da subnet privada.",
        "Tampering": "Alteração de regras internas.",
        "Repudiation": "Falta de registros de tráfego interno.",
        "Information Disclosure": "Dados internos expostos sem VPN.",
        "Denial of Service": "Exaustão de recursos internos.",
        "Elevation of Privilege": "Máquina sem privilégio acessa rede restrita."
    },
    "AWS-Private_vpc": {
        "Spoofing": "Invasor imita dispositivo autorizado.",
        "Tampering": "Alteração maliciosa nas rotas da VPC.",
        "Repudiation": "Logs de tráfego ausentes.",
        "Information Disclosure": "Rotas internas expostas.",
        "Denial of Service": "Flood de tráfego interno.",
        "Elevation of Privilege": "VM comprometida obtém acesso privilegiado."
    },
    "AWS-Public-subnet": {
        "Spoofing": "Serviço falso na subnet pública.",
        "Tampering": "Alteração de tráfego público.",
        "Repudiation": "Logs incompletos de acessos externos.",
        "Information Disclosure": "Exposição de portas/serviços desnecessários.",
        "Denial of Service": "Sobrecarga em serviços públicos.",
        "Elevation of Privilege": "Serviço exposto usado como pivô de ataque."
    },
    "AWS-RDS": {
        "Spoofing": "Uso de credenciais de banco falsificadas.",
        "Tampering": "Injeção de SQL ou alteração de registros.",
        "Repudiation": "Ausência de trilhas de auditoria.",
        "Information Disclosure": "Exposição de dados confidenciais.",
        "Denial of Service": "Exaustão de conexões por queries pesadas.",
        "Elevation of Privilege": "Usuário comum ganha privilégios de admin."
    },
    "AWS-Region": {
        "Spoofing": "Tráfego redirecionado para região falsa.",
        "Tampering": "Alteração de configuração de replicação.",
        "Repudiation": "Logs inconsistentes entre regiões.",
        "Information Disclosure": "Exposição de dados replicados.",
        "Denial of Service": "Ataques em massa a uma região específica.",
        "Elevation of Privilege": "Acesso indevido a recursos inter-regionais."
    },
    "AWS-Res_Elastic-Load-Balancing_Application-Load-Balancer": {
        "Spoofing": "Cliente falso finge ser legítimo.",
        "Tampering": "Alteração maliciosa do tráfego roteado.",
        "Repudiation": "Falta de logs confiáveis de requisições.",
        "Information Disclosure": "Cabeçalhos ou erros expondo dados.",
        "Denial of Service": "Ataques volumétricos (DoS/DDoS).",
        "Elevation of Privilege": "Configuração incorreta permite bypass de regras."
    },
    "AWS-Res_Users": {
        "Spoofing": "Usuário falso se passa por legítimo.",
        "Tampering": "Modificação de dados enviados ao sistema.",
        "Repudiation": "Negação de ações realizadas.",
        "Information Disclosure": "Dados pessoais expostos.",
        "Denial of Service": "Tentativas massivas de login.",
        "Elevation of Privilege": "Usuário comum ganha acesso de administrador."
    },
    "AWS-Scaling-group": {
        "Spoofing": "Instâncias falsas entram no grupo.",
        "Tampering": "Alteração de políticas de escalonamento.",
        "Repudiation": "Falta de logs de escalonamento.",
        "Information Disclosure": "Exposição de métricas sensíveis.",
        "Denial of Service": "Escalonamento excessivo consome recursos.",
        "Elevation of Privilege": "Política incorreta gera acesso indevido."
    },
    "AWS-Shield": {
        "Spoofing": "Relatórios falsos de ataques.",
        "Tampering": "Modificação de regras de proteção.",
        "Repudiation": "Negação de incidentes registrados.",
        "Information Disclosure": "Dados de mitigação expostos.",
        "Denial of Service": "Falha proposital da proteção contra DoS.",
        "Elevation of Privilege": "Configuração incorreta dá acesso a defesas críticas."
    },
    "AWS-Simple-Email-Service": {
        "Spoofing": "Envio de e-mails falsos (phishing).",
        "Tampering": "Alteração de mensagens em trânsito.",
        "Repudiation": "Remetente nega envio de mensagens.",
        "Information Disclosure": "Exposição de listas de contatos.",
        "Denial of Service": "Flood de envios até bloquear SES.",
        "Elevation of Privilege": "Usuário comum envia em nome de domínios restritos."
    },
    "AWS-WAF": {
        "Spoofing": "Requisições falsas burlam o WAF.",
        "Tampering": "Alteração de regras de filtragem.",
        "Repudiation": "Logs de bloqueio inconsistentes.",
        "Information Disclosure": "Cabeçalhos expostos em respostas.",
        "Denial of Service": "Ataques não mitigados sobrecarregam serviços.",
        "Elevation of Privilege": "Configuração incorreta permite bypass total."
    },
    "Azure_api": {
        "Spoofing": "Chaves ou tokens de API falsificados.",
        "Tampering": "Manipulação das requisições/respostas.",
        "Repudiation": "Falta de logs detalhados de chamadas.",
        "Information Disclosure": "Respostas de API contendo informações sensíveis.",
        "Denial of Service": "Flood de chamadas para exaurir recursos.",
        "Elevation of Privilege": "API mal configurada permite comandos administrativos."
    },
    "Azure_api_gateway": {
        "Spoofing": "Cliente falso burla autenticação.",
        "Tampering": "Alteração de rotas e payloads.",
        "Repudiation": "Logs insuficientes de acessos.",
        "Information Disclosure": "Erros expõem detalhes internos.",
        "Denial of Service": "Excesso de requisições sobrecarrega APIs.",
        "Elevation of Privilege": "Configuração incorreta dá acesso irrestrito."
    },
    "Azure_cloud_services": {
        "Spoofing": "Serviço falso imita instância Azure.",
        "Tampering": "Alteração de código implantado.",
        "Repudiation": "Atividades não rastreadas.",
        "Information Disclosure": "Dados de configuração expostos.",
        "Denial of Service": "Falha proposital no balanceamento.",
        "Elevation of Privilege": "Usuário comum acessa funções administrativas."
    },
    "Azure_http": {
        "Spoofing": "Requisições forjadas com headers falsos.",
        "Tampering": "Manipulação de tráfego HTTP.",
        "Repudiation": "Logs de requisições ausentes.",
        "Information Disclosure": "URLs expõem parâmetros sensíveis.",
        "Denial of Service": "Flood de conexões HTTP.",
        "Elevation of Privilege": "Headers permitem escalonamento de acesso."
    },
    "Azure_integration-204-Logic-Apps": {
        "Spoofing": "Aplicativo falso executa workflows.",
        "Tampering": "Alteração de fluxos automatizados.",
        "Repudiation": "Execuções não rastreadas.",
        "Information Disclosure": "Dados processados expostos.",
        "Denial of Service": "Execuções massivas sobrecarregam serviço.",
        "Elevation of Privilege": "Workflow concede acesso indevido."
    },
    "Azure_management-portal": {
        "Spoofing": "Login falso imita portal oficial.",
        "Tampering": "Alteração de configurações críticas.",
        "Repudiation": "Ações administrativas não rastreadas.",
        "Information Disclosure": "Dados de gestão expostos.",
        "Denial of Service": "Sobrecarga de acessos ao portal.",
        "Elevation of Privilege": "Usuário comum vira administrador."
    },
    "Azure_microsoft_entra": {
        "Spoofing": "Identidade falsa burla autenticação.",
        "Tampering": "Manipulação de tokens de identidade.",
        "Repudiation": "Atividades de login não rastreadas.",
        "Information Disclosure": "Dados de identidade expostos.",
        "Denial of Service": "Tentativas massivas de login.",
        "Elevation of Privilege": "Escalonamento de privilégios via identidade."
    },
    "Azure_resource_group": {
        "Spoofing": "Recurso falso dentro do grupo.",
        "Tampering": "Alteração não autorizada de recursos.",
        "Repudiation": "Ações não registradas.",
        "Information Disclosure": "Dados de configuração expostos.",
        "Denial of Service": "Criação massiva de recursos esgota limites.",
        "Elevation of Privilege": "Permissões excessivas em recursos críticos."
    },
    "Azure_services": {
        "Spoofing": "Serviço falso se passa por oficial.",
        "Tampering": "Alteração de parâmetros de serviço.",
        "Repudiation": "Falta de rastreabilidade.",
        "Information Disclosure": "Dados internos expostos.",
        "Denial of Service": "Sobrecarga proposital do serviço.",
        "Elevation of Privilege": "Configuração incorreta dá acesso total."
    },
    "Azure_users": {
        "Spoofing": "Usuário falso se passa por legítimo.",
        "Tampering": "Alteração de credenciais.",
        "Repudiation": "Negação de ações.",
        "Information Disclosure": "Dados pessoais expostos.",
        "Denial of Service": "Múltiplas tentativas de login.",
        "Elevation of Privilege": "Usuário comum obtém privilégios administrativos."
    }
}

# ======================
# 2. Função IoU
# ======================
def calcular_iou(box1, box2):
    x_min_inter = max(box1[0], box2[0])
    y_min_inter = max(box1[1], box2[1])
    x_max_inter = min(box1[2], box2[2])
    y_max_inter = min(box1[3], box2[3])

    inter_width = max(0, x_max_inter - x_min_inter)
    inter_height = max(0, y_max_inter - y_min_inter)
    intersection_area = inter_width * inter_height

    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = box1_area + box2_area - intersection_area

    return 0 if union_area == 0 else intersection_area / union_area

def filtrar_deteccoes_por_iou(boxes, names_map, iou_threshold=0.5):
    sorted_boxes = sorted(boxes.tolist(), key=lambda b: float(b[4]), reverse=True)
    filtradas = []
    for box in sorted_boxes:
        is_overlapping = False
        for f_box in filtradas:
            if calcular_iou(box[:4], f_box[:4]) > iou_threshold:
                is_overlapping = True
                break
        if not is_overlapping:
            conf = float(box[4])
            cls_id = int(box[5])
            class_name = names_map[cls_id]
            filtradas.append(box + [class_name])
    return filtradas

# ======================
# 3. Carregar YOLO
# ======================
model_path = r"D:\_fiap\treinamentoModeloYolo\dataset\best.pt"
try:
    model = YOLO(model_path)
except Exception as e:
    print(f"❌ Erro ao carregar modelo: {e}")
    exit()

# ======================
# 4. Imagens a processar
# ======================
image_paths = [
    r"D:\_fiap\treinamentoModeloYolo\Arquiteturas Imagens\arch_azure.png",
    r"D:\_fiap\treinamentoModeloYolo\Arquiteturas Imagens\arch_aws.png"
]

try:
    font = ImageFont.truetype("arial.ttf", 20)
except IOError:
    font = ImageFont.load_default()

names_map = model.names

# ======================
# 5. Gerar Relatório
# ======================
# --- INÍCIO DA CORREÇÃO ---
# Define a pasta onde os relatórios e imagens serão salvos
OUTPUT_FOLDER = "analise_stride"

# Verifica se a pasta existe, se não, cria
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)
    print(f"✅ Pasta '{OUTPUT_FOLDER}' criada para salvar os relatórios.")
# --- FIM DA CORREÇÃO ---


markdown_report = "# Relatório de Ameaças STRIDE\n\n"
report_story = []
styles = getSampleStyleSheet()

for image_path in image_paths:
    if not os.path.exists(image_path):
        print(f"⚠️ Arquivo não encontrado: {image_path}")
        continue

    base_filename = os.path.basename(image_path)
    
    # --- CORREÇÃO: Usa o caminho completo para a imagem rotulada ---
    labeled_image_path = os.path.join(OUTPUT_FOLDER, f"labeled_{base_filename}")
    # --- FIM DA CORREÇÃO ---

    # Processar imagem e gerar a versão com anotações
    results = model.predict(source=image_path, conf=0.25, save=False, verbose=False)
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    deteccoes = filtrar_deteccoes_por_iou(results[0].boxes.data, names_map)
    legend_text = []

    for i, box_info in enumerate(deteccoes, start=1):
        x1, y1, x2, y2, conf, cls_id, class_name = box_info
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
        draw.text((x1, max(0, y1 - 25)), str(i), fill="red", font=font)
        legend_text.append(f"{i}: {class_name} ({conf:.2f})")

    line_height = 30
    extra_height = len(legend_text) * line_height + 20
    img_width, img_height = img.size
    new_img = Image.new("RGB", (img_width, img_height + extra_height), (255, 255, 255))
    new_img.paste(img, (0, 0))
    draw_new = ImageDraw.Draw(new_img)
    y_offset = img_height + 10
    for text in legend_text:
        draw_new.text((20, y_offset), text, fill="black", font=font)
        y_offset += line_height
    new_img.save(labeled_image_path)
    print(f"✅ Processado: {labeled_image_path}")

    # Adicionar seção ao relatório Markdown
    markdown_report += f"## Relatório para: `{base_filename}`\n\n"
    markdown_report += "---\n\n"
    
    # Adicionar seção ao relatório PDF
    report_story.append(Paragraph(f"## Relatório para: {base_filename}", styles['h2']))
    report_story.append(Spacer(1, 12))
    report_story.append(RLImage(labeled_image_path, width=400, height=300)) # Ajuste width/height conforme necessário
    report_story.append(Spacer(1, 12))

    for i, box_info in enumerate(deteccoes, start=1):
        x1, y1, x2, y2, conf, cls_id, class_name = box_info
        
        # Adicionar ameaças ao relatório Markdown e PDF
        if class_name in stride_mapping:
            markdown_report += f"### {class_name}\n"
            report_story.append(Paragraph(f"### {class_name}", styles['h3']))
            report_story.append(Spacer(1, 6))

            for threat, desc in stride_mapping[class_name].items():
                markdown_report += f"- **{threat}**: {desc}\n"
                story_paragraph = Paragraph(f"• <b>{threat}</b>: {desc}", styles['Normal'])
                report_story.append(story_paragraph)
                report_story.append(Spacer(1, 6))

            markdown_report += "\n"
    
    markdown_report += "---\n\n"
    report_story.append(Spacer(1, 24))

# ======================
# 6. Salvar arquivos
# ======================
# --- CORREÇÃO: Usa o caminho completo para salvar os arquivos finais ---
markdown_output_path = os.path.join(OUTPUT_FOLDER, "relatorio_stride.md")
pdf_output_path = os.path.join(OUTPUT_FOLDER, "relatorio_stride.pdf")

# Salvar Markdown
with open(markdown_output_path, "w", encoding="utf-8") as f:
    f.write(markdown_report)

# Salvar PDF
doc = SimpleDocTemplate(pdf_output_path)
doc.build(report_story)

print(f"📄 Relatórios gerados em '{OUTPUT_FOLDER}': {os.path.basename(markdown_output_path)} e {os.path.basename(pdf_output_path)}")
# --- FIM DA CORREÇÃO ---

import pdfplumber

pdf_path = "docs/LABORATÓRIO 01 - Características de repositórios populares.pdf"
pdf_path = "LabMedExp/Laboratorios/Lab-01/docs/LABORATÓRIO 01 - Características de repositórios populares.pdf"

with pdfplumber.open(pdf_path) as pdf:
    all_text = ""
    for page in pdf.pages:
        all_text += page.extract_text() + "\n"

# Exibe um trecho do conteúdo extraído
print(all_text[:1000])  # Mostra os primeiros 1000 caracteres
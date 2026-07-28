"""
===============================================================================
HISTORIAS QUE INSPIRAN® - APPS / API
Servicio de Generación de Reporte "Libro Vivo" en PDF
===============================================================================
"""

from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generar_pdf_libro_vivo(
    nombre_usuario: str, datos_libro: dict, datos_pasaporte: dict
) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    # Estilos Personalizados
    style_titulo = ParagraphStyle(
        "TituloDoc",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=colors.HexColor("#11998e"),
        spaceAfter=10,
    )

    style_subtitulo = ParagraphStyle(
        "SubtituloDoc",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=colors.HexColor("#2C3E50"),
        spaceAfter=12,
    )

    style_cuerpo = ParagraphStyle(
        "CuerpoTexto",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#333333"),
        spaceAfter=10,
    )

    story = []

    # 1. Encabezado del Documento
    story.append(Paragraph("🌱 Historias que Inspiran®", style_titulo))
    story.append(
        Paragraph(
            f"<b>Libro Vivo de Emprendimiento de:</b> {nombre_usuario}", style_subtitulo
        )
    )
    story.append(Spacer(1, 10))

    # 2. Tabla de Métricas del Pasaporte (Estilo Refinado)
    resumen_adn = datos_libro.get("resumen_adn", {})
    tabla_data = [
        ["Nivel Actual", "Experiencia Total", "Empresa / Proyecto"],
        [
            str(datos_pasaporte.get("nivel_actual", 1)),
            f"{datos_pasaporte.get('puntos_experiencia', 0)} XP",
            resumen_adn.get("nombre_empresa", "Maison Zerda"),
        ],
    ]

    t = Table(tabla_data, colWidths=[130, 140, 260])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#11998e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F8F9F9")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 20))

    # 3. Sección ADN de la Idea
    story.append(Paragraph("🧬 ADN del Proyecto", style_subtitulo))
    proposito = resumen_adn.get("proposito", "Sin propósito registrado.")
    story.append(Paragraph(f"<b>Propósito / Visión:</b> {proposito}", style_cuerpo))
    story.append(Spacer(1, 15))

    # 4. Capítulos Narrativos
    story.append(Paragraph("📖 Capítulos Forjados", style_subtitulo))
    capitulos = datos_libro.get("capitulos_narrativos", [])

    if not capitulos:
        story.append(Paragraph("No hay capítulos forjados aún.", style_cuerpo))
    else:
        for idx, cap in enumerate(capitulos, start=1):
            num = cap.get("capitulo", idx)
            narrativa = cap.get("narrativa", "")
            story.append(
                Paragraph(
                    f"<b>Capítulo {num}</b>",
                    ParagraphStyle(
                        "CapHead",
                        parent=style_subtitulo,
                        fontSize=12,
                        textColor=colors.HexColor("#16A085"),
                    ),
                )
            )
            story.append(Paragraph(narrativa, style_cuerpo))
            story.append(Spacer(1, 8))

    doc.build(story)
    buffer.seek(0)
    return buffer

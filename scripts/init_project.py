"""
===============================================================================
HISTORIAS QUE INSPIRAN® - SOF (Software Operating Framework)
Script de Inicialización de Estructura de Proyecto Empresarial v0.1.0
===============================================================================
"""

import os
from pathlib import Path

# Definición de la Jerarquía Corporativa del Proyecto
DIRECTORIOS = [
    # Capas Principales
    "backend/api",
    "backend/services",
    "backend/repositories",
    "backend/models",
    "backend/schemas",
    "backend/security",
    "backend/core",
    "backend/utils",
    "backend/database",
    "frontend/pages",
    "frontend/components",
    "frontend/animations",
    "frontend/avatars",
    "frontend/widgets",
    "frontend/styles",
    "frontend/sounds",
    "frontend/dialogs",
    "frontend/onboarding",
    "frontend/universe",
    "frontend/missions",
    "frontend/book",
    "frontend/passport",
    "docs/Software_Bible",
    "assets/images",
    "assets/audio",
    "assets/models_3d",
    "tests/unit",
    "tests/integration",
    "deployment/docker",
    "deployment/k8s",
    "scripts",
    "database/migrations",
    "ai/prompts",
    "ai/models",
    "game/engine",
    "universe/worlds",
    "branding/kit",
    "finances/calculators",
    "marketplace/catalog",
    "analytics/telemetry",
    ".github/workflows",
]

ARCHIVOS_BASE = {
    "VERSION": "0.1.0\n",
    "README.md": "# Historias que Inspiran® - Inspire Engine™\n\nSistema Operativo para Jóvenes Emprendedores.\n",
    "CHANGELOG.md": "# Changelog\n\n## [0.1.0] - 2026-07-26\n- Fundación de la arquitectura empresarial SOF.\n",
    "LICENSE.md": "Propiedad Intelectual Reservada - Historias que Inspiran® 2026.\n",
    "backend/__init__.py": "",
    "backend/api/__init__.py": "",
    "backend/services/__init__.py": "",
    "backend/repositories/__init__.py": "",
    "backend/models/__init__.py": "",
    "backend/schemas/__init__.py": "",
    "backend/core/__init__.py": "",
    "docs/Software_Bible/Vision.md": "# Visión de Historias que Inspiran®\n",
    "docs/Software_Bible/Architecture.md": "# Arquitectura del Inspire Engine™\n",
}


def construir_estudio():
    print("🚀 Construyendo la infraestructura de Historias que Inspiran®...")
    base_dir = Path.cwd()

    for folder in DIRECTORIOS:
        path = base_dir / folder
        path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Directorio verificado: {folder}")

    for file_path, content in ARCHIVOS_BASE.items():
        full_path = base_dir / file_path
        if not full_path.exists():
            full_path.write_text(content, encoding="utf-8")
            print(f"  ✓ Archivo creado: {file_path}")

    print("\n✨ ¡Estructura de Software Studio v0.1.0 inicializada con éxito!")


if __name__ == "__main__":
    construir_estudio()

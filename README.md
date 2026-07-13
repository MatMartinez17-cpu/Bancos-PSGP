# 📚 Bancos-PSGP — Banco de Exámenes UNI-FIEE

Repositorio oficial de exámenes, prácticas y material de estudio para los cursos
de la **Facultad de Ingeniería Eléctrica y Electrónica** de la
**Universidad Nacional de Ingeniería (UNI)**.

Este banco alimenta la plataforma **[PGSP-Tutor](https://github.com/MatMartinez17-cpu/pgsp-tutor)**
(Plataforma de Soporte Pedagógico con IA), un asistente académico inteligente
con búsqueda TF-IDF, recomendador híbrido y tutor matemático basado en SymPy.

---

## 📊 Contenido actual

### BMA02 — Cálculo Integral

| Tipo | Cantidad | Notas |
|---|---|---|
| Prueba de Entrada (PE) | 5 | 2023 - 2026 |
| Práctica Calificada 1 (PC1) | 27 | 2012 - 2026 |
| Práctica Calificada 2 (PC2) | 18 | 2012 - 2026 |
| Práctica Calificada 3 (PC3) | 9 | 2023 - 2026 |
| Práctica Calificada 4 (PC4) | 8 | 2023 - 2026 |
| Práctica Calificada 5 (PC5) | 8 | 2023 - 2026 |
| Examen Parcial (EP) | 21 | 2012 - 2026 |
| Examen Final (EF) | 8 | 2023 - 2026 |
| Sustitutorio | 3 | 2023 - 2025 |
| **Total evaluaciones** | **107** | |
| **Con solucionario** | **20** | 23 solucionarios distintos |
| Material de clase | 9 | Semanas de Vidal + cuadernos |

---

## 🗂️ Estructura del repositorio

```
Bancos-PSGP/
├── BMA02_Calculo_Integral/
│   ├── Prueba de Entrada/     ← 5 archivos
│   ├── PC1/                    ← 27 archivos
│   ├── PC2/                    ← 18 archivos
│   ├── PC3/                    ← 9 archivos
│   ├── PC4/                    ← 8 archivos
│   ├── PC5/                    ← 8 archivos
│   ├── Parcial/                ← 21 archivos
│   ├── Final/                  ← 8 archivos
│   ├── Susti/                  ← 3 archivos
│   └── Material/
│       ├── Clases Vidal 26-1/  ← Semanas de clases
│       └── Cuadernos/          ← Resúmenes de profesores
├── metadata_bma02.json         ← Metadata para PGSP-Tutor
├── scripts/
│   ├── comprimir_pdfs.py       ← Comprime PDFs pesados
│   └── generar_metadata.py     ← Regenera el JSON
└── README.md
```

---

## 🏷️ Convención de nombres

Los archivos siguen esta convención para permitir el parsing automático:

```
{TIPO} {CURSO} {PERIODO} [Sol by {AUTOR}].pdf
```

Donde:
- **TIPO**: `PC1`, `PC2`, `PC3`, `PC4`, `PC5`, `EP`, `EF`, `PE`, `Susti`
- **CURSO**: `BMA02` (código del curso)
- **PERIODO**: `AA-C` (ej: `25-2` = año 2025, ciclo 2)
- **`Sol by {AUTOR}`** o **`Sol por {AUTOR}`**: opcional, indica solucionario

**Ejemplos:**
```
PC5 BMA02 25-2.pdf                          → Enunciado PC5 2025-2
PC5 BMA02 25-2 Sol by Deyvi Villanueva.pdf  → Solucionario
EP BMA02 26-1 Sol por Axel Marquina.pdf     → Parcial con solucionario
```

---

## 🧠 Integración con PGSP-Tutor

Este banco se integra con el módulo **`BANCO_EXAMENES`** de PGSP-Tutor. Ejemplo
de uso en Python:

```python
import json
import requests

# Cargar el JSON de metadata directamente desde GitHub
url = "https://raw.githubusercontent.com/MatMartinez17-cpu/Bancos-PSGP/main/metadata_bma02.json"
metadata = requests.get(url).json()

# Consultar evaluaciones disponibles
for clave, evaluacion in metadata["evaluaciones"].items():
    print(f"{clave}: {evaluacion['nombre_curso']} - {len(evaluacion['soluciones'])} solucionarios")

# Descargar el enunciado de una evaluación
pc5 = metadata["evaluaciones"]["PC5 25-2"]
print(f"Enunciado: {pc5['enunciado']['url']}")
for sol in pc5["soluciones"]:
    print(f"Solución por {sol['autor']}: {sol['url']}")
```

---

## 🔄 Cómo actualizar el banco

Cuando agregues nuevos PDFs, regenera el JSON automáticamente:

```bash
# 1. Coloca los nuevos PDFs en la carpeta correspondiente respetando la nomenclatura
# 2. Comprime los que superen 90 MB
python scripts/comprimir_pdfs.py BMA02_Calculo_Integral BMA02_Calculo_Integral_comp --umbral 90

# 3. Regenera el metadata
python scripts/generar_metadata.py BMA02_Calculo_Integral metadata_bma02.json

# 4. Commit y push
git add .
git commit -m "Agregado: PC5 26-2 con solucionario"
git push origin main
```

---

## 📥 Cómo clonar/descargar

**Opción 1 — Clonar todo:**
```bash
git clone https://github.com/MatMartinez17-cpu/Bancos-PSGP.git
```

**Opción 2 — Descargar un solo archivo:**
Haz clic en el archivo y luego en el botón **"Download"** (o **"Raw"** → clic
derecho → **"Guardar enlace como…"**).

**Opción 3 — Solo el JSON (para integrar con tu app):**
```bash
curl -O https://raw.githubusercontent.com/MatMartinez17-cpu/Bancos-PSGP/main/metadata_bma02.json
```

---

## ✍️ Créditos

- **Recopilación**: Estudiantes de FIEE-UNI
- **Solucionarios**: Deyvi Villanueva, Axel Marquina, Fabrizio Valencia Casanova,
  Dereck Hurtado y otros contribuidores
- **Cuadernos**: Prof. Oria, Bryan Llontop
- **Clases**: Prof. Vidal (26-1)

---

## ⚖️ Licencia

Material académico compartido con fines educativos exclusivamente. Los
derechos de autoría intelectual pertenecen a los profesores y estudiantes
originales que produjeron el material. Este repositorio no busca ni obtiene
lucro económico, y respeta los usos justos permitidos por la ley peruana de
derechos de autor para fines educativos.

Si eres autor de algún material y deseas su retiro, contacta al mantenedor
del repositorio.

---

**Repositorio mantenido por**: [@MatMartinez17-cpu](https://github.com/MatMartinez17-cpu)

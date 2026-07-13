# 🔧 CÓMO ARREGLAR EL REPO Bancos-PSGP

## Problema actual

Tu repositorio `https://github.com/MatMartinez17-cpu/Bancos-PSGP` contiene por
error un archivo `pgsp-tutor.zip` (el proyecto de código), pero debería
contener los **exámenes de BMA02 Cálculo Integral**.

## Solución en 4 pasos

Vamos a:
1. Eliminar el ZIP incorrecto del repo
2. Subir la carpeta `BMA02_Calculo_Integral` con los 136 archivos organizados
3. Subir el `metadata_bma02.json` para integración con PGSP-Tutor
4. Subir el README profesional

---

## Paso 1 — Preparar tu computadora local

### 1.1 Instalar Git (si no lo tienes)
- Windows: descarga [Git for Windows](https://git-scm.com/download/win)
- Verifica: abre CMD/PowerShell y ejecuta:
  ```bash
  git --version
  ```

### 1.2 Clonar tu repositorio actual
Abre una carpeta de trabajo (por ejemplo `Documents/proyectos/`) y ejecuta:
```bash
cd Documents/proyectos
git clone https://github.com/MatMartinez17-cpu/Bancos-PSGP.git
cd Bancos-PSGP
```

### 1.3 Configurar Git con tu usuario (una sola vez)
```bash
git config --global user.name "MatMartinez17-cpu"
git config --global user.email "TU_EMAIL@ejemplo.com"
```

---

## Paso 2 — Limpiar el repo (eliminar el ZIP viejo)

Dentro de la carpeta `Bancos-PSGP` clonada:

```bash
# Eliminar el archivo incorrecto
git rm pgsp-tutor.zip

# Confirmar la eliminación
git commit -m "Eliminado pgsp-tutor.zip (archivo incorrecto)"
```

**No hagas push aún** — mejor subimos todo junto en un solo commit al final.

---

## Paso 3 — Copiar los archivos correctos

Descarga los archivos que te entregué:
- **Carpeta `BMA02_Calculo_Integral/`** (136 archivos, 149 MB) — todos los PDFs
- **`metadata_bma02.json`** (63 KB) — metadata para PGSP-Tutor
- **`README.md`** — descripción del repo
- **Carpeta `scripts/`** — utilidades para mantenimiento

Cópialos DENTRO de tu carpeta `Bancos-PSGP` local. Debe quedar así:

```
Bancos-PSGP/
├── .git/                           ← esto ya existe
├── BMA02_Calculo_Integral/         ← NUEVO (todos los PDFs)
├── metadata_bma02.json             ← NUEVO
├── README.md                       ← NUEVO
└── scripts/                        ← NUEVO
    ├── comprimir_pdfs.py
    └── generar_metadata.py
```

---

## Paso 4 — Subir todo a GitHub

Dentro de `Bancos-PSGP/`, ejecuta:

```bash
# Ver qué archivos nuevos se detectan
git status

# Agregar todo
git add .

# Confirmar los cambios
git commit -m "Añadido: banco completo BMA02 Cálculo Integral (107 exámenes + 9 materiales)"

# Subir al repositorio remoto
git push origin main
```

**⏱️ La subida puede tardar 5-15 minutos** porque son 149 MB. Ten paciencia.

---

## Verificación

Después del push, ve a `https://github.com/MatMartinez17-cpu/Bancos-PSGP`
y deberías ver:

- ✅ El README.md renderizado con la tabla de contenido
- ✅ La carpeta `BMA02_Calculo_Integral/` con las subcarpetas
- ✅ El archivo `metadata_bma02.json`
- ✅ La carpeta `scripts/`
- ✅ **NO** debe aparecer más `pgsp-tutor.zip`

---

## 🐛 Solución de problemas comunes

### "Error: file is larger than 100 MB"
Si algún archivo aún es mayor a 100 MB, ejecuta:
```bash
python scripts/comprimir_pdfs.py BMA02_Calculo_Integral BMA02_Calculo_Integral_comp --umbral 90
```
Luego reemplaza la carpeta original con la comprimida.

### "Authentication failed"
GitHub ya no permite passwords, necesitas un **Personal Access Token**:
1. Ve a https://github.com/settings/tokens
2. Genera un token con permiso `repo`
3. Cuando `git push` te pida contraseña, pega el token

### "This exceeds GitHub's file size limit"
Un archivo específico es demasiado grande. Comprímelo individualmente:
```bash
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
   -dNOPAUSE -dQUIET -dBATCH -sOutputFile=archivo_comprimido.pdf archivo_original.pdf
```

### El push tarda demasiado
Es normal con 149 MB. Si tarda más de 30 min, cancela (Ctrl+C) y prueba con
conexión más rápida.

---

## 🔄 Para agregar más cursos en el futuro (BMA01, BMA03, etc.)

1. Crea la carpeta correspondiente: `BMA01_Calculo_Diferencial/`
2. Sigue la misma nomenclatura: `{TIPO} {CURSO} {PERIODO}.pdf`
3. Regenera el metadata con:
   ```bash
   python scripts/generar_metadata.py BMA01_Calculo_Diferencial metadata_bma01.json
   ```
4. Commit y push

---

## 📞 Integración con PGSP-Tutor

Una vez que el repo esté subido, tu código PGSP-Tutor podrá cargar el metadata
directamente desde GitHub, sin necesidad de descargar los PDFs:

```python
import requests

url = "https://raw.githubusercontent.com/MatMartinez17-cpu/Bancos-PSGP/main/metadata_bma02.json"
metadata = requests.get(url).json()

# Todas las evaluaciones están indexadas y listas para el motor de búsqueda
print(f"Total evaluaciones BMA02: {metadata['estadisticas']['total_evaluaciones']}")
```

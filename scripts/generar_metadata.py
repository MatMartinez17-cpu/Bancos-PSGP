#!/usr/bin/env python3
"""
Genera un JSON de metadata a partir de los PDFs de BMA02 (Cálculo Integral).

El JSON tiene una estructura similar a BANCO_EXAMENES de PGSP-tutor,
listo para integrarse con la plataforma.

Uso:
    python generar_metadata.py <carpeta_pdfs> <archivo_salida.json>

Ejemplo:
    python generar_metadata.py BMA02_Calculo_Integral metadata_bma02.json
"""

import argparse
import json
import re
from pathlib import Path
from datetime import datetime


# ============================================================================
#  MAPEO DE TIPOS DE EVALUACIÓN
# ============================================================================
TIPOS_EVALUACION = {
    "PC1":     ("Practica",     1),
    "PC2":     ("Practica",     2),
    "PC3":     ("Practica",     3),
    "PC4":     ("Practica",     4),
    "PC5":     ("Practica",     5),
    "EP":      ("Parcial",      None),
    "EF":      ("Final",        None),
    "PE":      ("PruebaEntrada", None),
    "Susti":   ("Sustitutorio", None),
}

# URL base del repo (se personaliza al usar el script)
URL_BASE_REPO = "https://github.com/MatMartinez17-cpu/Bancos-PSGP/raw/main"


# ============================================================================
#  PARSING DEL NOMBRE DE ARCHIVO
# ============================================================================
def parsear_nombre_archivo(nombre: str) -> dict | None:
    """
    Extrae metadata del nombre de archivo.
    
    Ejemplos que reconoce:
        "PC5 BMA02 25-2.pdf"                                   → PC5 sin solucionario
        "PC5 BMA02 25-2 Sol by Deyvi Villanueva.pdf"           → PC5 con solucionario
        "EP BMA02 26-1 Sol por Valencia Casanova Fabrizio.pdf" → Parcial con solucionario
        "Susti BMA02 23-1.pdf"                                 → Sustitutorio
    """
    nombre_sin_ext = nombre.rsplit(".", 1)[0]
    
    # Detectar el tipo de evaluación al inicio
    tipo_evaluacion = None
    numero = None
    for prefijo, (tipo, num) in TIPOS_EVALUACION.items():
        if nombre_sin_ext.startswith(prefijo + " "):
            tipo_evaluacion = tipo
            numero = num
            resto = nombre_sin_ext[len(prefijo):].strip()
            break
    
    if tipo_evaluacion is None:
        return None   # no es un archivo de evaluación reconocido
    
    # Debe contener BMA02 después del prefijo
    if not resto.startswith("BMA02"):
        return None
    resto = resto[len("BMA02"):].strip()
    
    # Extraer el periodo (formato AA-C: año-ciclo, ej: "25-2", "26-1")
    match_periodo = re.match(r"(\d{2})-(\d)\s*(.*)", resto)
    if not match_periodo:
        return None
    
    anno = "20" + match_periodo.group(1)
    ciclo = match_periodo.group(2)
    periodo = f"{match_periodo.group(1)}-{ciclo}"
    resto = match_periodo.group(3).strip()
    
    # Detectar solucionario y autor
    es_solucionario = False
    autor_solucion = None
    profesor = None
    
    # Patrones típicos:
    #   "Sol by Autor"    → solucionario
    #   "Sol por Autor"   → solucionario
    #   "Solucionario"    → solucionario sin autor
    #   "(Prof. Xxx)"     → sin solución, dice el profesor
    match_sol = re.match(r"Sol(?:ucionario)?\s*(?:by|por)\s+(.+)", resto, re.IGNORECASE)
    if match_sol:
        es_solucionario = True
        autor_solucion = match_sol.group(1).strip().rstrip(".").strip()
    elif re.match(r"Solucionario\s*$", resto, re.IGNORECASE):
        es_solucionario = True
    
    match_prof = re.search(r"\(Prof\.\s*([^)]+)\)", resto)
    if match_prof:
        profesor = match_prof.group(1).strip()
    
    return {
        "curso":              "BMA02",
        "nombre_curso":       "Cálculo Integral",
        "tipo_evaluacion":    tipo_evaluacion,
        "numero_practica":    numero,
        "periodo":            periodo,
        "anno":               anno,
        "ciclo":              int(ciclo),
        "es_solucionario":    es_solucionario,
        "autor_solucion":     autor_solucion,
        "profesor":           profesor,
    }


def parsear_material(nombre: str, ruta_relativa: str) -> dict | None:
    """Parsea archivos de la carpeta Material (clases, cuadernos)."""
    nombre_sin_ext = nombre.rsplit(".", 1)[0]
    
    # Semanas de clases: "BMA02 SEMANA X 26-1.pdf" o "BMA02 SEMANA 6-7-8-9-10.pdf"
    match_semana = re.match(r"BMA02\s+SEMANA\s+([\d\-]+)(?:\s+(\d{2})-(\d))?", nombre_sin_ext)
    if match_semana:
        semana = match_semana.group(1)
        periodo = f"{match_semana.group(2)}-{match_semana.group(3)}" if match_semana.group(2) else None
        # Si no hay periodo en el nombre, inferirlo de la carpeta ("Clases Vidal 26-1")
        if not periodo:
            match_carpeta = re.search(r"(\d{2})-(\d)", ruta_relativa)
            if match_carpeta:
                periodo = f"{match_carpeta.group(1)}-{match_carpeta.group(2)}"
        return {
            "curso":              "BMA02",
            "nombre_curso":       "Cálculo Integral",
            "tipo_recurso":       "ClaseSemanal",
            "semana":             semana,
            "periodo":            periodo,
            "profesor":           "Vidal" if "Vidal" in ruta_relativa else None,
            "descripcion":        f"Clase de la semana {semana}",
        }
    
    # Cuadernos/resúmenes
    match_resumen = re.match(r"Resumen\s+Cálculo\s+Integral\s*\(By\s+(.+)\)", nombre_sin_ext, re.IGNORECASE)
    if match_resumen:
        return {
            "curso":              "BMA02",
            "nombre_curso":       "Cálculo Integral",
            "tipo_recurso":       "Cuaderno",
            "autor":              match_resumen.group(1).strip().rstrip(".").strip(),
            "descripcion":        "Cuaderno/resumen del curso",
        }
    
    return None


# ============================================================================
#  RECORRIDO DE LA CARPETA
# ============================================================================
def escanear_carpeta(carpeta_base: Path, url_base_repo: str) -> dict:
    """
    Escanea toda la carpeta y genera el diccionario de metadata.
    """
    if not carpeta_base.exists():
        raise FileNotFoundError(f"No existe: {carpeta_base}")
    
    evaluaciones = {}     # organizadas por clave "TIPO PERIODO"
    materiales   = []     # material de clases y cuadernos
    errores      = []
    
    for archivo in sorted(carpeta_base.rglob("*")):
        if not archivo.is_file():
            continue
        if archivo.suffix.lower() not in {".pdf", ".jpg", ".jpeg", ".png"}:
            continue
        ruta_relativa = archivo.relative_to(carpeta_base)
        subcarpeta = ruta_relativa.parts[0] if len(ruta_relativa.parts) > 1 else ""
        
        # Determinar si es evaluación o material
        if subcarpeta == "Material":
            data = parsear_material(archivo.name, str(ruta_relativa))
            if data:
                data["ruta_relativa"] = str(ruta_relativa).replace("\\", "/")
                data["url"] = f"{url_base_repo}/{data['ruta_relativa'].replace(' ', '%20')}"
                data["tamanio_kb"] = round(archivo.stat().st_size / 1024, 1)
                materiales.append(data)
            else:
                errores.append(f"Material no reconocido: {ruta_relativa}")
            continue
        
        # Evaluaciones (PC, EP, EF, PE, Susti)
        data = parsear_nombre_archivo(archivo.name)
        if not data:
            errores.append(f"No reconocido: {ruta_relativa}")
            continue
        
        # Datos adicionales del archivo
        data["nombre_archivo"] = archivo.name
        data["ruta_relativa"]  = str(ruta_relativa).replace("\\", "/")
        data["url"]            = f"{url_base_repo}/{data['ruta_relativa'].replace(' ', '%20')}"
        data["tamanio_kb"]     = round(archivo.stat().st_size / 1024, 1)
        
        # Clave: agrupa cada evaluación única
        # Ej: "PC5 25-2" reúne el enunciado + sus solucionarios
        prefijo = archivo.name.split(" ")[0]  # PC5, EP, EF, PE, Susti
        clave = f"{prefijo} {data['periodo']}"
        
        if clave not in evaluaciones:
            evaluaciones[clave] = {
                "curso":            "BMA02",
                "nombre_curso":     "Cálculo Integral",
                "examen":           prefijo,
                "tipo_evaluacion":  data["tipo_evaluacion"],
                "numero_practica":  data["numero_practica"],
                "periodo":          data["periodo"],
                "anno":             data["anno"],
                "ciclo":            data["ciclo"],
                "enunciado":        None,
                "soluciones":       [],
                "profesor":         data["profesor"],
            }
        
        # ¿Es el enunciado (sin "Sol") o un solucionario?
        if data["es_solucionario"]:
            evaluaciones[clave]["soluciones"].append({
                "autor":         data["autor_solucion"],
                "url":           data["url"],
                "ruta":          data["ruta_relativa"],
                "tamanio_kb":    data["tamanio_kb"],
            })
        else:
            evaluaciones[clave]["enunciado"] = {
                "url":           data["url"],
                "ruta":          data["ruta_relativa"],
                "tamanio_kb":    data["tamanio_kb"],
            }
        
        # Actualizar profesor si aparece en algún archivo
        if data["profesor"] and not evaluaciones[clave].get("profesor"):
            evaluaciones[clave]["profesor"] = data["profesor"]
    
    # Ordenar evaluaciones por examen + año + ciclo
    def clave_orden(item):
        v = item[1]
        # PC1 antes que PC2, PE antes que EP, etc.
        orden_tipo = {"PE": 0, "PC1": 1, "PC2": 2, "PC3": 3, "PC4": 4, "PC5": 5,
                       "EP": 6, "EF": 7, "Susti": 8}
        return (v["anno"], v["ciclo"], orden_tipo.get(v["examen"], 99))
    
    evaluaciones_ordenadas = dict(sorted(evaluaciones.items(), key=clave_orden))
    
    # Estadísticas
    total_evaluaciones = len(evaluaciones_ordenadas)
    con_solucionario = sum(1 for e in evaluaciones_ordenadas.values() if e["soluciones"])
    total_soluciones = sum(len(e["soluciones"]) for e in evaluaciones_ordenadas.values())
    
    conteo_por_tipo = {}
    for e in evaluaciones_ordenadas.values():
        conteo_por_tipo[e["examen"]] = conteo_por_tipo.get(e["examen"], 0) + 1
    
    resultado = {
        "curso":               "BMA02",
        "nombre_curso":        "Cálculo Integral",
        "facultad":            "FIEE",
        "universidad":         "UNI",
        "url_base_repositorio": url_base_repo,
        "fecha_generacion":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "estadisticas": {
            "total_evaluaciones":        total_evaluaciones,
            "con_solucionario":          con_solucionario,
            "total_solucionarios":       total_soluciones,
            "total_materiales":          len(materiales),
            "conteo_por_tipo":           conteo_por_tipo,
        },
        "evaluaciones":  evaluaciones_ordenadas,
        "materiales":    materiales,
    }
    
    if errores:
        resultado["archivos_no_reconocidos"] = errores
    
    return resultado


# ============================================================================
#  PROGRAMA PRINCIPAL
# ============================================================================
def main():
    parser = argparse.ArgumentParser(description="Genera JSON de metadata de PDFs")
    parser.add_argument("entrada", help="Carpeta con los PDFs organizados")
    parser.add_argument("salida", help="Archivo JSON de salida")
    parser.add_argument("--url-base", default=URL_BASE_REPO,
                        help=f"URL base del repositorio (default: {URL_BASE_REPO})")
    args = parser.parse_args()
    
    carpeta = Path(args.entrada)
    salida = Path(args.salida)
    
    print(f"🔍 Escaneando: {carpeta}")
    print(f"🌐 URL base:   {args.url_base}")
    
    resultado = escanear_carpeta(carpeta, args.url_base)
    
    salida.parent.mkdir(parents=True, exist_ok=True)
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    
    stats = resultado["estadisticas"]
    print(f"\n✅ JSON generado: {salida}")
    print(f"   Tamaño: {salida.stat().st_size / 1024:.1f} KB")
    print(f"\n📊 Estadísticas:")
    print(f"   Total evaluaciones:     {stats['total_evaluaciones']}")
    print(f"   Con solucionario:       {stats['con_solucionario']}")
    print(f"   Total solucionarios:    {stats['total_solucionarios']}")
    print(f"   Total materiales:       {stats['total_materiales']}")
    print(f"\n   Por tipo:")
    for tipo, cnt in sorted(stats["conteo_por_tipo"].items()):
        print(f"      {tipo:<8} → {cnt}")
    
    if "archivos_no_reconocidos" in resultado:
        print(f"\n⚠️  {len(resultado['archivos_no_reconocidos'])} archivos no reconocidos:")
        for a in resultado["archivos_no_reconocidos"]:
            print(f"      • {a}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Comprime PDFs grandes para que quepan en GitHub (< 100 MB).

Usa Ghostscript para reducir el peso manteniendo legibilidad.
Solo comprime archivos que superan el umbral configurado.

Uso:
    python comprimir_pdfs.py <carpeta_entrada> <carpeta_salida> [--umbral MB]

Ejemplo:
    python comprimir_pdfs.py "BMA02 Calculo Integral" "BMA02_final" --umbral 90
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


# Configuración de Ghostscript para reducir tamaño
# /screen  → muy comprimido (72 dpi) — para lectura en pantalla, pierde calidad
# /ebook   → moderado (150 dpi) — balance calidad/tamaño ★ RECOMENDADO
# /printer → alta calidad (300 dpi) — comprime poco
# /prepress → máxima calidad — comprime casi nada
PERFIL_COMPRESION = "/ebook"


def comprimir_pdf(entrada: Path, salida: Path, perfil: str = PERFIL_COMPRESION) -> bool:
    """
    Comprime un PDF usando Ghostscript.
    Retorna True si tuvo éxito.
    """
    try:
        cmd = [
            "gs", "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={perfil}",
            "-dNOPAUSE", "-dQUIET", "-dBATCH",
            f"-sOutputFile={salida}",
            str(entrada),
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=300)
        return result.returncode == 0 and salida.exists()
    except (subprocess.TimeoutExpired, Exception) as e:
        print(f"   ⚠️  Error: {e}")
        return False


def procesar_carpeta(carpeta_entrada: Path, carpeta_salida: Path,
                     umbral_mb: float = 90.0):
    """
    Copia todos los PDFs de la carpeta de entrada a la de salida.
    Los que superan 'umbral_mb' se comprimen automáticamente.
    """
    if not carpeta_entrada.exists():
        print(f"❌ No existe la carpeta: {carpeta_entrada}")
        sys.exit(1)
    
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    
    # Estadísticas
    total_archivos = 0
    total_original = 0
    total_final = 0
    comprimidos = []
    copiados = 0
    errores = []
    
    print(f"📁 Origen:  {carpeta_entrada}")
    print(f"📁 Destino: {carpeta_salida}")
    print(f"📏 Umbral de compresión: {umbral_mb} MB")
    print(f"⚙️  Perfil Ghostscript:  {PERFIL_COMPRESION}")
    print("─" * 70)
    
    # Recorrer todos los archivos manteniendo estructura de carpetas
    for archivo in sorted(carpeta_entrada.rglob("*")):
        if not archivo.is_file():
            continue
        
        # Ruta relativa para mantener la misma estructura
        ruta_relativa = archivo.relative_to(carpeta_entrada)
        destino = carpeta_salida / ruta_relativa
        destino.parent.mkdir(parents=True, exist_ok=True)
        
        tam_mb = archivo.stat().st_size / 1_048_576
        total_archivos += 1
        total_original += archivo.stat().st_size
        
        # Solo procesamos PDFs; el resto lo copiamos tal cual
        if archivo.suffix.lower() != ".pdf":
            shutil.copy2(archivo, destino)
            total_final += destino.stat().st_size
            copiados += 1
            continue
        
        if tam_mb <= umbral_mb:
            # No necesita compresión, solo copiar
            shutil.copy2(archivo, destino)
            total_final += destino.stat().st_size
            copiados += 1
        else:
            # Comprimir
            print(f"🗜️  Comprimiendo ({tam_mb:.1f} MB): {ruta_relativa}")
            exito = comprimir_pdf(archivo, destino)
            if exito:
                nuevo_tam = destino.stat().st_size / 1_048_576
                reduc_pct = 100 * (1 - nuevo_tam / tam_mb)
                comprimidos.append({
                    "archivo": str(ruta_relativa),
                    "original_mb": tam_mb,
                    "final_mb": nuevo_tam,
                    "reduccion_pct": reduc_pct,
                })
                total_final += destino.stat().st_size
                print(f"   ✅ {tam_mb:.1f} MB → {nuevo_tam:.1f} MB "
                      f"(reducción: {reduc_pct:.1f}%)")
            else:
                # Si falla la compresión, copiar el original
                shutil.copy2(archivo, destino)
                total_final += destino.stat().st_size
                errores.append(str(ruta_relativa))
                print(f"   ❌ Error al comprimir, copiado el original")
    
    # Reporte final
    print("\n" + "═" * 70)
    print("  RESUMEN")
    print("═" * 70)
    print(f"📊 Archivos totales:      {total_archivos}")
    print(f"   Copiados sin cambio:  {copiados}")
    print(f"   Comprimidos:          {len(comprimidos)}")
    print(f"   Errores:              {len(errores)}")
    print(f"\n💾 Tamaño original:      {total_original / 1_048_576:>8.1f} MB")
    print(f"💾 Tamaño final:         {total_final / 1_048_576:>8.1f} MB")
    if total_original > 0:
        ahorro = 100 * (1 - total_final / total_original)
        print(f"💾 Ahorro total:         {ahorro:>8.1f}%")
    
    if comprimidos:
        print(f"\n🗜️  Detalle de compresiones:")
        for c in comprimidos:
            print(f"   • {c['archivo']}")
            print(f"     {c['original_mb']:.1f} MB → {c['final_mb']:.1f} MB "
                  f"({c['reduccion_pct']:.1f}% menos)")
    
    if errores:
        print(f"\n⚠️  Errores en:")
        for e in errores:
            print(f"   • {e}")
    
    # Verificación: ¿algún archivo sigue > 100 MB?
    print("\n🔍 Verificación GitHub (límite 100 MB por archivo):")
    grandes = []
    for archivo in carpeta_salida.rglob("*.pdf"):
        tam_mb = archivo.stat().st_size / 1_048_576
        if tam_mb > 100:
            grandes.append((archivo.relative_to(carpeta_salida), tam_mb))
    
    if grandes:
        print(f"   ❌ Aún hay {len(grandes)} archivo(s) sobre 100 MB:")
        for ruta, tam in grandes:
            print(f"      • {ruta} ({tam:.1f} MB)")
        print(f"\n   💡 Estos archivos NECESITAN Git LFS. Ejecuta:")
        print(f"      git lfs install")
        print(f"      git lfs track \"*.pdf\"  # o especifica solo los pesados")
    else:
        print(f"   ✅ Todos los archivos son < 100 MB (aptos para Git normal)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Comprime PDFs pesados para GitHub")
    parser.add_argument("entrada", help="Carpeta con los PDFs originales")
    parser.add_argument("salida", help="Carpeta destino con PDFs comprimidos")
    parser.add_argument("--umbral", type=float, default=90.0,
                        help="Tamaño en MB a partir del cual se comprime (default: 90)")
    args = parser.parse_args()
    
    procesar_carpeta(Path(args.entrada), Path(args.salida), umbral_mb=args.umbral)

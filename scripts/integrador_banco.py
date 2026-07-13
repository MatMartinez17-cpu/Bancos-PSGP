"""
================================================================================
  INTEGRADOR BANCOS-PSGP ↔ PGSP-TUTOR
================================================================================

Módulo que carga el metadata del repositorio Bancos-PSGP y lo convierte al
formato que espera BANCO_EXAMENES de PGSP-Tutor.

Puedes usarlo de dos formas:

  A) DESCARGAR EL JSON ONLINE (recomendado, siempre actualizado)
     integrador = IntegradorBancoPSGP.desde_github()
     
  B) DESDE UN ARCHIVO LOCAL (offline)
     integrador = IntegradorBancoPSGP.desde_archivo("metadata_bma02.json")

Luego lo integras con tu plataforma:

  banco_bma02 = integrador.a_banco_examenes()
  BANCO_EXAMENES.update(banco_bma02)   # ya tienes los 107 exámenes
================================================================================
"""

import json
import urllib.request
from pathlib import Path
from typing import Optional


URL_METADATA_BMA02 = (
    "https://raw.githubusercontent.com/MatMartinez17-cpu/Bancos-PSGP/"
    "main/metadata_bma02.json"
)


class IntegradorBancoPSGP:
    """
    Carga y transforma el metadata de Bancos-PSGP para PGSP-Tutor.
    """
    
    def __init__(self, metadata: dict):
        self.metadata = metadata
        self.curso = metadata.get("curso", "BMA02")
        self.nombre_curso = metadata.get("nombre_curso", "Cálculo Integral")
    
    # ─────────────────────────────────────────────────────────────
    #  CONSTRUCTORES
    # ─────────────────────────────────────────────────────────────
    @classmethod
    def desde_github(cls, url: str = URL_METADATA_BMA02, timeout: int = 15):
        """Descarga el metadata directamente desde GitHub."""
        print(f"📥 Descargando metadata desde: {url}")
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            print(f"✅ Metadata descargado ({len(data.get('evaluaciones', {}))} evaluaciones)")
            return cls(data)
        except Exception as e:
            print(f"❌ Error al descargar: {e}")
            print("   Verifica tu conexión o usa desde_archivo() con un JSON local.")
            raise
    
    @classmethod
    def desde_archivo(cls, ruta: str):
        """Carga el metadata desde un archivo JSON local."""
        ruta = Path(ruta)
        if not ruta.exists():
            raise FileNotFoundError(f"No existe: {ruta}")
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(data)
    
    # ─────────────────────────────────────────────────────────────
    #  CONVERSIÓN AL FORMATO BANCO_EXAMENES
    # ─────────────────────────────────────────────────────────────
    def a_banco_examenes(self) -> dict:
        """
        Convierte el metadata al formato BANCO_EXAMENES de PGSP-tutor.
        
        Formato de salida (igual al que usa PGSP-tutor):
            {
                "pc5 25-2": {
                    "curso": "BMA02",
                    "nombre_curso": "Cálculo Integral",
                    "examen": "PC5",
                    "periodo": "25-2",
                    "url_enunciado": "https://...",
                    "solucionarios": [{"autor": "...", "url": "..."}],
                    "problemas": []   ← vacío por defecto; se llena manualmente
                },
                ...
            }
        """
        banco = {}
        for clave, ev in self.metadata.get("evaluaciones", {}).items():
            # La clave en PGSP-tutor va en minúsculas: "pc5 25-2"
            clave_pgsp = clave.lower()
            
            entrada = {
                "curso":            ev["curso"],
                "nombre_curso":     ev["nombre_curso"],
                "examen":           ev["examen"],
                "periodo":          ev["periodo"],
                "anno":             ev.get("anno"),
                "ciclo":            ev.get("ciclo"),
                "tipo_evaluacion":  ev.get("tipo_evaluacion"),
                "numero_practica":  ev.get("numero_practica"),
                "profesor":         ev.get("profesor"),
                "url_enunciado":    ev["enunciado"]["url"] if ev.get("enunciado") else None,
                "solucionarios":    [
                    {"autor": s["autor"], "url": s["url"]}
                    for s in ev.get("soluciones", [])
                ],
                "problemas":        [],   # se llena manualmente cuando se digitalizan
            }
            banco[clave_pgsp] = entrada
        
        return banco
    
    # ─────────────────────────────────────────────────────────────
    #  BÚSQUEDAS RÁPIDAS
    # ─────────────────────────────────────────────────────────────
    def buscar(self, examen: Optional[str] = None,
                periodo: Optional[str] = None,
                con_solucionario: bool = False) -> list:
        """
        Busca evaluaciones con filtros opcionales.
        
        Ejemplos:
            integrador.buscar(examen="PC5")               → todas las PC5
            integrador.buscar(periodo="26-1")             → todo lo del 2026-1
            integrador.buscar(examen="EP", con_solucionario=True)
        """
        resultados = []
        for clave, ev in self.metadata.get("evaluaciones", {}).items():
            if examen and ev["examen"] != examen:
                continue
            if periodo and ev["periodo"] != periodo:
                continue
            if con_solucionario and not ev.get("soluciones"):
                continue
            resultados.append((clave, ev))
        return resultados
    
    def resumen(self) -> str:
        """Retorna un resumen legible del banco."""
        stats = self.metadata.get("estadisticas", {})
        return (
            f"📊 BANCO BMA02 (Cálculo Integral)\n"
            f"   Total evaluaciones:      {stats.get('total_evaluaciones', '?')}\n"
            f"   Con solucionario:        {stats.get('con_solucionario', '?')}\n"
            f"   Total solucionarios:     {stats.get('total_solucionarios', '?')}\n"
            f"   Total materiales:        {stats.get('total_materiales', '?')}\n"
            f"   Por tipo: {stats.get('conteo_por_tipo', {})}\n"
        )


# ============================================================================
#  DEMO
# ============================================================================
def demo():
    """
    Muestra cómo usar el integrador. Descarga el JSON online, lo transforma,
    y hace algunas consultas de prueba.
    """
    print("═" * 70)
    print("  DEMO: INTEGRADOR BANCOS-PSGP  ↔  PGSP-TUTOR")
    print("═" * 70)
    
    # 1) Cargar (opción A: online, opción B: local)
    try:
        integrador = IntegradorBancoPSGP.desde_github()
    except Exception:
        print("\n⚠️  Sin conexión, cargando de archivo local...")
        integrador = IntegradorBancoPSGP.desde_archivo("metadata_bma02.json")
    
    # 2) Resumen
    print("\n" + integrador.resumen())
    
    # 3) Convertir al formato BANCO_EXAMENES
    banco = integrador.a_banco_examenes()
    print(f"✅ Formato BANCO_EXAMENES generado: {len(banco)} entradas\n")
    
    # 4) Ejemplos de consultas
    print("─" * 70)
    print("Ejemplo 1: PC5 25-2")
    print("─" * 70)
    if "pc5 25-2" in banco:
        ev = banco["pc5 25-2"]
        print(f"   Curso:     {ev['nombre_curso']}")
        print(f"   Enunciado: {ev['url_enunciado']}")
        for s in ev["solucionarios"]:
            print(f"   Sol por {s['autor']}: {s['url']}")
    
    print()
    print("─" * 70)
    print("Ejemplo 2: Todos los parciales con solucionario")
    print("─" * 70)
    parciales_con_sol = integrador.buscar(examen="EP", con_solucionario=True)
    print(f"   Encontrados: {len(parciales_con_sol)}")
    for clave, ev in parciales_con_sol[:5]:
        autores = ", ".join(s["autor"] or "Anónimo" for s in ev["soluciones"])
        print(f"   • {clave} — sol por: {autores}")
    
    print()
    print("─" * 70)
    print("Ejemplo 3: Todo lo del ciclo 26-1")
    print("─" * 70)
    ciclo_actual = integrador.buscar(periodo="26-1")
    print(f"   Encontrados: {len(ciclo_actual)}")
    for clave, ev in ciclo_actual:
        cnt_sol = len(ev.get("soluciones", []))
        marca = f"({cnt_sol} sol)" if cnt_sol else ""
        print(f"   • {clave} {marca}")
    
    # 5) Cómo integrar con PGSP-tutor
    print()
    print("─" * 70)
    print("Ejemplo 4: Integración con PGSP-Tutor")
    print("─" * 70)
    print("   from pgsp_tutor import BANCO_EXAMENES")
    print("   from integrador_banco import IntegradorBancoPSGP")
    print("   ")
    print("   integrador = IntegradorBancoPSGP.desde_github()")
    print("   BANCO_EXAMENES.update(integrador.a_banco_examenes())")
    print("   # ¡Ahora PGSP-tutor tiene acceso a las 107 evaluaciones!")


if __name__ == "__main__":
    demo()

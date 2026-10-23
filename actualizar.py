#!/usr/bin/env python3
"""Lee los próximos sorteos de la web oficial de Loterías y Apuestas del Estado
y guarda el bote y la fecha de cada juego en botes.json."""
import json, sys, urllib.request, datetime

JUEGOS = ["LNAC", "LAQU", "EMIL", "ELGR", "LAPR", "QGOL", "BONO", "LOTU", "EDMS", "QUPL"]
URL = "https://www.loteriasyapuestas.es/servicios/proximosv3?game_id={}&num=5"
UA = "Mozilla/5.0 (compatible; botes-kiosco; +https://github.com/kioscoisi/botes-kiosco)"

try:
    previo = json.load(open("botes.json", encoding="utf-8"))
except Exception:
    previo = {"juegos": {}}

ahora = datetime.datetime.now(datetime.timezone.utc)
salida = {"juegos": {}, "errores": {}}
ok = 0
for c in JUEGOS:
    try:
        req = urllib.request.Request(URL.format(c), headers={"User-Agent": UA, "Accept": "application/json"})
        filas = json.load(urllib.request.urlopen(req, timeout=30))
        abierto = next((f for f in filas if f.get("estado") == "abierto"), None)
        ok += 1
        if abierto:
            bote = abierto.get("premio_bote")
            salida["juegos"][c] = {
                "fecha": abierto["fecha"][:10],
                "cierre": abierto["cierre"][:19],
                "bote": int(bote) if bote else 0,
            }
        else:
            salida["juegos"][c] = None
    except Exception as e:
        salida["errores"][c] = str(e)[:120]
        salida["juegos"][c] = previo.get("juegos", {}).get(c)  # conserva el último dato bueno

print("Juegos leídos:", ok, "de", len(JUEGOS))
for c, e in salida["errores"].items():
    print("ERROR", c, e)
if ok == 0:
    sys.exit(1)  # que el robot salga en rojo si no se pudo leer nada

# solo reescribe el archivo si cambian los datos (evita commits inútiles)
if previo.get("juegos") != salida["juegos"] or previo.get("errores") != salida["errores"]:
    salida["actualizado"] = ahora.strftime("%Y-%m-%d %H:%M:%S UTC")
    json.dump(salida, open("botes.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    print("botes.json actualizado")
else:
    print("Sin cambios")

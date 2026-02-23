---
description: Limpia memoria caché muerta, deshechos de compilación y optimiza la lectura de disco local.
---

Este workflow es muy útil cuando Windows se queda atrapado por archivos `.pyc` corruptos, los puertos se cuelgan o el instalador Vite acumula cachés huérfanas en el disco duro.

// turbo-all

1. Limpiar toda la caché piramidal generada por Python (Bytecode obsoleto)
```powershell
Get-ChildItem -Path . -Include __pycache__ -Recurse -Hidden | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Include *.pyc -Recurse -Hidden | Remove-Item -Force -ErrorAction SilentlyContinue
```

2. Verifica si quedan procesos silenciosos de Python atascados en memoria en Windows
```powershell
Get-Process python -ErrorAction SilentlyContinue | Select-Object Id, CPU, StartTime
```

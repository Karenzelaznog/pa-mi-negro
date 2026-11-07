# Quita el fondo blanco de todas las imágenes PNG de la carpeta img/ (excepto fondo.jpg)
# Uso:  pip install pillow numpy   y luego   python quitar_fondo.py
import glob
from collections import deque
import numpy as np
from PIL import Image

def quitar(path, umbral=232):
    im = Image.open(path).convert("RGBA")
    a = np.array(im)
    h, w = a.shape[:2]
    claro = (a[..., :3] >= umbral).all(axis=2) | (a[..., 3] == 0)
    fondo = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if claro[y, x] and not fondo[y, x]: fondo[y, x] = True; q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if claro[y, x] and not fondo[y, x]: fondo[y, x] = True; q.append((y, x))
    while q:  # solo se borra el blanco conectado con el borde (los ojos y dientes se conservan)
        y, x = q.popleft()
        for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and claro[ny, nx] and not fondo[ny, nx]:
                fondo[ny, nx] = True; q.append((ny, nx))
    borde = np.zeros_like(fondo)  # suaviza el halo blanco de 1-2 píxeles
    for _ in range(2):
        d = fondo.copy()
        d[1:] |= fondo[:-1]; d[:-1] |= fondo[1:]; d[:, 1:] |= fondo[:, :-1]; d[:, :-1] |= fondo[:, 1:]
        borde |= d & ~fondo & (a[..., :3] >= 200).all(axis=2)
        fondo = fondo | borde
    a[fondo, 3] = 0
    Image.fromarray(a).save(path)
    print("listo:", path)

for f in glob.glob("img/*.png"):
    quitar(f)

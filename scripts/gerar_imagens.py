#!/usr/bin/env python3
"""Gera ícones (favicon PNG/ICO, Apple) e imagens de partilha (Open Graph, 1200×630 JPEG).
Uso: python3 scripts/gerar_imagens.py  (só cria o que falta; apagar o ficheiro para o refazer)
Precisa de Pillow. As imagens de partilha vêm das fotografias reais em assets/.
"""
import pathlib
from PIL import Image, ImageOps

RAIZ = pathlib.Path(__file__).resolve().parent.parent
A = RAIZ / "assets"

# Fotografia original de cada chave usada nas páginas (scripts/gerar_paginas.py, dicionário F)
OG = {
    "gaia_largo": "foto-real-20260915-162859.jpeg", "gaia_rolo": "telhado-real-04.jpeg", "gaia_obra": "foto-real-20260915-162840.jpeg",
    "gaia_vista": "foto-real-20260915-161005.jpeg", "gaia_juntas": "foto-real-20260915-161418.jpeg", "gaia_remate": "foto-real-20260915-161929.jpeg",
    "cobertura_mineral": "obra-real-cobertura-02.webp", "cobertura_remates": "telhado-real-01.jpeg", "cobertura_ralo": "telhado-real-02.jpeg",
    "terraco_grua": "foto-real-20260917-01.jpeg", "terraco_claraboia": "foto-real-20260917-02.jpeg", "terraco_passadico": "foto-real-20260909-151643.jpeg",
    "murete": "obra-terraco-1.webp", "parede_maquina": "parede-real-03.jpeg", "parede_imperalum": "parede-real-01.jpeg", "parede_fundacao": "parede-real-02.jpeg",
    "aroeira": "caso-aroeira-3000m2.webp", "ericeira": "caso-ericeira-200m2.webp", "gaia_caso": "caso-gaia-440m2.webp",
}


def icones():
    logo = Image.open(A / "logo-impermeabilizapro.webp").convert("RGB")
    for nome, tam in (("favicon-48.png", 48), ("favicon-192.png", 192), ("apple-touch-icon.png", 180)):
        p = A / nome
        if not p.exists():
            logo.resize((tam, tam), Image.LANCZOS).save(p, optimize=True)
    ico = RAIZ / "favicon.ico"
    if not ico.exists():
        logo.save(ico, sizes=[(16, 16), (32, 32), (48, 48)])


def partilha():
    (A / "og").mkdir(exist_ok=True)
    for chave, origem in OG.items():
        p = A / "og" / f"{chave}.jpg"
        if p.exists():
            continue
        im = Image.open(A / origem).convert("RGB")
        ImageOps.fit(im, (1200, 630), Image.LANCZOS, centering=(0.5, 0.55)).save(p, "JPEG", quality=78, optimize=True, progressive=True)


if __name__ == "__main__":
    icones()
    partilha()
    print("Ícones e imagens de partilha prontos.")

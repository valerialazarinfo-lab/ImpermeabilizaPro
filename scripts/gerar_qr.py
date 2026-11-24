#!/usr/bin/env python3
"""Gera assets/qr-avaliar.png: código QR para https://impermeabilizapro.pt/avaliar/ (propostas, faturas, cartões).

Aponta para o endereço curto do site, não para o link do Google: se o link do Google mudar, só se muda REVIEW_URL
no gerador e os QR já impressos continuam a funcionar. Precisa de: pip install "qrcode[pil]".
Uso: python3 scripts/gerar_qr.py
"""
import pathlib

import qrcode

RAIZ = pathlib.Path(__file__).resolve().parent.parent
qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=24, border=4)
qr.add_data("https://impermeabilizapro.pt/avaliar/")
qr.make(fit=True)
qr.make_image(fill_color="#0a2340", back_color="white").save(RAIZ / "assets" / "qr-avaliar.png")
print("assets/qr-avaliar.png gerado.")

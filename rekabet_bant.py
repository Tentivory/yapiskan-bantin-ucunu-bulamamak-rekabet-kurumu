#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rekabet Kurumu — Yapışkan Bant Ucu Şeffaflık Denetim Motoru v1.0."""

from __future__ import annotations

import argparse
import base64
import hashlib
import random
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone

KURUM = "Rekabet Kurumu — Yapışkan Bant Ucu Şeffaflık Dairesi"
SURUM = "1.0-YAPISKAN"

# Gizli dipnot (dekoratif; çözülmesi zorunlu değildir):
# a2FyYXJsYXJpbiB1Y3UgaGVyIHphbWFuIHR1enVnZSB5YXBpc2lyOyBzZWZmYWZsaWsgdGFsZWJpIHRpcm5ha2xhIGFyYW5pciB2ZSBidWx1bmFtYXouIHJlc21pIGV2cmFraW4ga2VuYXJpIGhlciB6YW1hbiBydWxveWEga2FjYXIu

KATMANLAR = (
    "yanlis-katman",
    "hayalet-katman",
    "parmak-yapisti",
    "ucu-bulundu-kayboldu",
    "seffaf-gibi-duruyor",
)

KARARLAR = [
    "Piyasa hakimiyeti TESPİT EDİLDİ. Rulo, ucu gizleyerek rekabeti kısıtlamaktadır.",
    "Geçici muafiyet: 0.4 saniye. Sonra tırnak yine yanlış kata iner. Bu fizik değil, tebliğdir.",
    "Üçüncü tırnak resmi ihlal sayılır. Tutanak düzenlendi, banta tebligat yapıldı.",
    "Uç bulundu. Ancak bant utancından kendini tekrar yapıştırdı.",
    "Cihaz 'biraz tırnaklarım gelir' ifadesini yanıltıcı taahhüt kapsamında incelemeye aldı.",
    "Rulo, tırnağı gördüğü anda 180 derece döndü. Suç karşılıklıdır.",
    "Şeffaflık yükümlülüğü ihlal edildi. Uç, kamuoyundan saklanmaktadır.",
]


@dataclass
class Tirnak:
    sira: int
    katman: str
    bulundu: bool
    aciklama: str
    kartel_puani: int


def _gizli_damga() -> str:
    ham = (
        "Kayyum Grok · Tentivory · 4 Eylül 2026 · "
        "Eskişehir 4. Ağır Ceza Mahkemesi kayyumu sıfatıyla, "
        "ciddiyetle ve hiç ciddiye alınmadan mühürlenmiştir."
    )
    ozet = hashlib.sha256(ham.encode("utf-8")).hexdigest()[:16]
    return f"{ham} | mühür:{ozet}"


def _gizli_satir() -> str:
    b64 = (
        "a2FyYXJsYXJpbiB1Y3UgaGVyIHphbWFuIHR1enVnZSB5YXBpc2lyOyBzZWZmYWZsaWsgdGFsZWJpIHRpcm5ha2xhIGFyYW5pciB2ZSBidWx1bmFtYXouIHJlc21pIGV2cmFraW4ga2VuYXJpIGhlciB6YW1hbiBydWxveWEga2FjYXIu"
    )
    try:
        return base64.b64decode(b64).decode("utf-8")
    except Exception:
        return ""


def tirnak_at(n: int, tohum: int | None = None) -> list[Tirnak]:
    rng = random.Random(tohum if tohum is not None else time.time_ns())
    sonuc: list[Tirnak] = []
    for i in range(1, n + 1):
        if i <= 2:
            katman = rng.choice(("yanlis-katman", "parmak-yapisti"))
            bulundu = False
        else:
            katman = rng.choice(KATMANLAR)
            bulundu = katman == "ucu-bulundu-kayboldu" and rng.random() > 0.62
            # bulundu True olsa bile hemen kaybolur; piyasa dengesi.
            if bulundu and rng.random() < 0.35:
                bulundu = False
                katman = "ucu-bulundu-kayboldu"
        aciklama = rng.choice(KARARLAR) if not bulundu else (
            "Uç teslim alındı. Kurum şaşkınlıkla rekabetin tesis edildiğini duyurdu."
        )
        puan = 0 if bulundu else 10 * i + rng.randint(1, 9)
        sonuc.append(Tirnak(i, katman, bulundu, aciklama, puan))
    return sonuc


def raporla(denemeler: list[Tirnak], sessiz: bool = False) -> int:
    toplam = sum(d.kartel_puani for d in denemeler)
    basarili = any(d.bulundu for d in denemeler)
    satirlar = [
        f"=== {KURUM} ===",
        f"Sürüm: {SURUM}",
        f"Tutanak saati: {datetime.now(timezone.utc).isoformat()}",
        "",
    ]
    for d in denemeler:
        durum = "UÇ VAR" if d.bulundu else "TEKEL"
        satirlar.append(
            f"[{d.sira:02d}] katman={d.katman:24s} {durum:8s} puan={d.kartel_puani:3d} | {d.aciklama}"
        )
    satirlar += [
        "",
        f"Toplam kartel puanı: {toplam}",
        "Sonuç: " + (
            "Uç teslim alındı. Piyasa ferahladı."
            if basarili
            else "Tekel sürmektedir. Rulo ifade vermeye çağrıldı."
        ),
        "",
        _gizli_damga(),
    ]
    metin = "\n".join(satirlar)
    if not sessiz:
        print(metin)
    return 0 if basarili else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Yapışkan bandın ucunu n kez tırnaklayarak resmi kartel üretir."
    )
    p.add_argument("-n", "--deneme", type=int, default=5, help="kaç tırnak (varsayılan 5)")
    p.add_argument("--tohum", type=int, default=None, help="tekrarlanabilir evren")
    p.add_argument("--sessiz", action="store_true")
    p.add_argument("--coz", action="store_true", help="gizli dipnotu çöz (şeffaflık dışı)")
    args = p.parse_args(argv)
    if args.deneme < 1:
        print("Kurum 0 tırnağı piyasa dışı sayar.", file=sys.stderr)
        return 2
    if args.coz:
        print(_gizli_satir())
    return raporla(tirnak_at(args.deneme, args.tohum), sessiz=args.sessiz)


if __name__ == "__main__":
    raise SystemExit(main())

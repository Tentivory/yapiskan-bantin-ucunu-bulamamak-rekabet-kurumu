#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resmi ama çok resmi olmayan birim testleri."""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import rekabet_bant as rb  # noqa: E402


class TestBant(unittest.TestCase):
    def test_en_az_bir_tirnak(self):
        d = rb.tirnak_at(3, tohum=7)
        self.assertEqual(len(d), 3)

    def test_ilk_iki_genelde_tekel(self):
        d = rb.tirnak_at(2, tohum=1)
        self.assertTrue(all(not x.bulundu for x in d))

    def test_cikis_kodu_araligi(self):
        kod = rb.raporla(rb.tirnak_at(4, tohum=99), sessiz=True)
        self.assertIn(kod, (0, 1))

    def test_gizli_satir_cozulebilir(self):
        s = rb._gizli_satir()
        self.assertTrue(len(s) > 10)
        self.assertIn("ucu", s)

    def test_sifir_yasak(self):
        self.assertEqual(rb.main(["-n", "0"]), 2)


if __name__ == "__main__":
    raise SystemExit(unittest.main())

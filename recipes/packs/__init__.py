# -*- coding: utf-8 -*-
"""업종 pack 레지스트리.

core 는 "업종이 바뀌어도 참인 것"만 담습니다(CLAUDE.md §D).
예약처럼 특정 업종에서만 성립하는 어휘는 여기 pack 으로 둡니다.
"""
import importlib, pathlib

def names():
    here = pathlib.Path(__file__).parent
    return sorted(f.stem for f in here.glob("*.py") if f.stem != "__init__")

def modules():
    return {n: importlib.import_module(f"recipes.packs.{n}") for n in names()}

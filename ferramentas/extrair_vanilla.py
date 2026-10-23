"""Extrai as texturas originais do seu Minecraft 1.8 para usar como base.

Uso:
    python ferramentas/extrair_vanilla.py                 # acha o .jar sozinho
    python ferramentas/extrair_vanilla.py --jar CAMINHO   # .jar específico
    python ferramentas/extrair_vanilla.py --pvp           # também copia as texturas de PvP para pack/
    python ferramentas/extrair_vanilla.py --servidor      # PvP + lã, céu, mobs, menus e tudo de servidor
    python ferramentas/extrair_vanilla.py --tudo          # todas as texturas do 1.8

Tudo vai para referencia/ (fora do pack, ignorado pelo git). Com --pvp, as
texturas mais importantes para PvP são copiadas para dentro de pack/ para
você editar por cima. Com --servidor, vai junto o resto do que aparece em
servidores (blocos de construção, lã, céu, mobs, menus, todos os itens). Com
--tudo, vão todas as texturas do jogo. Arquivos que já existem no pack nunca
são sobrescritos, a menos que você passe --sobrescrever.
"""

import argparse
import fnmatch
import sys
from pathlib import Path

from comum import REFERENCIA, TEXTURAS, TEXTURAS_PVP, TEXTURAS_SERVIDOR, achar_jar, ler_jar

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--jar", type=Path, help="caminho do 1.8.x.jar (padrão: procura em .minecraft/versions)")
    parser.add_argument("--pvp", action="store_true", help="copia as texturas de PvP para dentro de pack/")
    parser.add_argument("--servidor", action="store_true", help="copia as de PvP e todo o resto usado em servidores")
    parser.add_argument("--tudo", action="store_true", help="copia todas as texturas do jogo para dentro de pack/")
    parser.add_argument("--sobrescrever", action="store_true", help="com --pvp/--servidor/--tudo, substitui arquivos que já existem no pack")
    args = parser.parse_args()

    jar = args.jar or achar_jar()
    if jar is None or not jar.is_file():
        sys.exit("Não achei o .jar do 1.8. Abra o 1.8.9 uma vez no launcher ou passe --jar CAMINHO.")
    print(f"Lendo {jar}")
    texturas = ler_jar(jar)
    if not texturas:
        sys.exit("Esse .jar não tem assets/minecraft/textures/. Ele é mesmo do 1.8?")

    for nome, dados in texturas.items():
        destino = REFERENCIA / nome
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(dados)
    print(f"{len(texturas)} arquivos extraídos para {REFERENCIA}")

    if not (args.pvp or args.servidor or args.tudo):
        return

    if args.tudo:
        padroes = ["*"]
    else:
        padroes = TEXTURAS_PVP + (TEXTURAS_SERVIDOR if args.servidor else [])
    selecionados = set()
    for padrao in padroes:
        encontrados = {n for n in texturas if fnmatch.fnmatchcase(n, padrao)}
        if not encontrados:
            print(f"  (nenhum arquivo no jar casa com {padrao})")
        selecionados |= encontrados

    copiados = pulados = 0
    for nome in sorted(selecionados):
        destino = TEXTURAS / nome
        if destino.exists() and not args.sobrescrever:
            pulados += 1
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(texturas[nome])
        copiados += 1
        print(f"  + {nome}")
    print(f"{copiados} arquivos copiados para o pack ({pulados} já existiam e foram mantidas)")


if __name__ == "__main__":
    main()

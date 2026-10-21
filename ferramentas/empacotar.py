"""Confere o pack e gera dist/MajesticDiamond.zip pronto para o Minecraft 1.6.

Uso:
    python ferramentas/empacotar.py                # confere e gera o zip
    python ferramentas/empacotar.py --jar CAMINHO  # confere os nomes contra o seu 1.6.x.jar
    python ferramentas/empacotar.py --instalar     # também copia o zip para .minecraft/resourcepacks
    python ferramentas/empacotar.py --forcar       # gera o zip mesmo com erros

Se o .jar do 1.6 for encontrado sozinho em .minecraft/versions, ele é usado
para conferir se cada arquivo do pack tem um nome que o jogo realmente usa.
"""

import argparse
import difflib
import io
import json
import shutil
import sys
import zipfile
from pathlib import Path

from comum import (DIST, NOME_ZIP, NOMES_1_7_PARA_1_6, PACK, TEXTURAS,
                   achar_jar, arquivos_do_pack, ler_jar, pastas_minecraft)

try:
    from PIL import Image
except ImportError:
    Image = None

# Texturas de 16x16 por "quadro"; as demais (gui, armadura...) só precisam
# manter a proporção do original.
PASTAS_QUADRADAS = ("blocks/", "items/")


class Relatorio:
    def __init__(self):
        self.erros = []
        self.avisos = []

    def erro(self, arquivo, msg):
        self.erros.append(f"{arquivo}: {msg}")

    def aviso(self, arquivo, msg):
        self.avisos.append(f"{arquivo}: {msg}")


def potencia_de_dois(n):
    return n > 0 and n & (n - 1) == 0


def escala_valida(tamanho, original):
    """True se tamanho = original x 2, 4, 8... (ou dividido por isso)."""
    maior, menor = max(tamanho, original), min(tamanho, original)
    return maior % menor == 0 and potencia_de_dois(maior // menor)


def conferir_mcmeta_do_pack(rel):
    caminho = PACK / "pack.mcmeta"
    if not caminho.is_file():
        rel.erro("pack.mcmeta", "não existe; sem ele o Minecraft não reconhece o pack")
        return
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        formato = dados["pack"]["pack_format"]
    except (ValueError, KeyError, TypeError) as e:
        rel.erro("pack.mcmeta", f"JSON inválido ({e})")
        return
    if formato != 1:
        rel.erro("pack.mcmeta", f"pack_format é {formato}, mas o 1.6 usa 1")


def conferir_imagem(rel, nome, caminho, vanilla):
    try:
        with Image.open(caminho) as img:
            img.load()
            largura, altura = img.size
            modo = img.mode
    except Exception as e:
        rel.erro(nome, f"não é um PNG válido ({e})")
        return

    if modo not in ("RGBA", "RGB", "P", "LA", "L"):
        rel.aviso(nome, f"modo de cor {modo}; salve como PNG RGBA para evitar problemas")

    if nome.startswith(PASTAS_QUADRADAS):
        if not potencia_de_dois(largura) or largura < 16:
            rel.erro(nome, f"largura {largura}px; use 16, 32, 64...")
        elif altura != largura:
            if altura % largura:
                rel.erro(nome, f"{largura}x{altura}: altura precisa ser múltipla da largura")
            elif not (caminho.parent / (caminho.name + ".mcmeta")).is_file():
                rel.erro(nome, f"{largura}x{altura} é uma animação, mas falta {caminho.name}.mcmeta")
        return

    if vanilla is None:
        return
    with Image.open(io.BytesIO(vanilla)) as original:
        vl, va = original.size
    if largura * va != altura * vl:
        rel.erro(nome, f"{largura}x{altura}, mas o original é {vl}x{va}; mantenha a proporção")
    elif not escala_valida(largura, vl):
        rel.aviso(nome, f"{largura}x{altura}: use o tamanho original ({vl}x{va}) multiplicado por 2, 4, 8...")


def conferir_arquivos(rel, texturas_jar):
    arquivos = arquivos_do_pack()
    if not (PACK / "pack.png").is_file():
        rel.aviso("pack.png", "sem ícone; o pack aparece com o ícone padrão na lista")

    for caminho in arquivos:
        relativo = caminho.relative_to(PACK).as_posix()
        if caminho.suffix != caminho.suffix.lower():
            rel.erro(relativo, "extensão em maiúsculas; o jogo só acha .png/.mcmeta minúsculos")
            continue
        if caminho.suffix == ".mcmeta":
            try:
                json.loads(caminho.read_text(encoding="utf-8"))
            except ValueError as e:
                rel.erro(relativo, f"JSON inválido ({e})")
        if not caminho.is_relative_to(TEXTURAS):
            continue

        nome = caminho.relative_to(TEXTURAS).as_posix()
        if nome in NOMES_1_7_PARA_1_6:
            rel.erro(nome, f"nome do 1.7+; no 1.6 o arquivo se chama {NOMES_1_7_PARA_1_6[nome]}")
            continue
        if texturas_jar is not None and nome not in texturas_jar:
            parecidos = difflib.get_close_matches(nome, texturas_jar.keys(), n=3)
            dica = f" Você quis dizer: {', '.join(parecidos)}?" if parecidos else ""
            rel.erro(nome, f"o 1.6 não usa esse arquivo, então ele será ignorado.{dica}")
            continue
        if caminho.suffix == ".png" and Image is not None:
            conferir_imagem(rel, nome, caminho, texturas_jar.get(nome) if texturas_jar else None)
    return arquivos


def gerar_zip(arquivos):
    DIST.mkdir(exist_ok=True)
    destino = DIST / NOME_ZIP
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zf:
        for caminho in arquivos:
            # pack.mcmeta precisa ficar na raiz do zip, não dentro de uma pasta
            zf.write(caminho, caminho.relative_to(PACK).as_posix())
    return destino


def instalar(zip_gerado):
    for pasta in pastas_minecraft():
        if pasta.is_dir():
            destino = pasta / "resourcepacks"
            destino.mkdir(exist_ok=True)
            shutil.copy2(zip_gerado, destino / zip_gerado.name)
            return destino / zip_gerado.name
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--jar", type=Path, help="caminho do 1.6.x.jar para conferir os nomes")
    parser.add_argument("--instalar", action="store_true", help="copia o zip para .minecraft/resourcepacks")
    parser.add_argument("--forcar", action="store_true", help="gera o zip mesmo com erros")
    args = parser.parse_args()

    jar = args.jar or achar_jar()
    if args.jar and not args.jar.is_file():
        sys.exit(f"Arquivo não encontrado: {args.jar}")
    texturas_jar = ler_jar(jar) if jar else None
    if jar:
        print(f"Conferindo nomes contra {jar}")
    else:
        print("Aviso: .jar do 1.6 não encontrado; os nomes dos arquivos não serão conferidos (use --jar).")
    if Image is None:
        print("Aviso: Pillow não instalado; tamanhos das imagens não serão conferidos (pip install pillow).")

    rel = Relatorio()
    conferir_mcmeta_do_pack(rel)
    arquivos = conferir_arquivos(rel, texturas_jar)

    for msg in rel.avisos:
        print(f"  aviso: {msg}")
    for msg in rel.erros:
        print(f"  ERRO:  {msg}")
    total = sum(1 for p in arquivos if p.suffix == ".png")
    print(f"{total} PNGs no pack, {len(rel.erros)} erro(s), {len(rel.avisos)} aviso(s)")

    if rel.erros and not args.forcar:
        sys.exit("Corrija os erros acima (ou use --forcar) para gerar o zip.")

    zip_gerado = gerar_zip(arquivos)
    print(f"Pack gerado: {zip_gerado}")
    if args.instalar:
        instalado = instalar(zip_gerado)
        print(f"Instalado em {instalado}" if instalado else "Não achei a pasta .minecraft para instalar.")


if __name__ == "__main__":
    main()

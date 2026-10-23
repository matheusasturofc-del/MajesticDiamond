"""Confere o pack e gera dist/MajesticDiamond.zip pronto para o Minecraft 1.8.

Uso:
    python ferramentas/empacotar.py             # confere e gera o zip
    python ferramentas/empacotar.py --instalar  # também copia o zip para .minecraft/resourcepacks
    python ferramentas/empacotar.py --forcar    # gera o zip mesmo com erros

Os nomes e tamanhos são conferidos contra a lista de texturas do 1.8
(texturas_1_8.txt), então não precisa do .jar.
"""

import argparse
import difflib
import json
import shutil
import sys
import zipfile

from comum import (DIST, NOME_ZIP, PACK, TEXTURAS, arquivos_do_pack,
                   ler_lista_1_8, pastas_minecraft, sugerir_nome_1_8)

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
        rel.erro("pack.mcmeta", f"pack_format é {formato}, mas o 1.8 usa 1")


def conferir_imagem(rel, nome, caminho, tamanho_original):
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

    if tamanho_original is None:
        return
    vl, va = tamanho_original
    if largura * va != altura * vl:
        rel.erro(nome, f"{largura}x{altura}, mas o original é {vl}x{va}; mantenha a proporção")
    elif not escala_valida(largura, vl):
        rel.aviso(nome, f"{largura}x{altura}: use o tamanho original ({vl}x{va}) multiplicado por 2, 4, 8...")


def conferir_arquivos(rel, texturas_1_8):
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
        if nome not in texturas_1_8:
            sugestao = sugerir_nome_1_8(nome)
            if sugestao in texturas_1_8:
                rel.erro(nome, f"nome de outra versão; no 1.8 o arquivo se chama {sugestao}")
            else:
                parecidos = difflib.get_close_matches(nome, texturas_1_8.keys(), n=3)
                dica = f" Você quis dizer: {', '.join(parecidos)}?" if parecidos else ""
                rel.erro(nome, f"o 1.8 não usa esse arquivo, então ele será ignorado.{dica}")
            continue
        if caminho.suffix == ".png" and Image is not None:
            conferir_imagem(rel, nome, caminho, texturas_1_8[nome])
    return arquivos


def ler_properties(caminho):
    valores = {}
    for linha in caminho.read_text(encoding="utf-8", errors="replace").splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#") and "=" in linha:
            chave, _, valor = linha.partition("=")
            valores[chave.strip()] = valor.strip()
    return valores


def conferir_ceu(rel):
    """Skybox do OptiFine: assets/minecraft/mcpatcher/sky/world<N>/sky<N>.properties + imagem 3x2."""
    pasta_mc = PACK / "assets" / "minecraft"
    for mundo in sorted((pasta_mc / "mcpatcher" / "sky").glob("world*")):
        numeros = sorted(int(p.stem[3:]) for p in mundo.glob("sky*.properties") if p.stem[3:].isdigit())
        for anterior, numero in zip(numeros, numeros[1:]):
            if numero != anterior + 1:
                rel.aviso(mundo.relative_to(PACK).as_posix(),
                          f"falta sky{anterior + 1}.properties; o OptiFine para de procurar no primeiro número que faltar")
        for numero in numeros:
            props = mundo / f"sky{numero}.properties"
            nome = props.relative_to(PACK).as_posix()
            fonte = ler_properties(props).get("source", f"./sky{numero}.png")
            if fonte.startswith("./"):
                imagem = mundo / fonte[2:]
            elif fonte.startswith("~/"):
                imagem = pasta_mc / "mcpatcher" / fonte[2:]
            else:
                imagem = pasta_mc / fonte.split(":", 1)[-1]
            if not imagem.is_file():
                rel.erro(nome, f"a imagem do céu {fonte} não existe")
                continue
            if Image is None:
                continue
            with Image.open(imagem) as img:
                largura, altura = img.size
            if largura * 2 != altura * 3:
                rel.erro(imagem.relative_to(PACK).as_posix(),
                         f"{largura}x{altura}; o céu precisa ter os 6 lados em 3x2 (largura = 1,5 x altura, ex.: 768x512)")


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
    parser.add_argument("--instalar", action="store_true", help="copia o zip para .minecraft/resourcepacks")
    parser.add_argument("--forcar", action="store_true", help="gera o zip mesmo com erros")
    args = parser.parse_args()

    if Image is None:
        print("Aviso: Pillow não instalado; tamanhos das imagens não serão conferidos (pip install pillow).")

    rel = Relatorio()
    conferir_mcmeta_do_pack(rel)
    arquivos = conferir_arquivos(rel, ler_lista_1_8())
    conferir_ceu(rel)

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

"""Gera a skybox (céu personalizado) do pack e os moldes para desenhar o céu.

Uso:
    python ferramentas/gerar_ceu.py                 # cria o céu de exemplo (se ainda não existir) e os moldes
    python ferramentas/gerar_ceu.py --sobrescrever  # recria o céu de exemplo por cima do seu

O céu personalizado é um recurso do OptiFine. Funciona no Lunar Client, no
Badlion e em quem joga com OptiFine; sem ele, o jogo mostra o céu azul normal.

Arquivos criados no pack (formato do OptiFine para o 1.8):
  assets/minecraft/mcpatcher/sky/world0/sky1.png         a imagem do céu (6 lados em 3x2)
  assets/minecraft/mcpatcher/sky/world0/sky1.properties  como o jogo mostra a imagem

Moldes (em moldes/):
  ceu_molde.png  do tamanho do céu, cada lado de uma cor, para desenhar por cima
  ceu_guia.png   o mesmo com o nome de cada lado, a linha do horizonte e o norte
"""

import argparse
import math
import random

from PIL import Image, ImageDraw

from comum import PACK, RAIZ

LADO = 256  # pixels de cada lado do cubo; a imagem fica com 3x2 lados
PASTA_CEU = PACK / "assets" / "minecraft" / "mcpatcher" / "sky" / "world0"
MOLDES = RAIZ / "moldes"

# Posição de cada lado na imagem (coluna, linha), como na documentação do OptiFine.
LADOS = {
    "baixo": (0, 0), "cima": (1, 0), "sul": (2, 0),
    "oeste": (0, 1), "norte": (1, 1), "leste": (2, 1),
}

# Sem horários de fade o céu aparece o dia todo; replace troca o céu azul inteiro;
# rotate=false deixa o céu parado; o weather padrão do OptiFine é só tempo limpo.
PROPRIEDADES = """\
# Céu do Majestic Diamond (OptiFine: Lunar Client, Badlion ou OptiFine).
# A imagem tem os 6 lados do céu em 3 colunas x 2 linhas:
#   baixo | cima  | sul
#   oeste | norte | leste
# Veja moldes/ceu_guia.png para saber onde vai cada lado.
source=./sky1.png
blend=replace
rotate=false
weather=clear rain thunder
"""

# Degradê do céu pela altura (graus acima do horizonte): abaixo do horizonte escuro,
# brilho turquesa no horizonte, roxo no meio e índigo no alto.
DEGRADE = [
    (-90, (6, 9, 16)), (-8, (9, 14, 26)), (0, (36, 150, 150)), (6, (56, 120, 160)),
    (18, (74, 44, 138)), (45, (34, 24, 92)), (90, (24, 18, 70)),
]


def cor_do_ceu(elevacao):
    for (e0, c0), (e1, c1) in zip(DEGRADE, DEGRADE[1:]):
        if elevacao <= e1:
            t = (elevacao - e0) / (e1 - e0)
            t = t * t * (3 - 2 * t)  # suaviza a passagem entre as cores
            return tuple(round(a + (b - a) * t) for a, b in zip(c0, c1))
    return DEGRADE[-1][1]


def elevacao(lado, u, v):
    """Ângulo acima do horizonte (graus) do ponto (u, v) de um lado, com u e v de -1 a 1."""
    if lado == "cima":
        return math.degrees(math.atan2(1, math.hypot(u, v)))
    if lado == "baixo":
        return -math.degrees(math.atan2(1, math.hypot(u, v)))
    return math.degrees(math.atan2(-v, math.hypot(u, 1)))  # nos lados, o topo da imagem é o céu


def desenhar_lado(lado, sorteio):
    img = Image.new("RGBA", (LADO, LADO))
    px = img.load()
    for y in range(LADO):
        for x in range(LADO):
            u, v = (x + .5) / LADO * 2 - 1, (y + .5) / LADO * 2 - 1
            px[x, y] = cor_do_ceu(elevacao(lado, u, v)) + (255,)
    # estrelas: mais no alto, nenhuma abaixo do horizonte nem colada na borda (para não cortar ao meio)
    for y in range(3, LADO - 3):
        for x in range(3, LADO - 3):
            u, v = (x + .5) / LADO * 2 - 1, (y + .5) / LADO * 2 - 1
            e = elevacao(lado, u, v)
            if e < 4 or sorteio.random() > 0.0035 * min(1, (e - 4) / 35):
                continue
            brilho = sorteio.uniform(.45, 1)
            cor = (round(190 + 65 * brilho), round(220 + 35 * brilho), 255, 255)
            px[x, y] = cor
            if brilho > .93:  # algumas estrelas maiores, em forma de brilho de diamante
                meia = tuple(round(c * .55 + b * .45) for c, b in zip(cor, px[x + 2, y])) [:3] + (255,)
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    px[x + dx, y + dy] = meia
    return img


def gerar_ceu():
    ceu = Image.new("RGBA", (LADO * 3, LADO * 2))
    sorteio = random.Random(1789)  # sempre o mesmo céu de exemplo
    for lado, (col, lin) in LADOS.items():
        ceu.paste(desenhar_lado(lado, sorteio), (col * LADO, lin * LADO))
    return ceu


CORES_MOLDE = {
    "baixo": (70, 70, 80), "cima": (90, 170, 255), "sul": (240, 190, 60),
    "oeste": (60, 210, 140), "norte": (240, 100, 90), "leste": (170, 120, 255),
}
NOMES = {"baixo": "BAIXO (chao)", "cima": "CIMA", "sul": "SUL", "oeste": "OESTE", "norte": "NORTE", "leste": "LESTE"}


def gerar_moldes():
    molde = Image.new("RGBA", (LADO * 3, LADO * 2))
    guia = Image.new("RGBA", (LADO * 3, LADO * 2 + 40), (40, 40, 40, 255))
    dm, dg = ImageDraw.Draw(molde), ImageDraw.Draw(guia)
    for lado, (col, lin) in LADOS.items():
        x0, y0 = col * LADO, lin * LADO
        caixa = [x0, y0, x0 + LADO - 1, y0 + LADO - 1]
        cor = CORES_MOLDE[lado] + (255,)
        dm.rectangle(caixa, fill=cor)
        dg.rectangle(caixa, fill=cor, outline=(0, 0, 0, 255), width=2)
        if lado not in ("cima", "baixo"):
            # horizonte no meio: em cima é céu, embaixo é o que fica abaixo do horizonte
            for alvo in (dm, dg):
                alvo.line([x0, y0 + LADO // 2, x0 + LADO - 1, y0 + LADO // 2], fill=(255, 255, 255, 255), width=2)
            dg.text((x0 + 8, y0 + LADO // 2 - 16), "horizonte", fill=(255, 255, 255, 255))
        dg.text((x0 + 8, y0 + 8), NOMES[lado], fill=(0, 0, 0, 255))
    # onde fica o norte nos lados de cima e de baixo
    dg.text((LADO // 2 - 3, 24), "N", fill=(255, 255, 255, 255))
    dg.text((LADO + LADO // 2 - 3, LADO - 30), "N", fill=(255, 255, 255, 255))
    dg.text((10, LADO * 2 + 12), "Cada lado: o topo do quadrado e o ceu, a linha branca e o horizonte. Cima e baixo: N = lado do norte.",
            fill=(230, 230, 230, 255))
    MOLDES.mkdir(exist_ok=True)
    molde.save(MOLDES / "ceu_molde.png")
    guia.save(MOLDES / "ceu_guia.png")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sobrescrever", action="store_true", help="recria o céu de exemplo por cima do que já existe")
    args = parser.parse_args()

    PASTA_CEU.mkdir(parents=True, exist_ok=True)
    imagem = PASTA_CEU / "sky1.png"
    if imagem.exists() and not args.sobrescrever:
        print(f"{imagem} já existe; mantive o seu céu (use --sobrescrever para recriar o exemplo).")
    else:
        gerar_ceu().save(imagem)
        print(f"Céu de exemplo salvo em {imagem}")
    propriedades = PASTA_CEU / "sky1.properties"
    if not propriedades.exists() or args.sobrescrever:
        propriedades.write_text(PROPRIEDADES, encoding="utf-8")
    gerar_moldes()
    print(f"Moldes salvos em {MOLDES}")


if __name__ == "__main__":
    main()

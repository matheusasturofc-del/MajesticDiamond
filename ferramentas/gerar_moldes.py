"""Gera os moldes (mapas UV) da armadura em moldes/.

Uso:
    python ferramentas/gerar_moldes.py

Cria, para cada camada da armadura:
  - moldes/armadura_camada_N.png       64x32, cada face pintada de uma cor.
    Abra no editor como camada de fundo e desenhe por cima.
  - moldes/armadura_camada_N_guia.png  ampliado 8x, com o nome de cada face.

Camada 1 (diamond_layer_1.png): capacete (cabeça), peitoral (corpo + braços), botas (pernas).
Camada 2 (diamond_layer_2.png): calça (corpo + pernas).
"""

from PIL import Image, ImageDraw

from comum import RAIZ

MOLDES = RAIZ / "moldes"
ESCALA = 8

# Caixas do modelo do jogador (ModelBiped), textura 64x32:
# (nome, u, v, largura, altura, profundidade)
# Os textos ficam sem acento porque a fonte padrão do Pillow não tem acentos.
CABECA = ("cabeca", 0, 0, 8, 8, 8)
CHAPEU = ("camada externa da cabeca", 32, 0, 8, 8, 8)
CORPO = ("corpo", 16, 16, 8, 12, 4)
BRACO = ("bracos", 40, 16, 4, 12, 4)
PERNA = ("pernas", 0, 16, 4, 12, 4)

CAMADAS = {
    1: [(CABECA, "capacete", (90, 170, 255)),
        (CHAPEU, "capacete, opcional (deixe transparente se nao usar)", (150, 120, 255)),
        (CORPO, "peitoral", (60, 210, 140)),
        (BRACO, "peitoral", (240, 190, 60)),
        (PERNA, "botas (so a parte de baixo da perna)", (240, 100, 90))],
    2: [(CORPO, "calca (so a parte de baixo do corpo)", (60, 210, 140)),
        (PERNA, "calca", (240, 100, 90))],
}

# Brilho relativo de cada face, para dar noção de volume no molde.
FACES = {"topo": 1.15, "base": 0.6, "dir": 0.85, "frente": 1.0, "esq": 0.85, "tras": 0.7}
ALTURA_LEGENDA = 16


def faces_da_caixa(u, v, w, h, d):
    """Retângulos (x, y, largura, altura) de cada face na textura."""
    return {
        "topo": (u + d, v, w, d),
        "base": (u + d + w, v, w, d),
        "dir": (u, v + d, d, h),
        "frente": (u + d, v + d, w, h),
        "esq": (u + d + w, v + d, d, h),
        "tras": (u + d + w + d, v + d, w, h),
    }


def tom(cor, fator):
    return tuple(min(255, int(c * fator)) for c in cor) + (255,)


def gerar_camada(numero, partes):
    molde = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    altura_guia = 32 * ESCALA + ALTURA_LEGENDA * len(partes) + 8
    guia = Image.new("RGBA", (64 * ESCALA, altura_guia), (40, 40, 40, 255))
    desenho_molde = ImageDraw.Draw(molde)
    desenho_guia = ImageDraw.Draw(guia)

    # quadriculado de pixels no guia, para contar posições
    for x in range(0, 64 * ESCALA, ESCALA):
        desenho_guia.line([(x, 0), (x, 32 * ESCALA)], fill=(55, 55, 55, 255))
    for y in range(0, 32 * ESCALA, ESCALA):
        desenho_guia.line([(0, y), (64 * ESCALA, y)], fill=(55, 55, 55, 255))

    for i, ((nome, u, v, w, h, d), peca, cor) in enumerate(partes):
        for face, (x, y, fw, fh) in faces_da_caixa(u, v, w, h, d).items():
            preenchimento = tom(cor, FACES[face])
            desenho_molde.rectangle([x, y, x + fw - 1, y + fh - 1], fill=preenchimento)
            caixa = [x * ESCALA, y * ESCALA, (x + fw) * ESCALA - 1, (y + fh) * ESCALA - 1]
            desenho_guia.rectangle(caixa, fill=preenchimento, outline=(0, 0, 0, 255))
            desenho_guia.text((caixa[0] + 3, caixa[1] + 2), face, fill=(0, 0, 0, 255))
        legenda_y = 32 * ESCALA + 6 + i * ALTURA_LEGENDA
        desenho_guia.rectangle([6, legenda_y, 18, legenda_y + 10], fill=tom(cor, 1.0))
        desenho_guia.text((26, legenda_y), f"{nome} (x={u}, y={v}) -> {peca}", fill=(230, 230, 230, 255))

    MOLDES.mkdir(exist_ok=True)
    molde.save(MOLDES / f"armadura_camada_{numero}.png")
    guia.save(MOLDES / f"armadura_camada_{numero}_guia.png")


def main():
    for numero, partes in CAMADAS.items():
        gerar_camada(numero, partes)
    print(f"Moldes salvos em {MOLDES}")


if __name__ == "__main__":
    main()

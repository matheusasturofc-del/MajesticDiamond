"""Constantes e funções compartilhadas pelas ferramentas do pack."""

import os
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PACK = RAIZ / "pack"
TEXTURAS = PACK / "assets" / "minecraft" / "textures"
REFERENCIA = RAIZ / "referencia"
DIST = RAIZ / "dist"
NOME_ZIP = "MajesticDiamond.zip"
LISTA_1_8 = Path(__file__).resolve().parent / "texturas_1_8.txt"

PREFIXO_JAR = "assets/minecraft/textures/"
VERSOES = ("1.8.9", "1.8.8", "1.8")

# Texturas que mais importam no PvP, como padrões glob relativos a textures/
# (o * também casa subpastas).
TEXTURAS_PVP = [
    # Itens
    "items/*_sword.png",
    "items/bow_*.png",
    "items/arrow.png",
    "items/fishing_rod_*.png",
    "items/apple_golden.png",
    "items/ender_pearl.png",
    "items/potion_*.png",
    "items/diamond*.png",
    "items/iron_*.png",
    "items/beef_cooked.png",
    "items/porkchop_cooked.png",
    "items/flint_and_steel.png",
    "items/bucket_*.png",
    # Blocos
    "blocks/glass.png",
    "blocks/glass_pane_top.png",
    "blocks/fire_layer_*",
    "blocks/*_ore.png",
    "blocks/obsidian.png",
    "blocks/web.png",
    "blocks/stone.png",
    "blocks/cobblestone.png",
    # Armadura no corpo do jogador
    "models/armor/diamond_layer_*.png",
    "models/armor/iron_layer_*.png",
    # Interface
    "gui/icons.png",
    "gui/widgets.png",
    "gui/container/inventory.png",
    "misc/enchanted_item_glint.png*",
]

# Com --servidor, além das de PvP: o resto do que aparece em servidores
# (lobbies, minigames, bedwars, skywars...): blocos de construção, lã, céu,
# mobs, baús, partículas, menus e todos os itens.
TEXTURAS_SERVIDOR = [
    "items/*",
    # Blocos de construção e de mapas
    "blocks/wool_colored_*.png",
    "blocks/hardened_clay*.png",
    "blocks/glass_*.png",
    "blocks/planks_*.png",
    "blocks/log_*.png",
    "blocks/leaves_*.png",
    "blocks/*sandstone*.png",
    "blocks/*sand.png",
    "blocks/gravel.png",
    "blocks/dirt*.png",
    "blocks/coarse_dirt.png",
    "blocks/grass_*.png",
    "blocks/stone*.png",
    "blocks/cobblestone_mossy.png",
    "blocks/brick.png",
    "blocks/quartz_block_*.png",
    "blocks/*_block*.png",
    "blocks/snow.png",
    "blocks/ice*.png",
    "blocks/water_*",
    "blocks/lava_*",
    "blocks/tnt_*.png",
    "blocks/ladder.png",
    "blocks/vine.png",
    "blocks/iron_bars.png",
    "blocks/end_stone.png",
    "blocks/bedrock.png",
    "blocks/netherrack.png",
    "blocks/nether_brick.png",
    "blocks/soul_sand.png",
    "blocks/glowstone.png",
    "blocks/clay.png",
    "blocks/slime.png",
    "blocks/sponge*.png",
    "blocks/bookshelf.png",
    "blocks/crafting_table_*.png",
    "blocks/furnace_*.png",
    "blocks/enchanting_table_*.png",
    "blocks/anvil_*.png",
    "blocks/brewing_stand*.png",
    "blocks/beacon.png",
    "blocks/mob_spawner.png",
    "blocks/torch_on.png",
    "blocks/door_*.png",
    "blocks/trapdoor.png",
    "blocks/pumpkin_*.png",
    "blocks/melon_*.png",
    "blocks/tallgrass.png",
    "blocks/destroy_stage_*.png",
    # Mobs, jogadores, baús, placas, flechas no chão...
    "entity/*",
    # Céu, nuvens, chuva, partículas, cores do bioma
    "environment/*",
    "particle/*",
    "colormap/*",
    # Menus e textos
    "gui/*",
    "misc/*",
    "font/ascii.png",
    "map/*",
    "painting/*",
]

# Nomes de outras versões que não funcionam no 1.8 (erro comum ao copiar
# texturas de packs do 1.5/1.6 ou do 1.13+), por pasta: nome errado -> nome 1.8.
NOMES_ERRADOS = {
    "items": {
        # 1.5/1.6
        "swordDiamond": "diamond_sword", "swordIron": "iron_sword", "swordGold": "gold_sword",
        "swordStone": "stone_sword", "swordWood": "wood_sword",
        "helmetDiamond": "diamond_helmet", "chestplateDiamond": "diamond_chestplate",
        "leggingsDiamond": "diamond_leggings", "bootsDiamond": "diamond_boots",
        "helmetIron": "iron_helmet", "chestplateIron": "iron_chestplate",
        "leggingsIron": "iron_leggings", "bootsIron": "iron_boots",
        "appleGold": "apple_golden", "enderPearl": "ender_pearl",
        "beefCooked": "beef_cooked", "porkchopCooked": "porkchop_cooked",
        "flintAndSteel": "flint_and_steel",
        "potion_contents": "potion_overlay", "potion_splash": "potion_bottle_splash",
        "bow_pull_0": "bow_pulling_0", "bow_pull_1": "bow_pulling_1", "bow_pull_2": "bow_pulling_2",
        # 1.13+
        "golden_sword": "gold_sword", "wooden_sword": "wood_sword",
        "golden_helmet": "gold_helmet", "golden_chestplate": "gold_chestplate",
        "golden_leggings": "gold_leggings", "golden_boots": "gold_boots",
        "golden_apple": "apple_golden", "cooked_beef": "beef_cooked",
        "cooked_porkchop": "porkchop_cooked", "potion": "potion_bottle_drinkable",
        "splash_potion": "potion_bottle_splash", "bow": "bow_standby",
        "fishing_rod": "fishing_rod_uncast", "bucket": "bucket_empty",
        "water_bucket": "bucket_water", "lava_bucket": "bucket_lava",
    },
    "blocks": {
        # 1.5/1.6
        "thinglass_top": "glass_pane_top", "oreDiamond": "diamond_ore", "oreGold": "gold_ore",
        "oreIron": "iron_ore", "oreCoal": "coal_ore", "oreEmerald": "emerald_ore",
        "oreRedstone": "redstone_ore", "oreLapis": "lapis_ore",
        # 1.6 e 1.13+
        "fire_0": "fire_layer_0", "fire_1": "fire_layer_1", "cobweb": "web",
    },
}
# O 1.13+ usa as pastas no singular.
PASTAS_ERRADAS = {"item": "items", "block": "blocks"}


def sugerir_nome_1_8(nome):
    """Para um caminho relativo a textures/ de outra versão, devolve o nome 1.8 (ou None)."""
    pasta, _, arquivo = nome.partition("/")
    pasta_certa = PASTAS_ERRADAS.get(pasta, pasta)
    base, ponto, extensao = arquivo.partition(".")
    base_certa = NOMES_ERRADOS.get(pasta_certa, {}).get(base, base)
    sugestao = f"{pasta_certa}/{base_certa}{ponto}{extensao}"
    return sugestao if sugestao != nome else None


def ler_lista_1_8():
    """Devolve {caminho relativo a textures/: (largura, altura) ou None} do 1.8."""
    texturas = {}
    for linha in LISTA_1_8.read_text(encoding="utf-8").splitlines():
        if not linha or linha.startswith("#"):
            continue
        nome, _, tamanho = linha.partition(" ")
        texturas[nome] = tuple(map(int, tamanho.split("x"))) if tamanho else None
    return texturas


def ler_jar(caminho_jar):
    """Devolve {caminho relativo a textures/: bytes} de todas as texturas do jar."""
    with zipfile.ZipFile(caminho_jar) as jar:
        return {
            nome[len(PREFIXO_JAR):]: jar.read(nome)
            for nome in jar.namelist()
            if nome.startswith(PREFIXO_JAR) and not nome.endswith("/")
        }


def arquivos_do_pack():
    """Arquivos reais do pack (ignora .gitkeep e outros arquivos ocultos)."""
    return sorted(
        p for p in PACK.rglob("*")
        if p.is_file() and not any(parte.startswith(".") for parte in p.relative_to(PACK).parts)
    )


def pastas_minecraft():
    """Possíveis pastas .minecraft (Windows, macOS, Linux), na ordem de busca."""
    if os.environ.get("APPDATA"):
        yield Path(os.environ["APPDATA"]) / ".minecraft"
    yield Path.home() / "Library" / "Application Support" / "minecraft"
    yield Path.home() / ".minecraft"


def achar_jar():
    """Procura o .jar do 1.8.x instalado pelo launcher. Devolve None se não achar."""
    for pasta in pastas_minecraft():
        for versao in VERSOES:
            jar = pasta / "versions" / versao / f"{versao}.jar"
            if jar.is_file():
                return jar
    return None

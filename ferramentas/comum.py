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

PREFIXO_JAR = "assets/minecraft/textures/"

# Texturas que mais importam no PvP, como padrões glob relativos a textures/.
# São padrões (e não nomes fixos) para casar com os nomes exatos do seu .jar 1.6.
TEXTURAS_PVP = [
    # Itens
    "items/sword*.png",
    "items/bow*.png",
    "items/arrow.png",
    "items/fishingRod*.png",
    "items/appleGold.png",
    "items/enderPearl.png",
    "items/potion*.png",
    "items/*Diamond.png",
    "items/*Iron.png",
    "items/diamond.png",
    "items/beefCooked.png",
    "items/porkchopCooked.png",
    "items/flintAndSteel.png",
    "items/bucket*.png",
    # Blocos
    "blocks/glass.png",
    "blocks/thinglass_top.png",
    "blocks/fire_*",
    "blocks/ore*.png",
    "blocks/obsidian.png",
    "blocks/web.png",
    "blocks/stone.png",
    "blocks/cobblestone.png",
    # Armadura no corpo do jogador
    "models/armor/diamond*",
    "models/armor/iron*",
    # Interface
    "gui/icons.png",
    "gui/widgets.png",
    "gui/container/inventory.png",
    "misc/enchanted_item_glint.png",
]

# Nomes do 1.7+ que não funcionam no 1.6 (erro comum ao copiar texturas de
# packs mais novos). Chave: nome 1.7+, valor: nome 1.6.
NOMES_1_7_PARA_1_6 = {
    "items/diamond_sword.png": "items/swordDiamond.png",
    "items/iron_sword.png": "items/swordIron.png",
    "items/golden_sword.png": "items/swordGold.png",
    "items/stone_sword.png": "items/swordStone.png",
    "items/wood_sword.png": "items/swordWood.png",
    "items/diamond_helmet.png": "items/helmetDiamond.png",
    "items/diamond_chestplate.png": "items/chestplateDiamond.png",
    "items/diamond_leggings.png": "items/leggingsDiamond.png",
    "items/diamond_boots.png": "items/bootsDiamond.png",
    "items/iron_helmet.png": "items/helmetIron.png",
    "items/iron_chestplate.png": "items/chestplateIron.png",
    "items/iron_leggings.png": "items/leggingsIron.png",
    "items/iron_boots.png": "items/bootsIron.png",
    "items/apple_golden.png": "items/appleGold.png",
    "items/ender_pearl.png": "items/enderPearl.png",
    "items/beef_cooked.png": "items/beefCooked.png",
    "items/porkchop_cooked.png": "items/porkchopCooked.png",
    "items/flint_and_steel.png": "items/flintAndSteel.png",
    "items/potion_bottle_drinkable.png": "items/potion.png",
    "items/potion_bottle_splash.png": "items/potion_splash.png",
    "items/potion_overlay.png": "items/potion_contents.png",
    "blocks/glass_pane_top.png": "blocks/thinglass_top.png",
    "blocks/diamond_ore.png": "blocks/oreDiamond.png",
    "blocks/gold_ore.png": "blocks/oreGold.png",
    "blocks/iron_ore.png": "blocks/oreIron.png",
    "blocks/coal_ore.png": "blocks/oreCoal.png",
    "blocks/emerald_ore.png": "blocks/oreEmerald.png",
    "blocks/redstone_ore.png": "blocks/oreRedstone.png",
    "blocks/lapis_ore.png": "blocks/oreLapis.png",
    "blocks/fire_layer_0.png": "blocks/fire_0.png",
    "blocks/fire_layer_1.png": "blocks/fire_1.png",
}


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
    """Procura o .jar do 1.6.x instalado pelo launcher. Devolve None se não achar."""
    for pasta in pastas_minecraft():
        for versao in ("1.6.4", "1.6.2", "1.6.1"):
            jar = pasta / "versions" / versao / f"{versao}.jar"
            if jar.is_file():
                return jar
    return None

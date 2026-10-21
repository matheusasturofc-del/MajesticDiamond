# Majestic Diamond — pack de texturas PvP para Minecraft 1.8

Modelo de resource pack para o **Minecraft 1.8.x** (`pack_format: 1`), a versão
mais usada em servidores de PvP. Também costuma funcionar no 1.7. A estrutura,
os moldes e as ferramentas estão prontos: só falta desenhar as texturas.

```
pack/                      <- o resource pack (é isso que vira o .zip)
  pack.mcmeta              <- nome e descrição que aparecem no jogo
  pack.png                 <- (crie) ícone do pack, ex.: 64x64 ou 128x128
  assets/minecraft/textures/
    items/                 <- espadas, arco, poções, maçã dourada, pérola...
    blocks/                <- vidro, fogo, minérios...
    models/armor/          <- armadura no corpo do jogador
    gui/                   <- mira, corações, hotbar, inventário
    misc/  environment/  font/
moldes/                    <- mapas UV da armadura para desenhar por cima
ferramentas/               <- scripts para extrair, conferir e empacotar
```

## Passo a passo

Precisa de Python 3.9+ e do Pillow (`pip install pillow`). Abra o 1.8.9 no
launcher oficial pelo menos uma vez, para o `.jar` existir em `.minecraft/versions`
(Lunar e Badlion guardam o jogo em outro lugar).

1. **Pegue as texturas originais como base**

   ```
   python ferramentas/extrair_vanilla.py --pvp
   ```

   Todas as texturas do jogo vão para `referencia/` (só para consulta, fica fora
   do git) e as que importam no PvP são copiadas para dentro de `pack/`.
   Troque `--pvp` por `--servidor` para levar também o resto do que aparece em
   servidores: blocos de construção, lã, vidro colorido, céu, mobs, baús,
   partículas, menus e todos os itens (cerca de 680 texturas). Se o
   `.jar` não for achado sozinho, use `--jar CAMINHO/1.8.9.jar`.

   Sem Python: abra o `1.8.9.jar` com o 7-Zip ou WinRAR e copie a pasta
   `assets/minecraft/textures` para dentro de `pack/assets/minecraft/`.

2. **Edite os PNGs dentro de `pack/`** no editor que preferir (Aseprite,
   Paint.NET, GIMP, Pixlr, LibreSprite...). Arquivo que você não quer mudar,
   apague do `pack/`: o jogo usa o original no lugar.

3. **Confira e empacote**

   ```
   python ferramentas/empacotar.py --instalar
   ```

   O script confere o pack (nomes que o 1.8 usa, tamanhos, animações, JSON),
   gera `dist/MajesticDiamond.zip` e copia para `.minecraft/resourcepacks`.

4. No jogo: **Opções → Pacotes de Recursos** → selecione *Majestic Diamond*.
   Depois de mudar algo, rode o passo 3 de novo e selecione o pack outra vez
   (ou aperte F3+T para recarregar).

## O que editar para PvP

Os nomes são os do 1.8. Packs do 1.6 (`swordDiamond.png`) ou do 1.13+
(`item/golden_sword.png`) usam outros nomes e não funcionam aqui; o
`empacotar.py` avisa e diz o nome certo. A lista completa de arquivos do 1.8
está em `ferramentas/texturas_1_8.txt`.

| Textura | Arquivo(s) em `textures/` | Dica |
|---|---|---|
| Espadas | `items/diamond_sword.png`, `iron_sword`, `gold_sword`, `stone_sword`, `wood_sword` | Espada "curta" (lâmina menor) atrapalha menos a visão. |
| Arco | `items/bow_standby.png`, `bow_pulling_0`, `bow_pulling_1`, `bow_pulling_2` | Os 4 precisam ter o mesmo formato, só a corda/flecha muda. |
| Flecha | `items/arrow.png` | |
| Poções | `items/potion_bottle_drinkable.png`, `potion_bottle_splash.png`, `potion_overlay.png` | Veja abaixo. |
| Maçã dourada | `items/apple_golden.png` | A encantada usa a mesma imagem + brilho. |
| Pérola do Ender | `items/ender_pearl.png` | |
| Vara de pescar | `items/fishing_rod_uncast.png`, `fishing_rod_cast.png` | |
| Armadura (ícone) | `items/diamond_helmet.png`, `diamond_chestplate`, `diamond_leggings`, `diamond_boots` | Igual para `iron_`, `gold_`, `chainmail_`. |
| Armadura (no corpo) | `models/armor/diamond_layer_1.png`, `diamond_layer_2.png` | 64x32, use os moldes. |
| Vidro limpo | `blocks/glass.png`, `blocks/glass_pane_top.png` (borda do painel) | Veja abaixo. |
| Fogo baixo | `blocks/fire_layer_0.png`, `blocks/fire_layer_1.png` | Veja abaixo. |
| Minérios | `blocks/diamond_ore.png`, `gold_ore`, `iron_ore`... | Cores fortes ajudam a achar no meio da pedra. |
| Teia | `blocks/web.png` | Muito usada em PvP; deixe fácil de ver. |
| Mira, corações, fome | `gui/icons.png` | A mira é o quadrado 16x16 no canto superior esquerdo. |
| Hotbar | `gui/widgets.png` | |
| Inventário | `gui/container/inventory.png` | |
| Brilho de encantamento | `misc/enchanted_item_glint.png` | |

### Poções

O jogo desenha a poção em duas camadas: primeiro `potion_overlay.png` (o
líquido), pintado com a cor do efeito, e por cima `potion_bottle_drinkable.png`
ou `potion_bottle_splash.png` (o vidro). Por isso:

- desenhe o **líquido em branco/cinza** — o jogo colore. Cinza claro fica com a
  cor do efeito, cinza escuro fica com a cor mais escura;
- deixe o **interior do vidro transparente**, senão ele tampa o líquido;
- um líquido maior deixa mais fácil distinguir as poções na hotbar.

### Vidro limpo

O 1.8 desenha o vidro comum "recortado": cada pixel é totalmente visível ou totalmente
invisível (transparência parcial vira invisível ou opaca). Para vidro limpo,
deixe só a borda (ou só os cantos) com pixels opacos e o resto 100% transparente.

### Fogo baixo e animações

`fire_layer_0.png` e `fire_layer_1.png` são **animações**: uma tira vertical com vários
quadros quadrados empilhados (16x16, 16x32, 16x48...), com um arquivo
`.mcmeta` ao lado:

```json
{ "animation": { "frametime": 2 } }
```

`frametime` é quantos ticks cada quadro fica na tela (20 ticks = 1 segundo).
Para "fogo baixo", deixe a metade de cima de cada quadro transparente. Isso
diminui o fogo na tela quando você está queimando — e também o fogo no mundo.
Água e lava funcionam do mesmo jeito.

### Armadura no corpo

Abra `moldes/armadura_camada_1_guia.png` para ver qual pedaço da imagem vai em
qual parte do corpo, e use `moldes/armadura_camada_1.png` (64x32) como camada
de fundo no editor para desenhar por cima. Lembre de apagar a camada do molde
antes de salvar: o que não for armadura tem que ficar transparente.

- `diamond_layer_1.png`: capacete (cabeça), peitoral (corpo + braços), botas (pernas)
- `diamond_layer_2.png`: calça (corpo + pernas)

Para recriar os moldes: `python ferramentas/gerar_moldes.py`.

### Resolução (16x, 32x, 64x...)

O pack é 16x, mas o 1.8 aceita alta resolução: itens e blocos podem ter
32x32, 64x64 etc. (sempre potência de 2). Arquivos maiores, como `icons.png`
(256x256), crescem na mesma proporção: num pack 32x ele vira 512x512 e a mira
passa a ser 32x32. Se mudar a resolução, troque o "16x" no `pack.mcmeta`.

## Erros comuns

- **O pack não aparece no jogo**: o `pack.mcmeta` precisa estar na raiz do
  zip, não dentro de uma pasta. O `empacotar.py` já monta o zip certo.
- **A textura não muda**: nome errado (nome de outra versão, maiúscula/minúscula
  diferente, `.PNG` em maiúsculas). Rode o `empacotar.py`, ele aponta o nome certo.
- **Textura toda roxa e preta**: o PNG está corrompido ou com tamanho inválido.

As texturas originais em `referencia/` são da Mojang: use como base, mas não
publique cópias sem modificação.

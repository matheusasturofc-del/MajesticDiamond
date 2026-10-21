# Majestic Diamond — pack de texturas PvP para Minecraft 1.6

Modelo de resource pack para o **Minecraft 1.6.x** (`pack_format: 1`). A estrutura,
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

Precisa de Python 3.9+ e do Pillow (`pip install pillow`). Abra o 1.6.4 no
launcher pelo menos uma vez, para o `.jar` existir em `.minecraft/versions`.

1. **Pegue as texturas originais como base**

   ```
   python ferramentas/extrair_vanilla.py --pvp
   ```

   Todas as texturas do jogo vão para `referencia/` (só para consulta, fica fora
   do git) e as que importam no PvP são copiadas para dentro de `pack/`. Se o
   `.jar` não for achado sozinho, use `--jar CAMINHO/1.6.4.jar`.

2. **Edite os PNGs dentro de `pack/`** no editor que preferir (Aseprite,
   Paint.NET, GIMP, Pixlr, LibreSprite...). Arquivo que você não quer mudar,
   apague do `pack/`: o jogo usa o original no lugar.

3. **Confira e empacote**

   ```
   python ferramentas/empacotar.py --instalar
   ```

   O script confere o pack (nomes que o 1.6 usa, tamanhos, animações, JSON),
   gera `dist/MajesticDiamond.zip` e copia para `.minecraft/resourcepacks`.

4. No jogo: **Opções → Pacotes de Recursos** → selecione *Majestic Diamond*.
   Depois de mudar algo, rode o passo 3 de novo e selecione o pack outra vez
   (ou aperte F3+T para recarregar).

## O que editar para PvP

Os nomes são os do 1.6 (o 1.7 renomeou quase tudo, ex.: `diamond_sword.png`
não funciona aqui). Na dúvida, procure o nome exato em `referencia/` — o
`empacotar.py` também avisa quando um arquivo tem nome que o jogo não usa.

| Textura | Arquivo(s) em `textures/` | Dica |
|---|---|---|
| Espadas | `items/swordDiamond.png`, `swordIron`, `swordGold`, `swordStone`, `swordWood` | Espada "curta" (lâmina menor) atrapalha menos a visão. |
| Arco | `items/bow_*.png` (parado + 3 estados puxando) | Os 4 precisam ter o mesmo formato, só a corda/flecha muda. |
| Flecha | `items/arrow.png` | |
| Poções | `items/potion.png`, `potion_splash.png`, `potion_contents.png` | Veja abaixo. |
| Maçã dourada | `items/appleGold.png` | A encantada usa a mesma imagem + brilho. |
| Pérola do Ender | `items/enderPearl.png` | |
| Vara de pescar | `items/fishingRod*.png` (normal e lançada) | |
| Armadura (ícone) | `items/helmetDiamond.png`, `chestplateDiamond`, `leggingsDiamond`, `bootsDiamond` | Igual para `Iron`, `Gold`, `Chain`. |
| Armadura (no corpo) | `models/armor/diamond_layer_1.png`, `diamond_layer_2.png` | 64x32, use os moldes. |
| Vidro limpo | `blocks/glass.png`, `blocks/thinglass_top.png` (borda do painel) | Veja abaixo. |
| Fogo baixo | `blocks/fire_0.png`, `blocks/fire_1.png` | Veja abaixo. |
| Minérios | `blocks/oreDiamond.png`, `oreGold`, `oreIron`... | Cores fortes ajudam a achar no meio da pedra. |
| Mira, corações, fome | `gui/icons.png` | A mira é o quadrado 16x16 no canto superior esquerdo. |
| Hotbar | `gui/widgets.png` | |
| Inventário | `gui/container/inventory.png` | |
| Brilho de encantamento | `misc/enchanted_item_glint.png` | |

### Poções

O jogo desenha a poção em duas camadas: primeiro `potion_contents.png` (o
líquido), pintado com a cor do efeito, e por cima `potion.png` ou
`potion_splash.png` (o vidro). Por isso:

- desenhe o **líquido em branco/cinza** — o jogo colore. Cinza claro fica com a
  cor do efeito, cinza escuro fica com a cor mais escura;
- deixe o **interior do vidro transparente**, senão ele tampa o líquido;
- um líquido maior deixa mais fácil distinguir as poções na hotbar.

### Vidro limpo

O 1.6 desenha o vidro "recortado": cada pixel é totalmente visível ou totalmente
invisível (transparência parcial vira invisível ou opaca). Para vidro limpo,
deixe só a borda (ou só os cantos) com pixels opacos e o resto 100% transparente.

### Fogo baixo e animações

`fire_0.png` e `fire_1.png` são **animações**: uma tira vertical com vários
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

O pack é 16x, mas o 1.6 aceita alta resolução: itens e blocos podem ter
32x32, 64x64 etc. (sempre potência de 2). Arquivos maiores, como `icons.png`
(256x256), crescem na mesma proporção: num pack 32x ele vira 512x512 e a mira
passa a ser 32x32. Se mudar a resolução, troque o "16x" no `pack.mcmeta`.

## Erros comuns

- **O pack não aparece no jogo**: o `pack.mcmeta` precisa estar na raiz do
  zip, não dentro de uma pasta. O `empacotar.py` já monta o zip certo.
- **A textura não muda**: nome errado (nome do 1.7+, maiúscula/minúscula
  diferente, `.PNG` em maiúsculas). Rode o `empacotar.py`, ele aponta o nome certo.
- **Textura toda roxa e preta**: o PNG está corrompido ou com tamanho inválido.

As texturas originais em `referencia/` são da Mojang: use como base, mas não
publique cópias sem modificação.

"""Desenho animado da arvore AVL com Pygame.

Uso:
    vis = VisualizadorArvore(arvore, pygame.Rect(x, y, largura, altura))

    # depois de cada insercao/remocao na arvore:
    vis.atualizar_estrutura()

    # a cada frame:
    vis.atualizar(dt)          # dt em segundos
    vis.desenhar(tela)

Os nos deslizam suavemente para a nova posicao, entao uma rotacao aparece
como os nos trocando de lugar. O no que foi rotacionado pisca e um aviso
com o tipo da rotacao (LL, RR, LR, RL) aparece no topo da area.

Cores:
  azul     -> fator de balanceamento 0
  laranja  -> fator de balanceamento +1 ou -1
  borda vermelha -> no de maior ameaca (o alvo prioritario do jogo)
"""
import math

import pygame

from layout_arvore import calcular_layout, raio_dos_nos

COR_FUNDO = (14, 18, 28)
COR_ARESTA = (95, 105, 130)
COR_FB_ZERO = (45, 100, 175)
COR_FB_UM = (190, 120, 35)
COR_BORDA = (20, 25, 40)
COR_MAXIMO = (235, 75, 75)
COR_FLASH = (255, 235, 120)
COR_TEXTO = (240, 244, 250)
COR_TEXTO_FRACO = (150, 160, 180)
COR_AVISO = (255, 235, 120)

DESCRICAO_ROTACAO = {
    "LL": "rotação simples à direita",
    "RR": "rotação simples à esquerda",
    "LR": "rotação dupla esquerda-direita",
    "RL": "rotação dupla direita-esquerda",
}

VELOCIDADE_ANIMACAO = 12.0   # maior = nos chegam mais rapido
DURACAO_FLASH = 1.0          # segundos
DURACAO_AVISO = 2.2          # segundos


class VisualizadorArvore:
    def __init__(self, arvore, area):
        pygame.font.init()
        self.arvore = arvore
        self.area = pygame.Rect(area)
        self.nos = []            # lista de NoDesenho (posicao final de cada no)
        self.alvo = {}           # chave -> NoDesenho
        self.pos = {}            # chave -> [x, y] (posicao atual, animada)
        self.flash = {}          # chave -> segundos restantes
        self.aviso = ""
        self.aviso_t = 0.0
        self.raio = 20
        self._fontes = {}
        self.atualizar_estrutura()

    # ---------- estado ----------
    def _fonte(self, tamanho):
        if tamanho not in self._fontes:
            self._fontes[tamanho] = pygame.font.Font(None, tamanho)
        return self._fontes[tamanho]

    def atualizar_estrutura(self):
        """Recalcula o layout. Chame depois de mudar a arvore."""
        area = (self.area.x, self.area.y, self.area.width, self.area.height)
        self.nos = calcular_layout(self.arvore, area)
        self.alvo = {n.chave: n for n in self.nos}
        self.raio = raio_dos_nos(len(self.nos), self.area.width)

        existentes = set(self.pos)
        for n in self.nos:
            if n.chave in existentes:
                continue
            # no novo: nasce na posicao atual do pai e desliza ate o lugar dele
            if n.pai in existentes:
                self.pos[n.chave] = list(self.pos[n.pai])
            else:
                self.pos[n.chave] = [n.x, n.y]
        for chave in list(self.pos):
            if chave not in self.alvo:
                del self.pos[chave]
                self.flash.pop(chave, None)

        eventos = self.arvore.consumir_eventos()
        for tipo, chave in eventos:
            self.flash[chave] = DURACAO_FLASH
        if eventos:
            self.aviso = "   |   ".join(
                f"{tipo} em {chave[0]}: {DESCRICAO_ROTACAO[tipo]}"
                for tipo, chave in eventos
            )
            self.aviso_t = DURACAO_AVISO

    def atualizar(self, dt):
        """Avanca a animacao em dt segundos."""
        k = 1 - math.exp(-VELOCIDADE_ANIMACAO * dt)
        for chave, p in self.pos.items():
            alvo = self.alvo[chave]
            p[0] += (alvo.x - p[0]) * k
            p[1] += (alvo.y - p[1]) * k
        for chave in list(self.flash):
            self.flash[chave] -= dt
            if self.flash[chave] <= 0:
                del self.flash[chave]
        if self.aviso_t > 0:
            self.aviso_t -= dt

    # ---------- desenho ----------
    def desenhar(self, tela):
        tela.set_clip(self.area)
        pygame.draw.rect(tela, COR_FUNDO, self.area)

        if not self.nos:
            msg = self._fonte(30).render("Árvore vazia", True, COR_TEXTO_FRACO)
            tela.blit(msg, msg.get_rect(center=self.area.center))
            tela.set_clip(None)
            return

        # arestas primeiro, para ficarem atras dos circulos
        for n in self.nos:
            if n.pai is not None and n.pai in self.pos:
                a = self.pos[n.pai]
                b = self.pos[n.chave]
                pygame.draw.line(tela, COR_ARESTA, (int(a[0]), int(a[1])),
                                 (int(b[0]), int(b[1])), 2)

        maior = self.arvore.maximo()
        chave_maior = maior.chave if maior else None
        r = self.raio
        fonte_no = self._fonte(int(max(14, min(26, r * 1.3))))
        fonte_fb = self._fonte(int(max(13, min(20, r))))

        for n in self.nos:
            x, y = self.pos[n.chave]
            centro = (int(x), int(y))
            cor = COR_FB_ZERO if n.fb == 0 else COR_FB_UM
            pygame.draw.circle(tela, cor, centro, int(r))
            pygame.draw.circle(tela, COR_BORDA, centro, int(r), 2)

            if n.chave == chave_maior:
                pygame.draw.circle(tela, COR_MAXIMO, centro, int(r) + 3, 3)
            if n.chave in self.flash:
                forca = min(1.0, self.flash[n.chave] / DURACAO_FLASH)
                pygame.draw.circle(tela, COR_FLASH, centro,
                                   int(r) + 6, max(2, int(5 * forca)))

            texto = fonte_no.render(str(n.chave[0]), True, COR_TEXTO)
            tela.blit(texto, texto.get_rect(center=centro))

            rotulo = "0" if n.fb == 0 else f"{n.fb:+d}"
            fb = fonte_fb.render(rotulo, True, COR_TEXTO_FRACO)
            tela.blit(fb, fb.get_rect(midtop=(centro[0], centro[1] + int(r) + 4)))

        if self.aviso_t > 0 and self.aviso:
            surf = self._fonte(28).render(self.aviso, True, COR_AVISO)
            surf.set_alpha(int(255 * min(1.0, self.aviso_t / 0.6)))
            tela.blit(surf, surf.get_rect(midtop=(self.area.centerx, self.area.y + 8)))

        tela.set_clip(None)
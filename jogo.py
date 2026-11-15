"""Interface Pygame do Air Defense.

A logica fica em partida.py; aqui so ha desenho, entrada do jogador e o
painel com a arvore AVL (desenho_arvore.py).

Controles:
  botao esquerdo (segurar)      atira na direcao da mira
  botao direito ou ESPACO       missil teleguiado na maior ameaca
  P pausa   R reinicia   ESC sai
"""
import argparse
import math
import os
import random

import pygame

from desenho_arvore import (COR_FUNDO, COR_MAXIMO, COR_TEXTO, COR_TEXTO_FRACO,
                            VisualizadorArvore)
from partida import (ALTURA_CAMPO, BATERIA_X, BATERIA_Y, CANO_Y,
                     INTERVALO_MISSIL, LARGURA_CAMPO, SOLO_Y, VIDA_BASE, Partida)

LARGURA, ALTURA = LARGURA_CAMPO, 720
PAINEL = pygame.Rect(0, ALTURA_CAMPO, LARGURA, ALTURA - ALTURA_CAMPO)

COR_CEU = (10, 14, 24)
COR_SOLO = (22, 40, 32)
COR_LINHA_SOLO = (60, 110, 80)
COR_TORRE = (70, 85, 110)
COR_TIRO = (255, 240, 150)
COR_MISSIL = (255, 150, 60)


class Jogo:
    def __init__(self, tela, semente=None):
        self.tela = tela
        self.semente = semente
        self.estado = "menu"           # menu | jogando | pausado
        self.mira = None               # usado so na captura; normalmente = mouse
        self.banner_t = 0.0
        self.onda_vista = 1
        self._fontes = {}
        rng = random.Random(7)
        self.estrelas = [(rng.randint(0, LARGURA), rng.randint(0, SOLO_Y - 40),
                          rng.choice((1, 1, 1, 2))) for _ in range(90)]
        self.novo()

    def novo(self):
        self.partida = Partida(self.semente)
        self.vis = VisualizadorArvore(self.partida.arvore, PAINEL)
        self.onda_vista = 1
        self.banner_t = 2.0

    def fonte(self, tamanho):
        if tamanho not in self._fontes:
            self._fontes[tamanho] = pygame.font.Font(None, tamanho)
        return self._fontes[tamanho]

    def pos_mira(self):
        return self.mira if self.mira else pygame.mouse.get_pos()

    # ---------- entrada ----------
    def tratar_evento(self, ev):
        """Devolve False quando o jogador quer sair."""
        if ev.type == pygame.QUIT:
            return False
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                return False
            if self.estado == "menu":
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.estado = "jogando"
            elif ev.key == pygame.K_p and not self.partida.fim:
                self.estado = "pausado" if self.estado == "jogando" else "jogando"
            elif ev.key == pygame.K_r:
                self.novo()
                self.estado = "jogando"
            elif ev.key == pygame.K_SPACE and self.estado == "jogando":
                self.partida.disparar_missil()
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            if self.estado == "menu" and ev.button == 1:
                self.estado = "jogando"
            elif self.estado == "jogando" and ev.button == 3:
                self.partida.disparar_missil()
        return True

    # ---------- atualizacao ----------
    def atualizar(self, dt):
        if self.estado == "jogando":
            mx, my = self.pos_mira()
            if self.mira is None and pygame.mouse.get_pressed()[0] and my < ALTURA_CAMPO:
                self.partida.atirar(mx, my)
            self.partida.update(dt)
            if self.partida.onda != self.onda_vista:
                self.onda_vista = self.partida.onda
                self.banner_t = 2.0
        self.banner_t = max(0.0, self.banner_t - dt)

        if self.partida.arvore_mudou:
            self.vis.atualizar_estrutura()
            self.partida.arvore_mudou = False
        self.vis.atualizar(dt)

    # ---------- desenho ----------
    def desenhar(self):
        t = self.tela
        t.fill(COR_FUNDO)
        pygame.draw.rect(t, COR_CEU, (0, 0, LARGURA, ALTURA_CAMPO))
        for x, y, r in self.estrelas:
            pygame.draw.circle(t, (70, 80, 110), (x, y), r)

        self._desenhar_torre()
        pygame.draw.rect(t, COR_SOLO, (0, SOLO_Y, LARGURA, ALTURA_CAMPO - SOLO_Y))
        pygame.draw.line(t, COR_LINHA_SOLO, (0, SOLO_Y), (LARGURA, SOLO_Y), 2)

        p = self.partida
        maior = p.arvore.maximo()
        chave_maior = maior.chave if maior else None
        for m in p.misseis:
            self._desenhar_missil(m)
        for a in p.aeronaves:
            self._desenhar_aeronave(a, a.chave == chave_maior)
        for tiro in p.tiros:
            pygame.draw.circle(t, COR_TIRO, (int(tiro.x), int(tiro.y)), 3)

        self._desenhar_hud()
        self._desenhar_mira()

        # painel da arvore
        self.vis.desenhar(t)
        pygame.draw.line(t, (45, 55, 80), (0, ALTURA_CAMPO), (LARGURA, ALTURA_CAMPO), 2)
        rotulo = ("Radar: árvore AVL das ameaças   "
                  "(borda vermelha = maior ameaça = alvo do míssil)")
        t.blit(self.fonte(22).render(rotulo, True, COR_TEXTO_FRACO),
               (16, ALTURA - 26))

        if self.estado == "menu":
            self._desenhar_menu()
        elif self.estado == "pausado":
            self._cobertura("PAUSADO", "P para continuar")
        elif p.fim:
            self._desenhar_fim()

    def _desenhar_torre(self):
        t = self.tela
        pygame.draw.circle(t, COR_TORRE, (int(BATERIA_X), int(BATERIA_Y)), 28)
        mx, my = self.pos_mira()
        ang = math.atan2(my - CANO_Y, mx - BATERIA_X)
        ang = max(-math.pi + 0.12, min(-0.12, ang))      # cano so aponta para cima
        ponta = (BATERIA_X + math.cos(ang) * 42, CANO_Y + math.sin(ang) * 42)
        pygame.draw.line(t, (150, 165, 190), (BATERIA_X, CANO_Y), ponta, 7)
        pygame.draw.circle(t, (110, 125, 150), (int(BATERIA_X), int(CANO_Y)), 12)

    def _desenhar_aeronave(self, a, eh_maior):
        t = self.tela
        ang = math.atan2(a.vy, a.vx)
        c, s = math.cos(ang), math.sin(ang)
        r = a.raio

        def ponto(fx, fy):
            return (a.x + fx * c - fy * s, a.y + fx * s + fy * c)

        corpo = [ponto(r * 1.5, 0), ponto(-r, r * 0.95),
                 ponto(-r * 0.45, 0), ponto(-r, -r * 0.95)]
        cor = (255, 255, 255) if a.piscar > 0 else a.cor
        pygame.draw.polygon(t, cor, corpo)
        pygame.draw.polygon(t, (20, 25, 40), corpo, 2)

        if eh_maior:
            pygame.draw.circle(t, COR_MAXIMO, (int(a.x), int(a.y)), r + 10, 2)

        texto = self.fonte(20).render(str(a.ameaca), True, COR_TEXTO)
        t.blit(texto, texto.get_rect(center=(a.x, a.y - r - 16)))
        if a.vida_max > 1:
            larg = r * 2
            x0, y0 = a.x - r, a.y - r - 8
            pygame.draw.rect(t, (40, 48, 66), (x0, y0, larg, 4))
            pygame.draw.rect(t, (90, 210, 120), (x0, y0, larg * a.vida / a.vida_max, 4))

    def _desenhar_missil(self, m):
        t = self.tela
        if len(m.rastro) > 1:
            pygame.draw.lines(t, (200, 110, 50), False,
                              [(int(x), int(y)) for x, y in m.rastro], 2)
        pygame.draw.circle(t, COR_MISSIL, (int(m.x), int(m.y)), 5)

    def _barra(self, x, y, larg, alt, fracao, cor):
        pygame.draw.rect(self.tela, (40, 48, 66), (x, y, larg, alt), border_radius=3)
        if fracao > 0:
            pygame.draw.rect(self.tela, cor, (x, y, int(larg * fracao), alt),
                             border_radius=3)

    def _desenhar_hud(self):
        t = self.tela
        p = self.partida
        frac = p.base_vida / VIDA_BASE
        cor = (80, 200, 120) if frac > 0.5 else (230, 170, 60) if frac > 0.25 \
            else (230, 80, 80)
        t.blit(self.fonte(24).render(f"BASE  {int(p.base_vida)}", True, COR_TEXTO), (20, 10))
        self._barra(20, 32, 260, 14, frac, cor)

        pronto = 1 - p.espera_missil / INTERVALO_MISSIL
        t.blit(self.fonte(20).render("MÍSSIL", True, COR_TEXTO_FRACO), (20, 56))
        self._barra(80, 60, 200, 8, pronto, COR_MISSIL if pronto >= 1 else (150, 110, 70))

        t.blit(self.fonte(24).render(f"PONTOS  {p.pontos}", True, COR_TEXTO), (310, 10))
        t.blit(self.fonte(22).render(f"onda {p.onda}    abates {p.abates}",
                                     True, COR_TEXTO_FRACO), (310, 36))

        for i, texto in enumerate(p.log):
            brilho = 110 + 29 * i
            surf = self.fonte(22).render(texto, True, (brilho, brilho, brilho + 10))
            t.blit(surf, surf.get_rect(topright=(LARGURA - 20, 12 + i * 20)))

        dica = ("esquerdo: atirar     direito / espaço: míssil na maior ameaça     "
                "P: pausa     R: reiniciar     ESC: sair")
        t.blit(self.fonte(20).render(dica, True, COR_TEXTO_FRACO), (20, SOLO_Y + 6))

        if self.banner_t > 0 and self.estado == "jogando":
            surf = self.fonte(64).render(f"ONDA {p.onda}", True, COR_TEXTO)
            surf.set_alpha(int(255 * min(1.0, self.banner_t / 0.7)))
            t.blit(surf, surf.get_rect(center=(LARGURA / 2, 120)))
        elif p.pausa_onda is not None:
            surf = self.fonte(36).render(f"Onda {p.onda} concluída", True, COR_TEXTO)
            t.blit(surf, surf.get_rect(center=(LARGURA / 2, 120)))

    def _desenhar_mira(self):
        mx, my = self.pos_mira()
        no_campo = my < ALTURA_CAMPO and self.estado == "jogando"
        if self.mira is None:
            pygame.mouse.set_visible(not no_campo)
        if no_campo:
            t = self.tela
            pygame.draw.circle(t, (255, 255, 255), (mx, my), 11, 1)
            pygame.draw.line(t, (255, 255, 255), (mx - 16, my), (mx - 5, my), 1)
            pygame.draw.line(t, (255, 255, 255), (mx + 5, my), (mx + 16, my), 1)
            pygame.draw.line(t, (255, 255, 255), (mx, my - 16), (mx, my - 5), 1)
            pygame.draw.line(t, (255, 255, 255), (mx, my + 5), (mx, my + 16), 1)

    def _cobertura(self, titulo, subtitulo=None, extra=()):
        veu = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        veu.fill((8, 10, 18, 190))
        self.tela.blit(veu, (0, 0))
        surf = self.fonte(96).render(titulo, True, COR_TEXTO)
        self.tela.blit(surf, surf.get_rect(center=(LARGURA / 2, 190)))
        y = 270
        if subtitulo:
            surf = self.fonte(34).render(subtitulo, True, COR_TEXTO_FRACO)
            self.tela.blit(surf, surf.get_rect(center=(LARGURA / 2, y)))
            y += 44
        for linha in extra:
            surf = self.fonte(28).render(linha, True, COR_TEXTO)
            self.tela.blit(surf, surf.get_rect(center=(LARGURA / 2, y)))
            y += 34

    def _desenhar_menu(self):
        self._cobertura("AIR DEFENSE", "Defesa aérea com árvore AVL", [
            "Cada aeronave entra no radar (uma árvore AVL) pelo nível de ameaça.",
            "Abata os inimigos antes que cheguem ao solo e proteja a base.",
            "O míssil sempre persegue a maior ameaça, o máximo da árvore.",
            "",
            "ENTER ou clique para começar",
        ])

    def _desenhar_fim(self):
        p = self.partida
        self._cobertura("BASE DESTRUÍDA", f"{p.pontos} pontos", [
            f"onda {p.onda}    abates {p.abates}",
            "",
            "R para jogar de novo",
        ])


# ---------- captura de imagens (sem janela) ----------
def capturar(jogo, pasta):
    """Joga sozinho por alguns segundos e salva menu.png e jogo.png."""
    os.makedirs(pasta, exist_ok=True)
    jogo.desenhar()
    pygame.image.save(jogo.tela, os.path.join(pasta, "menu.png"))

    jogo.estado = "jogando"
    dt = 1 / 60
    melhor = None
    melhor_nos = -1
    ruido = random.Random(11)       # o bot erra a mira, senao abate tudo rapido
    for frame in range(60 * 60):
        p = jogo.partida
        if p.aeronaves:
            alvo = max(p.aeronaves, key=lambda a: a.y)
            assert alvo is not None
            jogo.mira = (alvo.x + alvo.vx * 0.3 + ruido.uniform(-110, 110),
                         alvo.y + alvo.vy * 0.3 + ruido.uniform(-110, 110))
            if frame % 12 == 0:
                p.atirar(*jogo.mira)
        if len(p.aeronaves) >= 6 and frame % 90 == 0:
            p.disparar_missil()
        jogo.atualizar(dt)
        if p.fim:
            break
        if frame > 60 * 8 and frame % 15 == 0 and len(p.arvore) > melhor_nos:
            jogo.desenhar()
            melhor, melhor_nos = jogo.tela.copy(), len(p.arvore)
    if melhor is None:
        jogo.desenhar()
        melhor = jogo.tela
    pygame.image.save(melhor, os.path.join(pasta, "jogo.png"))
    print(f"imagens salvas em {pasta} (arvore com {melhor_nos} nos no print)")


def main():
    parser = argparse.ArgumentParser(description="Air Defense")
    parser.add_argument("--captura", metavar="PASTA",
                        help="joga sozinho, salva menu.png e jogo.png e sai")
    args = parser.parse_args()

    if args.captura:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Air Defense")
    jogo = Jogo(tela, semente=2 if args.captura else None)

    if args.captura:
        capturar(jogo, args.captura)
        pygame.quit()
        return

    relogio = pygame.time.Clock()
    rodando = True
    while rodando:
        dt = min(relogio.tick(60) / 1000, 0.05)      # evita saltos se travar
        for ev in pygame.event.get():
            if not jogo.tratar_evento(ev):
                rodando = False
        jogo.atualizar(dt)
        jogo.desenhar()
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
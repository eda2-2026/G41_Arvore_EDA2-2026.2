"""Laboratorio da arvore AVL: veja insercoes, remocoes e rotacoes acontecendo.

Rode com:  python demo_arvore.py

Teclas:
  I  insere 1 chave aleatoria        A  insere 10 chaves (uma a cada instante)
  S  sequencia crescente (forca RR)  D  sequencia decrescente (forca LL)
  R  remove uma chave aleatoria      M  remove a de maior ameaca
  C  limpa a arvore                  ESC ou Q  sai

Para gerar uma imagem sem abrir janela (util para o README):
  python demo_arvore.py --captura assets/arvore.png
"""
import argparse
import os
import random

import pygame

from avl import ArvoreAVL
from desenho_arvore import (COR_FB_UM, COR_FB_ZERO, COR_FUNDO, COR_MAXIMO,
                            COR_TEXTO, COR_TEXTO_FRACO, VisualizadorArvore)

LARGURA, ALTURA = 1280, 720
TOPO = 120
PAINEL = pygame.Rect(0, TOPO, LARGURA, ALTURA - TOPO)
INTERVALO_FILA = 0.45        # segundos entre insercoes de uma sequencia

AJUDA = [
    "I: inserir 1    A: inserir 10    S: crescente    D: decrescente",
    "R: remover aleatória    M: remover a de maior ameaça    C: limpar    ESC: sair",
]


class Demo:
    def __init__(self, tela):
        self.tela = tela
        self.arvore = ArvoreAVL()
        self.vis = VisualizadorArvore(self.arvore, PAINEL)
        self.rng = random.Random()
        self.proximo_id = 1
        self.fila = []           # ameacas esperando para serem inseridas
        self.espera = 0.0

    # ---------- operacoes ----------
    def inserir(self, ameaca):
        self.arvore.inserir((ameaca, self.proximo_id))
        self.proximo_id += 1
        self.vis.atualizar_estrutura()

    def remover(self, chave):
        self.arvore.remover(chave)
        self.vis.atualizar_estrutura()

    def _maior_ameaca(self):
        no = self.arvore.maximo()
        return no.chave[0] if no else 0

    def _menor_ameaca(self):
        no = self.arvore.minimo()
        return no.chave[0] if no else 100

    def tecla(self, tecla):
        if tecla == pygame.K_i:
            self.fila.append(self.rng.randint(1, 99))
        elif tecla == pygame.K_a:
            self.fila.extend(self.rng.randint(1, 99) for _ in range(10))
        elif tecla == pygame.K_s:
            base = self._maior_ameaca()
            self.fila.extend(min(99, base + i) for i in range(1, 8))
        elif tecla == pygame.K_d:
            base = self._menor_ameaca()
            self.fila.extend(max(1, base - i) for i in range(1, 8))
        elif tecla == pygame.K_r:
            nos = self.arvore.em_ordem()
            if nos:
                self.remover(self.rng.choice(nos).chave)
        elif tecla == pygame.K_m:
            no = self.arvore.maximo()
            if no:
                self.remover(no.chave)
        elif tecla == pygame.K_c:
            self.fila.clear()
            self.arvore.limpar()
            self.vis.atualizar_estrutura()

    # ---------- ciclo do jogo ----------
    def atualizar(self, dt):
        if self.fila:
            self.espera -= dt
            if self.espera <= 0:
                self.inserir(self.fila.pop(0))
                self.espera = INTERVALO_FILA
        else:
            self.espera = 0.0
        self.vis.atualizar(dt)

    def desenhar(self):
        self.tela.fill(COR_FUNDO)
        titulo = pygame.font.Font(None, 40).render(
            "Air Defense - Laboratório da Árvore AVL", True, COR_TEXTO)
        self.tela.blit(titulo, (24, 14))

        fonte = pygame.font.Font(None, 24)
        for i, linha in enumerate(AJUDA):
            self.tela.blit(fonte.render(linha, True, COR_TEXTO_FRACO),
                           (24, 52 + i * 22))

        a = self.arvore
        maximo = a.maximo()
        minimo = a.minimo()
        maior = maximo.chave[0] if maximo else "-"
        menor = minimo.chave[0] if minimo else "-"
        info = (f"nós: {len(a)}    altura: {a.altura()}    "
                f"maior ameaça: {maior}    menor ameaça: {menor}    "
                f"na fila: {len(self.fila)}")
        self.tela.blit(fonte.render(info, True, COR_TEXTO), (24, 96))

        # legenda de cores, canto direito
        x = LARGURA - 330
        for cor, texto, raio in [(COR_FB_ZERO, "fator 0", 8),
                                 (COR_FB_UM, "fator ±1", 8)]:
            pygame.draw.circle(self.tela, cor, (x, 28), raio)
            self.tela.blit(fonte.render(texto, True, COR_TEXTO_FRACO), (x + 14, 21))
            x += 110
        pygame.draw.circle(self.tela, COR_MAXIMO, (LARGURA - 330, 56), 9, 3)
        self.tela.blit(fonte.render("maior ameaça (alvo)", True, COR_TEXTO_FRACO),
                       (LARGURA - 330 + 16, 49))

        self.vis.desenhar(self.tela)


def capturar(demo, caminho):
    """Monta uma arvore de exemplo e salva a imagem (sem interacao)."""
    for ameaca in [50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 45, 5]:
        demo.inserir(ameaca)
    for _ in range(60):                  # deixa a animacao assentar
        demo.vis.atualizar(1 / 60)
    demo.inserir(3)                      # dispara uma rotacao visivel
    demo.inserir(2)
    for _ in range(40):
        demo.atualizar(1 / 60)
    demo.desenhar()
    pasta = os.path.dirname(caminho)
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    pygame.image.save(demo.tela, caminho)
    print(f"imagem salva em {caminho}")


def main():
    parser = argparse.ArgumentParser(description="Laboratório da árvore AVL")
    parser.add_argument("--captura", metavar="ARQUIVO.png",
                        help="salva uma imagem de exemplo e sai (sem janela)")
    args = parser.parse_args()

    if args.captura:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Air Defense - Laboratório da Árvore AVL")
    demo = Demo(tela)

    if args.captura:
        capturar(demo, args.captura)
        pygame.quit()
        return

    relogio = pygame.time.Clock()
    rodando = True
    while rodando:
        dt = relogio.tick(60) / 1000
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_ESCAPE, pygame.K_q):
                    rodando = False
                else:
                    demo.tecla(evento.key)
        demo.atualizar(dt)
        demo.desenhar()
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
"""Calculo das posicoes dos nos para desenhar a arvore (sem depender do Pygame).

Regra de posicionamento:
  - x: a posicao do no no percurso em ordem. Assim a ordem das chaves
    aparece da esquerda para a direita e nenhuma aresta se cruza.
  - y: a profundidade do no (raiz no topo, abaixo de uma faixa reservada
    para o aviso de rotacao).

Ficar separado do Pygame deixa essa parte testavel sem abrir janela.
"""
from collections import namedtuple

from avl import fator_balanceamento

# pai e a chave do no pai (None para a raiz)
NoDesenho = namedtuple("NoDesenho", "chave x y fb altura pai")


def _percurso(no, profundidade, pai, saida):
    """Percurso em ordem guardando (no, profundidade, chave_do_pai)."""
    if no is None:
        return
    _percurso(no.esq, profundidade + 1, no.chave, saida)
    saida.append((no, profundidade, pai))
    _percurso(no.dir, profundidade + 1, no.chave, saida)


MARGEM_TOPO = 56    # faixa livre no topo para o aviso de rotacao


def calcular_layout(arvore, area, margem=30, margem_topo=MARGEM_TOPO,
                    passo_y_max=80):
    """Devolve a lista de NoDesenho, em ordem crescente de chave.

    area = (x, y, largura, altura) da regiao onde a arvore sera desenhada.
    """
    x0, y0, largura, altura_area = area
    itens = []
    _percurso(arvore.raiz, 0, None, itens)
    n = len(itens)
    if n == 0:
        return []

    profundidade_max = max(prof for _, prof, _ in itens)
    util_x = max(largura - 2 * margem, 0)
    util_y = max(altura_area - margem_topo - margem, 0)
    passo_y = min(passo_y_max, util_y / profundidade_max) if profundidade_max else 0

    resultado = []
    for i, (no, prof, pai) in enumerate(itens):
        x = x0 + margem + (util_x * i / (n - 1) if n > 1 else util_x / 2)
        y = y0 + margem_topo + prof * passo_y
        resultado.append(
            NoDesenho(no.chave, x, y, fator_balanceamento(no), no.altura, pai)
        )
    return resultado


def raio_dos_nos(quantidade, largura, margem=30, maximo=20, minimo=6):
    """Raio dos circulos: diminui quando ha muitos nos para nao se sobreporem."""
    if quantidade <= 1:
        return maximo
    passo_x = (largura - 2 * margem) / (quantidade - 1)
    return max(minimo, min(maximo, passo_x * 0.48))
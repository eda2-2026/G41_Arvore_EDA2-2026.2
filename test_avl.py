"""Testes da arvore, independentes da interface. Rode com: python test_avl.py"""
from avl import ArvoreAVL


def teste_insercao_e_ordem():
    a = ArvoreAVL()
    for chave in [(5, 1), (3, 2), (8, 3), (1, 4), (4, 5)]:
        assert a.inserir(chave)
    assert len(a) == 5
    assert [n.chave for n in a.em_ordem()] == [(1, 4), (3, 2), (4, 5), (5, 1), (8, 3)]


def teste_chave_repetida():
    a = ArvoreAVL()
    assert a.inserir((5, 1))
    assert not a.inserir((5, 1))
    assert len(a) == 1


def teste_desempate_por_id():
    a = ArvoreAVL()
    a.inserir((5, 1))
    a.inserir((5, 2))
    assert len(a) == 2
    maximo = a.maximo()
    assert maximo is not None
    assert maximo.chave == (5, 2)


def teste_busca_minimo_maximo():
    a = ArvoreAVL()
    assert a.minimo() is None and a.maximo() is None
    for chave in [(5, 1), (3, 2), (8, 3)]:
        a.inserir(chave, valor=f"inimigo{chave[1]}")
    encontrado = a.buscar((3, 2))
    assert encontrado is not None
    assert encontrado.valor == "inimigo2"
    assert a.buscar((9, 9)) is None
    minimo = a.minimo()
    maximo = a.maximo()
    assert minimo is not None
    assert maximo is not None
    assert minimo.chave == (3, 2)
    assert maximo.chave == (8, 3)


def teste_altura():
    a = ArvoreAVL()
    assert a.altura() == 0
    a.inserir((2, 1))
    assert a.altura() == 1
    a.inserir((1, 2))
    a.inserir((3, 3))
    assert a.altura() == 2


def montar(chaves):
    a = ArvoreAVL()
    for c in chaves:
        a.inserir(c, valor=f"inimigo{c[1]}")
    return a


def chaves(a):
    return [n.chave for n in a.em_ordem()]


# Arvore usada nos testes de remocao (ja balanceada, entao nenhuma
# rotacao acontece ao montar):
#           (5,1)
#          /     \
#      (3,2)     (8,3)
#      /   \        \
#  (1,4)  (4,5)    (9,6)

BASE = [(5, 1), (3, 2), (8, 3), (1, 4), (4, 5), (9, 6)]


def teste_remover_folha():
    a = montar(BASE)
    assert a.remover((1, 4))
    assert len(a) == 5
    assert a.buscar((1, 4)) is None
    assert chaves(a) == [(3, 2), (4, 5), (5, 1), (8, 3), (9, 6)]


def teste_remover_no_com_um_filho():
    a = montar(BASE)
    assert a.remover((8, 3))          # so tem filho direito (9,6)
    assert len(a) == 5
    assert a.raiz is not None
    filho = a.raiz.dir
    assert filho is not None
    assert filho.chave == (9, 6)
    assert chaves(a) == [(1, 4), (3, 2), (4, 5), (5, 1), (9, 6)]


def teste_remover_no_com_dois_filhos():
    a = montar(BASE)
    assert a.remover((3, 2))          # sucessor em ordem e (4,5)
    assert len(a) == 5
    assert a.raiz is not None
    filho = a.raiz.esq
    assert filho is not None
    assert filho.chave == (4, 5)
    assert filho.valor == "inimigo5"   # valor acompanha a chave
    assert a.buscar((3, 2)) is None
    assert chaves(a) == [(1, 4), (4, 5), (5, 1), (8, 3), (9, 6)]


def teste_remover_raiz():
    a = montar(BASE)
    assert a.remover((5, 1))          # sucessor em ordem e (8,3)
    assert a.raiz is not None
    assert a.raiz.chave == (8, 3)
    filho = a.raiz.dir
    assert filho is not None
    assert filho.chave == (9, 6)
    assert len(a) == 5
    assert chaves(a) == [(1, 4), (3, 2), (4, 5), (8, 3), (9, 6)]


def teste_remover_chave_inexistente():
    a = montar(BASE)
    assert not a.remover((7, 7))
    assert len(a) == 6
    assert chaves(a) == sorted(BASE)


def teste_remover_ate_esvaziar():
    a = montar(BASE)
    for c in BASE:
        assert a.remover(c)
    assert len(a) == 0
    assert a.raiz is None
    assert a.altura() == 0
    assert a.minimo() is None
    assert not a.remover((5, 1))


def teste_alturas_apos_remocao():
    a = montar(BASE)
    assert a.altura() == 3
    a.remover((1, 4))
    a.remover((4, 5))
    assert a.altura() == 3            # (5,1) -> (8,3) -> (9,6)
    a.remover((9, 6))
    assert a.altura() == 2
    assert a.raiz is not None
    assert a.raiz.altura == 2


def teste_minimo_maximo_apos_remocao():
    a = montar(BASE)
    a.remover((9, 6))
    a.remover((1, 4))
    maximo = a.maximo()
    minimo = a.minimo()
    assert maximo is not None
    assert minimo is not None
    assert maximo.chave == (8, 3)
    assert minimo.chave == (3, 2)


def verificar(a):
    """Confere as invariantes da AVL: ordem BST, alturas e balanceamento."""
    def rec(no, minimo, maximo):
        if no is None:
            return 0
        if minimo is not None:
            assert no.chave > minimo, "viola a ordem da BST"
        if maximo is not None:
            assert no.chave < maximo, "viola a ordem da BST"
        he = rec(no.esq, minimo, no.chave)
        hd = rec(no.dir, no.chave, maximo)
        assert no.altura == 1 + max(he, hd), "altura guardada esta errada"
        assert abs(he - hd) <= 1, f"no {no.chave} desbalanceado"
        return no.altura

    rec(a.raiz, None, None)
    assert len(a.em_ordem()) == len(a)


def teste_rotacao_ll():
    a = montar([(3, 1), (2, 2), (1, 3)])
    assert a.consumir_eventos() == [("LL", (3, 1))]
    assert a.raiz is not None
    assert a.raiz.chave == (2, 2)
    esquerda = a.raiz.esq
    direita = a.raiz.dir
    assert esquerda is not None and direita is not None
    assert esquerda.chave == (1, 3) and direita.chave == (3, 1)
    verificar(a)


def teste_rotacao_rr():
    a = montar([(1, 1), (2, 2), (3, 3)])
    assert a.consumir_eventos() == [("RR", (1, 1))]
    assert a.raiz is not None
    assert a.raiz.chave == (2, 2)
    esquerda = a.raiz.esq
    direita = a.raiz.dir
    assert esquerda is not None and direita is not None
    assert esquerda.chave == (1, 1) and direita.chave == (3, 3)
    verificar(a)


def teste_rotacao_lr():
    a = montar([(3, 1), (1, 2), (2, 3)])
    assert a.consumir_eventos() == [("LR", (3, 1))]
    assert a.raiz is not None
    assert a.raiz.chave == (2, 3)
    esquerda = a.raiz.esq
    direita = a.raiz.dir
    assert esquerda is not None and direita is not None
    assert esquerda.chave == (1, 2) and direita.chave == (3, 1)
    verificar(a)


def teste_rotacao_rl():
    a = montar([(1, 1), (3, 2), (2, 3)])
    assert a.consumir_eventos() == [("RL", (1, 1))]
    assert a.raiz is not None
    assert a.raiz.chave == (2, 3)
    esquerda = a.raiz.esq
    direita = a.raiz.dir
    assert esquerda is not None and direita is not None
    assert esquerda.chave == (1, 1) and direita.chave == (3, 2)
    verificar(a)


def teste_consumir_eventos_limpa():
    a = montar([(1, 1), (2, 2), (3, 3)])
    assert len(a.consumir_eventos()) == 1
    assert a.consumir_eventos() == []


def teste_insercao_sem_rotacao_nao_gera_evento():
    a = montar([(2, 1), (1, 2), (3, 3)])
    assert a.consumir_eventos() == []


def teste_insercao_crescente_fica_balanceada():
    a = ArvoreAVL()
    for i in range(1, 128):         # 127 = 2^7 - 1 chaves, arvore perfeita
        a.inserir((i, i))
        verificar(a)
    assert a.altura() == 7
    assert a.raiz is not None
    assert a.raiz.chave == (64, 64)


def teste_insercao_decrescente_fica_balanceada():
    a = ArvoreAVL()
    for i in range(127, 0, -1):
        a.inserir((i, i))
        verificar(a)
    assert a.altura() == 7


def teste_remocao_com_rotacao():
    a = montar([(2, 1), (1, 2), (3, 3), (4, 4)])
    a.consumir_eventos()
    assert a.remover((1, 2))        # (2,1) fica pesada a direita -> RR
    assert a.consumir_eventos() == [("RR", (2, 1))]
    assert a.raiz is not None
    assert a.raiz.chave == (3, 3)
    assert chaves(a) == [(2, 1), (3, 3), (4, 4)]
    verificar(a)


def teste_remocao_com_rotacao_dupla():
    a = montar([(3, 1), (1, 2), (5, 3), (4, 4)])
    a.consumir_eventos()
    assert a.remover((1, 2))        # (3,1) pesada a direita, filho a esquerda -> RL
    assert a.consumir_eventos() == [("RL", (3, 1))]
    assert a.raiz is not None
    assert a.raiz.chave == (4, 4)
    verificar(a)


def teste_remocao_do_sucessor_rebalanceia():
    # remover a raiz usa o sucessor da direita; isso pode desbalancear
    a = montar([(4, 1), (2, 2), (6, 3), (1, 4), (3, 5), (5, 6), (7, 7), (8, 8)])
    verificar(a)
    a.remover((4, 1))
    verificar(a)
    assert chaves(a) == [(1, 4), (2, 2), (3, 5), (5, 6), (6, 3), (7, 7), (8, 8)]


def teste_aleatorio_mantem_invariantes():
    import math
    import random
    rng = random.Random(42)
    a = ArvoreAVL()
    esperado = set()
    for _ in range(1500):
        c = (rng.randint(0, 40), rng.randint(0, 5))
        if rng.random() < 0.55:
            assert a.inserir(c) == (c not in esperado)
            esperado.add(c)
        else:
            assert a.remover(c) == (c in esperado)
            esperado.discard(c)
        verificar(a)
        assert len(a) == len(esperado)
        assert chaves(a) == sorted(esperado)
        if esperado:
            minimo = a.minimo()
            maximo = a.maximo()
            assert minimo is not None
            assert maximo is not None
            assert minimo.chave == min(esperado)
            assert maximo.chave == max(esperado)
            # limite teorico da AVL: h < 1.4405 * log2(n + 2)
            assert a.altura() < 1.4405 * math.log2(len(esperado) + 2)


if __name__ == "__main__":
    testes = [v for k, v in dict(globals()).items() if k.startswith("teste_")]
    for t in testes:
        t()
        print(f"ok  {t.__name__}")
    print(f"\n{len(testes)} testes passaram")
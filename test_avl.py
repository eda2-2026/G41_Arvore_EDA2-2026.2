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


# Arvore usada nos testes de remocao (sem balanceamento por enquanto):
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


if __name__ == "__main__":
    testes = [v for k, v in dict(globals()).items() if k.startswith("teste_")]
    for t in testes:
        t()
        print(f"ok  {t.__name__}")
    print(f"\n{len(testes)} testes passaram")
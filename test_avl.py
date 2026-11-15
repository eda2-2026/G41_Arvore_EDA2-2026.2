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


if __name__ == "__main__":
    testes = [v for k, v in dict(globals()).items() if k.startswith("teste_")]
    for t in testes:
        t()
        print(f"ok  {t.__name__}")
    print(f"\n{len(testes)} testes passaram")
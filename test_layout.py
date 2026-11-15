"""Testes do layout, sem janela. Rode com: python test_layout.py"""
import random

from avl import ArvoreAVL
from layout_arvore import MARGEM_TOPO, calcular_layout, raio_dos_nos

AREA = (100, 50, 800, 400)
MARGEM = 30


def montar(ameacas):
    a = ArvoreAVL()
    for i, ameaca in enumerate(ameacas):
        a.inserir((ameaca, i))
    return a


def teste_layout_vazio():
    assert calcular_layout(ArvoreAVL(), AREA) == []


def teste_um_no_fica_centralizado():
    [n] = calcular_layout(montar([5]), AREA)
    assert n.x == 100 + MARGEM + (800 - 2 * MARGEM) / 2
    assert n.y == 50 + MARGEM_TOPO
    assert n.pai is None
    assert n.fb == 0 and n.altura == 1


def teste_x_cresce_na_ordem_das_chaves():
    a = montar([5, 3, 8, 1, 4, 9, 7])
    layout = calcular_layout(a, AREA)
    assert [n.chave for n in layout] == [x.chave for x in a.em_ordem()]
    xs = [n.x for n in layout]
    assert xs == sorted(xs) and len(set(xs)) == len(xs)
    assert xs[0] == 100 + MARGEM and xs[-1] == 100 + 800 - MARGEM


def teste_y_depende_da_profundidade():
    a = montar([5, 3, 8, 1, 4, 9, 7])
    por_chave = {n.chave: n for n in calcular_layout(a, AREA)}
    assert a.raiz is not None
    raiz = por_chave[a.raiz.chave]
    assert raiz.y == 50 + MARGEM_TOPO
    for n in por_chave.values():
        if n.pai is not None:
            assert n.y > por_chave[n.pai].y, "filho tem de ficar abaixo do pai"
    # mesmo nivel -> mesmo y
    assert por_chave[(3, 1)].y == por_chave[(8, 2)].y


def teste_pai_aponta_para_o_no_certo():
    a = montar([5, 3, 8, 1, 4, 9, 7])
    for n in calcular_layout(a, AREA):
        if n.pai is None:
            assert a.raiz is not None
            assert n.chave == a.raiz.chave
        else:
            pai = a.buscar(n.pai)
            assert pai is not None
            assert n.chave in (pai.esq.chave if pai.esq else None,
                               pai.dir.chave if pai.dir else None)


def teste_fb_e_altura_vem_da_arvore():
    a = montar([5, 3, 8, 1])
    por_chave = {n.chave: n for n in calcular_layout(a, AREA)}
    assert a.raiz is not None
    assert por_chave[a.raiz.chave].altura == 3
    assert por_chave[(3, 1)].fb == 1


def teste_tudo_dentro_da_area():
    rng = random.Random(7)
    a = montar([rng.randint(1, 99) for _ in range(60)])
    for n in calcular_layout(a, AREA):
        assert 100 + MARGEM <= n.x <= 100 + 800 - MARGEM
        assert 50 + MARGEM_TOPO <= n.y <= 50 + 400 - MARGEM


def teste_raio_diminui_com_muitos_nos():
    assert raio_dos_nos(1, 800) == 20
    assert raio_dos_nos(5, 800) == 20
    assert raio_dos_nos(60, 800) < 20
    assert raio_dos_nos(10_000, 800) == 6      # nunca abaixo do minimo


if __name__ == "__main__":
    testes = [v for k, v in dict(globals()).items() if k.startswith("teste_")]
    for t in testes:
        t()
        print(f"ok  {t.__name__}")
    print(f"\n{len(testes)} testes passaram")
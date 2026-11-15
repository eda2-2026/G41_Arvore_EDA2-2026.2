"""Testes da logica do jogo, sem janela. Rode com: python test_partida.py"""
from partida import (BATERIA_X, DANO_MISSIL, PAUSA_ENTRE_ONDAS, SOLO_Y,
                     VIDA_BASE, Partida)
from test_avl import verificar


def parada(p, tipo, x, y):
    """Cria uma aeronave parada no ponto, para testes previsiveis."""
    a = p.gerar_aeronave(tipo)
    a.x, a.y, a.vx, a.vy = x, y, 0.0, 0.0
    return a


def nova():
    p = Partida(semente=1)
    p.a_gerar = 0               # sem novos nascimentos durante o teste
    return p


def teste_gerar_insere_no_radar():
    p = nova()
    a = p.gerar_aeronave("caca")
    assert len(p.arvore) == 1
    encontrado = p.arvore.buscar(a.chave)
    assert encontrado is not None
    assert encontrado.valor is a
    assert p.arvore_mudou
    assert 22 <= a.ameaca <= 26         # dano 10 + vel//10 = 12 + 0..4


def teste_ids_unicos_mesmo_com_ameaca_igual():
    p = nova()
    for _ in range(30):
        p.gerar_aeronave("drone")        # ameacas de 12 a 16, vai repetir
    assert len(p.arvore) == 30
    assert len({a.chave for a in p.aeronaves}) == 30


def teste_maior_ameaca_e_o_bombardeiro():
    p = nova()
    p.gerar_aeronave("drone")
    b = p.gerar_aeronave("bombardeiro")
    p.gerar_aeronave("caca")
    maximo = p.arvore.maximo()
    assert maximo is not None
    assert maximo.valor is b


def teste_impacto_tira_vida_da_base_e_sai_do_radar():
    p = nova()
    a = p.gerar_aeronave("caca")
    a.x, a.y, a.vx, a.vy = BATERIA_X, SOLO_Y - 1, 0.0, 100.0
    p.update(0.1)
    assert p.base_vida == VIDA_BASE - 10
    assert not p.aeronaves and len(p.arvore) == 0


def teste_tiro_abate_drone():
    p = nova()
    a = parada(p, "drone", BATERIA_X, 200)
    assert p.atirar(BATERIA_X, 200)
    for _ in range(120):
        p.update(1 / 60)
        if not p.aeronaves:
            break
    assert not p.aeronaves and len(p.arvore) == 0
    assert p.abates == 1 and p.pontos == a.ameaca


def teste_cadencia_do_tiro():
    p = nova()
    assert p.atirar(100, 100)
    assert not p.atirar(100, 100)        # ainda recarregando
    p.update(0.2)
    assert p.atirar(100, 100)


def teste_missil_vai_no_alvo_mais_perigoso():
    p = nova()
    parada(p, "drone", 300, 150)
    b = parada(p, "bombardeiro", BATERIA_X + 100, 150)
    assert p.disparar_missil()
    assert p.misseis[0].alvo == b.chave
    assert not p.disparar_missil()       # em recarga


def teste_missil_sem_alvo_nao_dispara():
    assert not nova().disparar_missil()


def teste_missil_abate_bombardeiro():
    p = nova()
    b = parada(p, "bombardeiro", BATERIA_X, 150)
    disparos = 0
    for _ in range(60 * 12):
        if p.disparar_missil():
            disparos += 1
        p.update(1 / 60)
        if not p.aeronaves:
            break
    assert not p.aeronaves and len(p.arvore) == 0
    assert disparos == -(-b.vida_max // DANO_MISSIL)    # 6 de vida / 3 = 2 misseis
    assert p.pontos == b.ameaca


def teste_missil_troca_de_alvo_quando_o_alvo_some():
    p = nova()
    d = parada(p, "drone", 300, 150)
    b = parada(p, "bombardeiro", BATERIA_X + 100, 150)
    p.disparar_missil()
    assert p.misseis[0].alvo == b.chave
    p._remover(b)                        # ex.: abatido por um tiro
    p.update(1 / 60)
    assert p.misseis[0].alvo == d.chave


def teste_onda_seguinte_depois_da_pausa():
    p = nova()
    p.update(0.1)                        # sem inimigos: onda limpa
    assert p.pausa_onda is not None and p.pontos == 50
    p.update(PAUSA_ENTRE_ONDAS + 0.1)
    assert p.onda == 2 and p.a_gerar == 8 and p.pausa_onda is None


def teste_fim_de_jogo():
    p = nova()
    p.base_vida = 1
    a = p.gerar_aeronave("drone")
    a.y = SOLO_Y
    p.update(0.01)
    assert p.fim and p.base_vida == 0
    pontos = p.pontos
    p.update(5)                          # depois do fim nada muda
    assert p.pontos == pontos and not p.atirar(10, 10)


def teste_simulacao_longa_mantem_radar_consistente():
    p = Partida(semente=5)
    dt = 1 / 60
    for frame in range(60 * 120):
        if p.aeronaves:
            alvo = max(p.aeronaves, key=lambda a: a.y)
            p.atirar(alvo.x + alvo.vx * 0.3, alvo.y + alvo.vy * 0.3)
        if frame % 100 == 0:
            p.disparar_missil()
        p.update(dt)
        if frame % 30 == 0:
            verificar(p.arvore)
            assert len(p.arvore) == len(p.aeronaves)
            assert sorted(a.chave for a in p.aeronaves) == \
                [n.chave for n in p.arvore.em_ordem()]
        if p.fim:
            break
    assert p.abates > 0


if __name__ == "__main__":
    testes = [v for k, v in dict(globals()).items() if k.startswith("teste_")]
    for t in testes:
        t()
        print(f"ok  {t.__name__}")
    print(f"\n{len(testes)} testes passaram")
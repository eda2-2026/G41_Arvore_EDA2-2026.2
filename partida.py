"""Logica do Air Defense, sem Pygame (assim da para testar sem abrir janela).

Como o jogo usa a arvore AVL (arvore.py/avl.py):
  - uma aeronave nasce            -> inserir(chave, aeronave)
  - uma aeronave e abatida ou
    chega ao solo                 -> remover(chave)
  - o missil escolhe o alvo       -> maximo()   (a maior ameaca do radar)
  - o missil confere se o alvo
    ainda existe                  -> buscar(chave)

A chave da arvore e (ameaca, id). A ameaca e definida no nascimento a
partir do tipo da aeronave e nao muda depois (se mudasse, a ordem da arvore
quebraria). O id desempata aeronaves com a mesma ameaca.

A lista `aeronaves` serve para mover e desenhar tudo a cada frame; a arvore
e o "radar" que mantem as aeronaves ordenadas por ameaca.
"""
import math
import random

from avl import ArvoreAVL

# ---------- campo de batalha ----------
LARGURA_CAMPO = 1280
ALTURA_CAMPO = 430
SOLO_Y = ALTURA_CAMPO - 28
BATERIA_X = LARGURA_CAMPO / 2
BATERIA_Y = SOLO_Y
CANO_Y = BATERIA_Y - 18         # de onde saem tiros e misseis

TIPOS = {
    "drone": dict(nome="Drone", vida=1, vel=75, dano=5, raio=11,
                  cor=(120, 205, 255)),
    "caca": dict(nome="Caça", vida=2, vel=120, dano=10, raio=13,
                 cor=(255, 200, 90)),
    "bombardeiro": dict(nome="Bombardeiro", vida=6, vel=45, dano=30, raio=18,
                        cor=(225, 115, 115)),
}

VIDA_BASE = 100
VEL_TIRO = 700
INTERVALO_TIRO = 0.16
VEL_MISSIL = 380
GIRO_MISSIL = 4.5               # rad/s: o missil faz curva, nao teleporta
INTERVALO_MISSIL = 1.6
DANO_MISSIL = 3
VIDA_MISSIL = 7.0               # segundos no ar
PAUSA_ENTRE_ONDAS = 3.0


class Aeronave:
    def __init__(self, id, tipo, x, y, vx, vy, ameaca):
        info = TIPOS[tipo]
        self.id = id
        self.tipo = tipo
        self.nome = info["nome"]
        self.cor = info["cor"]
        self.raio = info["raio"]
        self.dano = info["dano"]
        self.vida = self.vida_max = info["vida"]
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.ameaca = ameaca
        self.piscar = 0.0        # tempo restante do "flash" de dano

    @property
    def chave(self):
        return (self.ameaca, self.id)


class Tiro:
    def __init__(self, x, y, vx, vy):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy


class Missil:
    def __init__(self, x, y, alvo):
        self.x, self.y = x, y
        self.ang = -math.pi / 2  # sai apontando para cima
        self.alvo = alvo         # chave (ameaca, id) da aeronave perseguida
        self.vida = VIDA_MISSIL
        self.rastro = []


class Partida:
    def __init__(self, semente=None):
        self.rng = random.Random(semente)
        self.arvore = ArvoreAVL()
        self.arvore_mudou = False   # a interface le isso para redesenhar a arvore
        self.aeronaves = []
        self.tiros = []
        self.misseis = []
        self.base_vida = VIDA_BASE
        self.pontos = 0
        self.abates = 0
        self.onda = 1
        self.a_gerar = self._total_da_onda(1)
        self.prox_spawn = 1.0
        self.pausa_onda = None
        self.proximo_id = 1
        self.espera_tiro = 0.0
        self.espera_missil = 0.0
        self.fim = False
        self.log = []

    # ---------- ondas ----------
    def _total_da_onda(self, n):
        return 5 + 3 * (n - 1)

    def _intervalo_da_onda(self, n):
        return max(0.45, 1.6 - 0.12 * (n - 1))

    def _escolher_tipo(self):
        tipos = list(TIPOS)
        pesos = [6,
                 0 if self.onda < 2 else 2 + self.onda,
                 0 if self.onda < 3 else self.onda // 2 + 1]
        return self.rng.choices(tipos, weights=pesos, k=1)[0]

    def _atualizar_ondas(self, dt):
        if self.a_gerar > 0:
            self.prox_spawn -= dt
            if self.prox_spawn <= 0:
                self.gerar_aeronave()
                self.a_gerar -= 1
                self.prox_spawn = self._intervalo_da_onda(self.onda)
        elif not self.aeronaves:
            if self.pausa_onda is None:
                self.pausa_onda = PAUSA_ENTRE_ONDAS
                bonus = 50 * self.onda
                self.pontos += bonus
                self._registrar(f"Onda {self.onda} limpa! +{bonus}")
            self.pausa_onda -= dt
            if self.pausa_onda <= 0:
                self.onda += 1
                self.a_gerar = self._total_da_onda(self.onda)
                self.prox_spawn = 1.0
                self.pausa_onda = None

    # ---------- aeronaves ----------
    def gerar_aeronave(self, tipo=None, x=None):
        """Cria uma aeronave no topo e a insere no radar (arvore AVL)."""
        tipo = tipo or self._escolher_tipo()
        info = TIPOS[tipo]
        if x is None:
            x = self.rng.uniform(40, LARGURA_CAMPO - 40)
        y = -20.0
        alvo_x = min(max(self.rng.gauss(BATERIA_X, 260), 40), LARGURA_CAMPO - 40)
        dx, dy = alvo_x - x, SOLO_Y - y
        dist = math.hypot(dx, dy)
        vel = info["vel"] * min(1.6, 1 + 0.05 * (self.onda - 1))
        ameaca = info["dano"] + info["vel"] // 10 + self.rng.randint(0, 4)

        a = Aeronave(self.proximo_id, tipo, x, y,
                     dx / dist * vel, dy / dist * vel, ameaca)
        self.proximo_id += 1
        self.aeronaves.append(a)
        self.arvore.inserir(a.chave, a)
        self.arvore_mudou = True
        return a

    def _remover(self, a):
        self.aeronaves.remove(a)
        self.arvore.remover(a.chave)
        self.arvore_mudou = True

    def _abater(self, a):
        self.pontos += a.ameaca
        self.abates += 1
        self._registrar(f"{a.nome} abatido (ameaça {a.ameaca}) +{a.ameaca}")
        self._remover(a)

    def _causar_dano(self, a, valor):
        a.vida -= valor
        a.piscar = 0.12
        if a.vida <= 0:
            self._abater(a)

    def _registrar(self, texto):
        self.log.append(texto)
        del self.log[:-5]

    # ---------- disparos do jogador ----------
    def atirar(self, alvo_x, alvo_y):
        """Tiro manual na direcao do ponto. Devolve True se disparou."""
        if self.fim or self.espera_tiro > 0:
            return False
        dx, dy = alvo_x - BATERIA_X, alvo_y - CANO_Y
        dist = math.hypot(dx, dy)
        if dist < 1:
            return False
        self.tiros.append(Tiro(BATERIA_X, CANO_Y,
                               dx / dist * VEL_TIRO, dy / dist * VEL_TIRO))
        self.espera_tiro = INTERVALO_TIRO
        return True

    def disparar_missil(self):
        """Missil teleguiado na aeronave de maior ameaca (maximo da AVL)."""
        if self.fim or self.espera_missil > 0:
            return False
        alvo = self.arvore.maximo()
        if alvo is None:
            return False
        self.misseis.append(Missil(BATERIA_X, CANO_Y, alvo.chave))
        self.espera_missil = INTERVALO_MISSIL
        return True

    # ---------- atualizacao ----------
    def update(self, dt):
        if self.fim:
            return
        self.espera_tiro = max(0.0, self.espera_tiro - dt)
        self.espera_missil = max(0.0, self.espera_missil - dt)

        self._atualizar_ondas(dt)
        self._mover_aeronaves(dt)
        self._mover_tiros(dt)
        self._mover_misseis(dt)

        if self.base_vida <= 0:
            self.base_vida = 0
            self.fim = True
            self._registrar("A base foi destruída!")

    def _mover_aeronaves(self, dt):
        for a in list(self.aeronaves):
            a.x += a.vx * dt
            a.y += a.vy * dt
            a.piscar = max(0.0, a.piscar - dt)
            if a.y >= SOLO_Y:
                self.base_vida -= a.dano
                self._registrar(f"{a.nome} atingiu a base: -{a.dano}")
                self._remover(a)

    def _mover_tiros(self, dt):
        for t in list(self.tiros):
            t.x += t.vx * dt
            t.y += t.vy * dt
            if (t.x < -20 or t.x > LARGURA_CAMPO + 20
                    or t.y < -40 or t.y > ALTURA_CAMPO):
                self.tiros.remove(t)
                continue
            for a in self.aeronaves:
                if (a.x - t.x) ** 2 + (a.y - t.y) ** 2 <= (a.raio + 3) ** 2:
                    self.tiros.remove(t)
                    self._causar_dano(a, 1)
                    break

    def _mover_misseis(self, dt):
        for m in list(self.misseis):
            m.vida -= dt
            if m.vida <= 0:
                self.misseis.remove(m)
                continue

            # confere se o alvo ainda esta no radar; se nao, pega o novo maximo
            no = self.arvore.buscar(m.alvo)
            if no is None:
                no = self.arvore.maximo()
                if no is not None:
                    m.alvo = no.chave
            if no is not None:
                a = no.valor
                if a is None:
                    continue
                desejado = math.atan2(a.y - m.y, a.x - m.x)
                dif = (desejado - m.ang + math.pi) % (2 * math.pi) - math.pi
                passo = GIRO_MISSIL * dt
                m.ang += max(-passo, min(passo, dif))

            m.x += math.cos(m.ang) * VEL_MISSIL * dt
            m.y += math.sin(m.ang) * VEL_MISSIL * dt
            m.rastro.append((m.x, m.y))
            del m.rastro[:-14]

            if (m.x < -60 or m.x > LARGURA_CAMPO + 60
                    or m.y < -80 or m.y > ALTURA_CAMPO):
                self.misseis.remove(m)
                continue
            for a in self.aeronaves:
                if (a.x - m.x) ** 2 + (a.y - m.y) ** 2 <= (a.raio + 6) ** 2:
                    self.misseis.remove(m)
                    self._causar_dano(a, DANO_MISSIL)
                    break
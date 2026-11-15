"""Arvore AVL implementada manualmente para o Air Defense.

Cada no guarda uma chave (nivel de ameaca, id) e um valor (o inimigo).
O id entra na chave como desempate, entao duas aeronaves com a mesma
ameaca continuam tendo chaves distintas.

Estado atual: insercao, remocao, busca, minimo, maximo, percurso em ordem
e balanceamento por rotacoes (LL, RR, LR, RL).

Cada rotacao aplicada e registrada em `eventos` como uma tupla
(tipo, chave_do_no_desbalanceado), por exemplo ("LR", (5, 1)). A interface
do jogo usa isso para desenhar o rebalanceamento; `consumir_eventos()`
devolve a lista e a limpa.
"""


class No:
    def __init__(self, chave, valor=None):
        self.chave = chave      # tupla (ameaca, id)
        self.valor = valor      # objeto do jogo (ex.: inimigo)
        self.esq = None
        self.dir = None
        self.altura = 1         # folha tem altura 1


def altura(no):
    return no.altura if no else 0


def atualizar_altura(no):
    no.altura = 1 + max(altura(no.esq), altura(no.dir))


def fator_balanceamento(no):
    """Altura da subarvore esquerda menos a da direita."""
    return altura(no.esq) - altura(no.dir) if no else 0


def rotacao_direita(y):
    """Rotacao simples a direita. Devolve a nova raiz da subarvore.

            y                x
           / \\              / \\
          x   C    -->    A   y
         / \\                  / \\
        A   B                B   C
    """
    x = y.esq
    y.esq = x.dir
    x.dir = y
    atualizar_altura(y)     # y desceu, entao a altura dele vem primeiro
    atualizar_altura(x)
    return x


def rotacao_esquerda(x):
    """Rotacao simples a esquerda. Devolve a nova raiz da subarvore.

          x                    y
         / \\                  / \\
        A   y      -->      x   C
           / \\            / \\
          B   C          A   B
    """
    y = x.dir
    x.dir = y.esq
    y.esq = x
    atualizar_altura(x)
    atualizar_altura(y)
    return y


class ArvoreAVL:
    def __init__(self):
        self.raiz = None
        self.tamanho = 0
        self.eventos = []       # rotacoes aplicadas (para a interface)

    def consumir_eventos(self):
        """Devolve os eventos de rotacao acumulados e limpa a lista."""
        eventos, self.eventos = self.eventos, []
        return eventos

    def limpar(self):
        """Esvazia a arvore."""
        self.raiz = None
        self.tamanho = 0
        self.eventos = []

    # ---------- balanceamento ----------
    def _balancear(self, no):
        """Atualiza a altura do no e corrige o desbalanceamento, se houver.

        Devolve a nova raiz da subarvore.
        """
        atualizar_altura(no)
        fb = fator_balanceamento(no)

        if fb > 1:                                  # pesada a esquerda
            if fator_balanceamento(no.esq) < 0:     # filho pesado a direita
                self.eventos.append(("LR", no.chave))
                no.esq = rotacao_esquerda(no.esq)
            else:
                self.eventos.append(("LL", no.chave))
            return rotacao_direita(no)

        if fb < -1:                                 # pesada a direita
            if fator_balanceamento(no.dir) > 0:     # filho pesado a esquerda
                self.eventos.append(("RL", no.chave))
                no.dir = rotacao_direita(no.dir)
            else:
                self.eventos.append(("RR", no.chave))
            return rotacao_esquerda(no)

        return no

    # ---------- insercao ----------
    def inserir(self, chave, valor=None):
        """Insere a chave. Retorna False se ela ja existir."""
        self._inseriu = True
        self.raiz = self._inserir(self.raiz, chave, valor)
        if self._inseriu:
            self.tamanho += 1
        return self._inseriu

    def _inserir(self, no, chave, valor):
        if no is None:
            return No(chave, valor)
        if chave < no.chave:
            no.esq = self._inserir(no.esq, chave, valor)
        elif chave > no.chave:
            no.dir = self._inserir(no.dir, chave, valor)
        else:
            self._inseriu = False   # chave repetida
            return no
        return self._balancear(no)

    # ---------- remocao ----------
    def remover(self, chave):
        """Remove a chave. Retorna False se ela nao existir."""
        self._removeu = False
        self.raiz = self._remover(self.raiz, chave)
        if self._removeu:
            self.tamanho -= 1
        return self._removeu

    def _remover(self, no, chave):
        if no is None:
            return None             # chave nao encontrada

        if chave < no.chave:
            no.esq = self._remover(no.esq, chave)
        elif chave > no.chave:
            no.dir = self._remover(no.dir, chave)
        else:
            self._removeu = True
            # caso 1: folha, e caso 2: um filho so
            if no.esq is None:
                return no.dir
            if no.dir is None:
                return no.esq
            # caso 3: dois filhos -> troca pelo sucessor em ordem
            # (o menor no da subarvore direita) e remove o sucessor la
            sucessor = no.dir
            while sucessor.esq is not None:
                sucessor = sucessor.esq
            no.chave = sucessor.chave
            no.valor = sucessor.valor
            no.dir = self._remover_sucessor(no.dir)

        return self._balancear(no)

    def _remover_sucessor(self, no):
        """Remove o menor no da subarvore e devolve a nova raiz dela."""
        if no.esq is None:
            return no.dir
        no.esq = self._remover_sucessor(no.esq)
        return self._balancear(no)

    # ---------- busca ----------
    def buscar(self, chave):
        """Retorna o no com a chave ou None."""
        no = self.raiz
        while no is not None:
            if chave < no.chave:
                no = no.esq
            elif chave > no.chave:
                no = no.dir
            else:
                return no
        return None

    def minimo(self):
        no = self.raiz
        if no is None:
            return None
        while no.esq is not None:
            no = no.esq
        return no

    def maximo(self):
        no = self.raiz
        if no is None:
            return None
        while no.dir is not None:
            no = no.dir
        return no

    # ---------- percurso ----------
    def em_ordem(self):
        """Lista de nos em ordem crescente de chave."""
        resultado = []
        self._em_ordem(self.raiz, resultado)
        return resultado

    def _em_ordem(self, no, resultado):
        if no is None:
            return
        self._em_ordem(no.esq, resultado)
        resultado.append(no)
        self._em_ordem(no.dir, resultado)

    def altura(self):
        return altura(self.raiz)

    def __len__(self):
        return self.tamanho
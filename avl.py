"""Arvore AVL implementada manualmente para o Air Defense.

Cada no guarda uma chave (nivel de ameaca, id) e um valor (o inimigo).
O id entra na chave como desempate, entao duas aeronaves com a mesma
ameaca continuam tendo chaves distintas.

Estado atual: insercao, busca, minimo, maximo e percurso em ordem.
Remocao e rotacoes (balanceamento) entram nos proximos commits.
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


class ArvoreAVL:
    def __init__(self):
        self.raiz = None
        self.tamanho = 0

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
        atualizar_altura(no)
        return no

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
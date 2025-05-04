from pyDatalog import pyDatalog
import random
import os

# Inicializando pyDatalog
pyDatalog.create_terms('carta, pode_jogar')

# Fatos sobre as cartas
cores = ['vermelho', 'azul', 'verde', 'amarelo']
valores_numericos = list(range(0, 10))  # 0-9
valores_especiais = ['pular', 'inverter', '+2']
curingas = [('preto', 'curinga'), ('preto', '+4')]

# Criando as cartas
for cor in cores:
    pyDatalog.assert_fact('carta', cor, 0)
    for valor in valores_numericos[1:] + valores_especiais:
        pyDatalog.assert_fact('carta', cor, valor)
        pyDatalog.assert_fact('carta', cor, valor)

for _ in range(4):
    for cor, valor in curingas:
        pyDatalog.assert_fact('carta', cor, valor)

# Regras
def pode_jogar(carta_atual, carta_jogada, cor_curinga=None):
    if carta_jogada[0] == 'preto':
        return True
    if cor_curinga:
        return carta_jogada[0] == cor_curinga
    return carta_atual[0] == carta_jogada[0] or carta_atual[1] == carta_jogada[1]

def melhor_jogada(cartas, carta_atual, cor_curinga=None):
    for carta in cartas:
        if pode_jogar(carta_atual, carta, cor_curinga):
            return carta
    return None

def criar_baralho():
    baralho = []
    for cor in cores:
        baralho.append((cor, 0))
        for valor in valores_numericos[1:] + valores_especiais:
            baralho.append((cor, valor))
            baralho.append((cor, valor))
    for _ in range(4):
        baralho.extend(curingas)
    random.shuffle(baralho)
    return baralho

class EstadoJogo:
    def __init__(self):
        self.baralho = criar_baralho()
        self.mao_jogador = []
        self.mao_ia = []
        self.monte_descarte = []
        self.carta_atual = None
        self.cor_curinga = None
        self.turno = 'jogador'
        self.efeito_proximo_turno = None

def inicializar_jogo():
    estado = EstadoJogo()
    estado.mao_jogador = [estado.baralho.pop() for _ in range(7)]
    estado.mao_ia = [estado.baralho.pop() for _ in range(7)]

    while True:
        carta = estado.baralho.pop()
        if carta[0] != 'preto':
            estado.carta_atual = carta
            estado.monte_descarte.append(carta)
            break
        estado.baralho.insert(0, carta)
    return estado

def mostrar_mao(jogador):
    print("\nSuas cartas:")
    for i, carta in enumerate(jogador, 1):
        print(f"{i}. {carta[0]} {carta[1]}")

def escolher_cor():
    while True:
        cor = input("\nEscolha uma cor (vermelho, azul, verde, amarelo): ").strip().lower()
        if cor in cores:
            return cor
        print("Cor inválida.")

def aplicar_efeito(estado):
    if estado.efeito_proximo_turno == '+4':
        print("Você comprou 4 cartas devido ao +4.") if estado.turno == 'jogador' else print("IA comprou 4 cartas devido ao +4.")
        for _ in range(4):
            if estado.baralho:
                if estado.turno == 'jogador':
                    estado.mao_jogador.append(estado.baralho.pop())
                else:
                    estado.mao_ia.append(estado.baralho.pop())
        estado.efeito_proximo_turno = None
        return True
    elif estado.efeito_proximo_turno == '+2':
        print("Você comprou 2 cartas devido ao +2.") if estado.turno == 'jogador' else print("IA comprou 2 cartas devido ao +2.")
        for _ in range(2):
            if estado.baralho:
                if estado.turno == 'jogador':
                    estado.mao_jogador.append(estado.baralho.pop())
                else:
                    estado.mao_ia.append(estado.baralho.pop())
        estado.efeito_proximo_turno = None
        return True
    return False

def turno_jogador(estado):
    if aplicar_efeito(estado):
        return False

    print(f"\nCarta atual: {estado.carta_atual[0]} {estado.carta_atual[1]}")
    mostrar_mao(estado.mao_jogador)

    jogavel = [c for c in estado.mao_jogador if pode_jogar(estado.carta_atual, c, estado.cor_curinga)]
    if not jogavel:
        print("Nenhuma jogada possível. Você comprou uma carta.")
        if estado.baralho:
            nova = estado.baralho.pop()
            estado.mao_jogador.append(nova)
            if pode_jogar(estado.carta_atual, nova, estado.cor_curinga):
                print("Você pode jogar a carta comprada.")
                estado.mao_jogador.remove(nova)
                estado.carta_atual = nova
                estado.monte_descarte.append(nova)
                if nova[0] == 'preto':
                    estado.cor_curinga = escolher_cor()
                    if nova[1] == '+4':
                        estado.efeito_proximo_turno = '+4'
                elif nova[1] == '+2':
                    estado.efeito_proximo_turno = '+2'
                elif nova[1] == 'pular':
                    return True
        return False

    while True:
        escolha = input("\nDigite o número da carta ou 'comprar': ").strip().lower()
        if escolha == 'comprar':
            if estado.baralho:
                nova = estado.baralho.pop()
                estado.mao_jogador.append(nova)
                print("Você comprou uma carta.")
            return False
        try:
            idx = int(escolha) - 1
            carta_escolhida = estado.mao_jogador[idx]
            if pode_jogar(estado.carta_atual, carta_escolhida, estado.cor_curinga):
                estado.mao_jogador.pop(idx)
                estado.carta_atual = carta_escolhida
                estado.monte_descarte.append(carta_escolhida)
                estado.cor_curinga = None
                if carta_escolhida[0] == 'preto':
                    estado.cor_curinga = escolher_cor()
                    if carta_escolhida[1] == '+4':
                        estado.efeito_proximo_turno = '+4'
                elif carta_escolhida[1] == '+2':
                    estado.efeito_proximo_turno = '+2'
                if len(estado.mao_jogador) == 1:
                    print("\nUNO!")
                return carta_escolhida[1] == 'pular'
            else:
                print("Jogada inválida!")
        except:
            print("Entrada inválida!")

def turno_ia(estado):
    if aplicar_efeito(estado):
        return False

    print("\n--- VEZ DA IA ---")
    jogada = melhor_jogada(estado.mao_ia, estado.carta_atual, estado.cor_curinga)

    if jogada:
        estado.mao_ia.remove(jogada)
        estado.carta_atual = jogada
        estado.monte_descarte.append(jogada)
        estado.cor_curinga = None
        print(f"IA jogou: {jogada[0]} {jogada[1]}")
        if jogada[0] == 'preto':
            estado.cor_curinga = random.choice(cores)
            print(f"IA escolheu a cor: {estado.cor_curinga}")
            if jogada[1] == '+4':
                estado.efeito_proximo_turno = '+4'
        elif jogada[1] == '+2':
            estado.efeito_proximo_turno = '+2'
        if len(estado.mao_ia) == 1:
            print("IA grita UNO!")
        return jogada[1] == 'pular'
    else:
        if estado.baralho:
            nova = estado.baralho.pop()
            estado.mao_ia.append(nova)
            print("IA comprou uma carta.")
            if pode_jogar(estado.carta_atual, nova, estado.cor_curinga):
                estado.mao_ia.remove(nova)
                estado.carta_atual = nova
                estado.monte_descarte.append(nova)
                estado.cor_curinga = None
                print("IA jogou a carta comprada.")
                if nova[0] == 'preto':
                    estado.cor_curinga = random.choice(cores)
                    print(f"IA escolheu a cor: {estado.cor_curinga}")
                    if nova[1] == '+4':
                        estado.efeito_proximo_turno = '+4'
                elif nova[1] == '+2':
                    estado.efeito_proximo_turno = '+2'
                return nova[1] == 'pular'
        return False

def verificar_vitoria(estado):
    if not estado.mao_jogador:
        print("\nVocê venceu!")
        return True
    elif not estado.mao_ia:
        print("\nA IA venceu!")
        return True
    return False

if __name__ == "__main__":
    print("\n=== INICIANDO IAUNO ===")
    estado = inicializar_jogo()

    while True:
        if estado.turno == 'jogador':
            repetir = turno_jogador(estado)
            if not repetir:
                estado.turno = 'ia'
        else:
            repetir = turno_ia(estado)
            if not repetir:
                estado.turno = 'jogador'

        if verificar_vitoria(estado):
            break

        if not estado.baralho:
            print("\nO baralho acabou! Fim de jogo.")
            break


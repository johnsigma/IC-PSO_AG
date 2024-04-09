import json
import random

# random.seed(675)

PORCENTAGEM_SELECAO = 0.5


def ler_arquivo(nomeArquivo, numTarefas, dicionarioTarefas):
    with open(nomeArquivo, 'r') as arquivo:
        # Itera sobre cada linha no arquivo
        i = 0
        for linha in arquivo:
            if i == 0:
                numTarefas = int(linha.strip()) + 2
            else:
                if linha.__contains__('#'):
                    continue
                linha = linha.strip().split(' ')
                linha_formatada = [valor for valor in linha if valor != '']
                dicionarioTarefas[linha_formatada[0]] = {
                    'tarefa': linha_formatada[0],
                    'tempo_execucao': linha_formatada[1],
                    'num_predecessores': linha_formatada[2],
                    'predecessores': linha_formatada[3:]
                }
            i += 1
    return numTarefas, dicionarioTarefas


def selecaoIndividuos(populacao, dicionarioTarefas, numProcessadores, numTarefas, tamanhoPopulacao):

    individuosSelecionados = []
    individuosSorteados = []
    while True:
        if len(individuosSelecionados) == int(tamanhoPopulacao * PORCENTAGEM_SELECAO):
            break

        individuo1 = None
        individuo2 = None

        while True:
            individuo1 = random.choice(populacao)
            if individuo1 not in individuosSorteados:
                individuosSorteados.append(individuo1)
                break

        while True:
            individuo2 = random.choice(populacao)
            if individuo2 not in individuosSorteados:
                individuosSorteados.append(individuo2)
                break

        fitness1 = fitness(individuo1, dicionarioTarefas,
                           numProcessadores, numTarefas)
        fitness2 = fitness(individuo2, dicionarioTarefas,
                           numProcessadores, numTarefas)

        if fitness1 < fitness2:
            individuosSelecionados.append(individuo1)
            continue

        individuosSelecionados.append(individuo2)

    return individuosSelecionados


def geraPrimeiraParteIndividuo(numProcessadores, numTarefas):
    primeiraParteIndividuo = []

    for _ in range(numTarefas):
        processador = random.randint(0, numProcessadores - 1)
        primeiraParteIndividuo.append(processador)

    return primeiraParteIndividuo


def geraSegundaParteIndividuo(numTarefas, dicionarioTarefas):
    segundaParteIndividuo = []

    while True:

        if len(segundaParteIndividuo) == numTarefas:
            break

        tarefa = str(random.randint(0, numTarefas - 1))

        if tarefa in segundaParteIndividuo:
            continue

        predecessores = dicionarioTarefas[tarefa]['predecessores']

        if len(predecessores) == 0:
            segundaParteIndividuo.append(tarefa)
            continue

        predecessorEstaNaLista = True
        for predecessor in predecessores:
            if predecessor not in segundaParteIndividuo:
                predecessorEstaNaLista = False

        if predecessorEstaNaLista:
            segundaParteIndividuo.append(tarefa)

    return segundaParteIndividuo


def populacaoInicial(numTarefas, numProcessadores, tamanhoPopulacao, dicionarioTarefas):
    populacao = []

    while True:

        if len(populacao) == tamanhoPopulacao:
            break

        individuo = {
            'mapeamento': geraPrimeiraParteIndividuo(numProcessadores, numTarefas),
            'sequencia': geraSegundaParteIndividuo(numTarefas, dicionarioTarefas)
        }

        if len(individuo['mapeamento']) > 0 and len(individuo['sequencia']) > 0 and individuo:
            # print(individuo)
            populacao.append(individuo)

    return populacao


def crossover_map(pai1, pai2, numTarefas):
    ponto_corte = random.randint(0, numTarefas - 1)
    filho1 = {
        'mapeamento': [],
        'sequencia': pai1['sequencia']
    }
    filho2 = {
        'mapeamento': [],
        'sequencia': pai2['sequencia']
    }

    filho1['mapeamento'] = pai1['mapeamento'][:ponto_corte] + \
        pai2['mapeamento'][ponto_corte:]

    filho2['mapeamento'] = pai2['mapeamento'][:ponto_corte] + \
        pai1['mapeamento'][ponto_corte:]

    return [filho1, filho2]


def crossover_seq(pai1, pai2, numTarefas):
    ponto_corte = random.randint(0, numTarefas - 1)
    filho = {
        'mapeamento': pai1['mapeamento'],
        'sequencia': []
    }

    tarefasCorte = pai1['sequencia'][:ponto_corte]
    filho['sequencia'] = tarefasCorte

    for tarefa in pai2['sequencia']:
        if tarefa not in tarefasCorte:
            filho['sequencia'].append(tarefa)

    return filho


def mutacao(pai, numeroProcessadores):
    posicao = random.randint(0, len(pai['sequencia']) - 1)

    while True:
        novoProcessador = random.randint(0, numeroProcessadores - 1)

        if novoProcessador != pai['mapeamento'][posicao]:
            pai['mapeamento'][posicao] = novoProcessador
            break

    return pai


def fitness(individuo, dicionarioTarefas, numProcessadores, numTarefas):
    RT = [0] * numProcessadores  # RT = Ready Time
    ST = [0] * numTarefas  # ST = Start Time
    FT = [0] * numTarefas  # FT = Finish Time
    # LT = List of Tasks # LT = list(individuo['sequencia'])
    LT = list(individuo['sequencia'])
    S_length = 1

    for _ in range(numTarefas):
        if len(LT) == 0:  # if not LT:
            break
        tarefa = int(LT.pop(0))
        j = 0
        for j in range(numProcessadores):
            if individuo['mapeamento'][tarefa] == j:
                ST[tarefa] = max(RT[j], FT[tarefa])
                FT[tarefa] = ST[tarefa] + \
                    int(dicionarioTarefas[str(tarefa)]['tempo_execucao'])
                RT[j] = FT[tarefa]
            # j += 1

        S_length = max(FT)
        # i += 1
    a = 1
    return (a / S_length)


def main(populacao, dicionarioTarefas, numProcessadores, numTarefas, tamanhoPopulacao, numeroIteracoes, chance_crossover, chance_mutacao):

    melhorIndividuo = None

    for iteracao in range(numeroIteracoes):

        if iteracao == 0:
            melhorIndividuo = {
                'individuo': min(populacao, key=lambda individuo: fitness(individuo, dicionarioTarefas, numProcessadores, numTarefas)),
                'iteracao': iteracao + 1,
                'fitness': fitness(min(populacao, key=lambda individuo: fitness(individuo, dicionarioTarefas, numProcessadores, numTarefas)), dicionarioTarefas, numProcessadores, numTarefas)
            }

        fitnessMedia = sum([fitness(
            individuo, dicionarioTarefas, numProcessadores, numTarefas) for individuo in populacao]) / len(populacao)

        print(f'Média fitness da população: {fitnessMedia:.7f}')

        melhorIndividuoDaPopulacao = {
            'individuo': min(populacao, key=lambda individuo: fitness(individuo, dicionarioTarefas, numProcessadores, numTarefas)),
            'iteracao': iteracao + 1,
            'fitness': fitness(min(populacao, key=lambda individuo: fitness(individuo, dicionarioTarefas, numProcessadores, numTarefas)), dicionarioTarefas, numProcessadores, numTarefas)
        }

        if (melhorIndividuoDaPopulacao['fitness'] < melhorIndividuo['fitness']):
            melhorIndividuo = melhorIndividuoDaPopulacao

        individuosSelecionados = sorted(populacao, key=lambda individuo: fitness(
            individuo, dicionarioTarefas, numProcessadores, numTarefas))[:int(tamanhoPopulacao * PORCENTAGEM_SELECAO)]

        # selecaoIndividuos(
        #     populacao, dicionarioTarefas, numProcessadores, numTarefas, tamanhoPopulacao)

        while len(individuosSelecionados) > 1:
            pai1 = individuosSelecionados.pop(0)
            pai2 = individuosSelecionados.pop(0)

            rn = random.random()

            if rn < chance_crossover:
                filhos = crossover_map(pai1, pai2, numTarefas)
                populacao.extend(filhos)
            else:
                filho = crossover_seq(pai1, pai2, numTarefas)
                populacao.append(filho)

            mutacao1 = random.random()
            mutacao2 = random.random()

            if mutacao1 < chance_mutacao:
                indice = populacao.index(pai1)
                pai1 = mutacao(pai1, numProcessadores)
                populacao[indice] = pai1

            if mutacao2 < chance_mutacao:
                indice = populacao.index(pai2)
                pai2 = mutacao(pai2, numProcessadores)
                populacao[indice] = pai2

        populacao = random.sample(populacao, tamanhoPopulacao)

    print('Melhor indivíduo:\n')
    print(f'Iteração: {melhorIndividuo["iteracao"]}')
    print(f'Fitness: {melhorIndividuo["fitness"]:.7f}')
    # print(json.dumps(melhorIndividuo, indent=4))
    # print(json.dumps(populacao, indent=4))

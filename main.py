import random
import time
import mainAG as ag
import json

# random.seed(42)

# melhorPosicaoGlobal = 0


def ler_arquivo(nomeArquivo, numTarefas, dicionarioTarefas):
    with open(nomeArquivo, 'r') as arquivo:
        # Itera sobre cada linha no arquivo
        i = 0
        for linha in arquivo:
            if i == 0:
                numTarefas = int(linha.strip()) + 2
            else:
                if linha.__contains__('#'):
                    break
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


def calcula_fitness(particula, numProcessadores, numTarefas, dicionarioTarefas):

    RT = [0] * numProcessadores
    ST = [0] * numTarefas
    FT = [0] * numTarefas

    LT = list(map(lambda x: x['tarefa'], particula))

    S_length = 1

    for _ in range(numTarefas):
        if len(LT) == 0:
            break

        tarefa = int(LT.pop(0))

        for j in range(numProcessadores):
            if particula[tarefa]['processador'] == j:
                ST[tarefa] = max(RT[j], FT[tarefa])
                FT[tarefa] = ST[tarefa] + \
                    int(dicionarioTarefas[str(tarefa)]['tempo_execucao'])
                RT[j] = FT[tarefa]

        S_length = max(FT)

    a = 1

    return (a / S_length)


def inicializa_espaco_de_busca(numTarefas, numProcessadores, tamanhoPopulacao, dicionarioTarefas):
    espacoDeBusca = []

    for _ in range(tamanhoPopulacao):
        particula = []
        tarefasAlocadas = []

        while len(particula) < numTarefas:

            while True:

                if len(particula) == 0:
                    tarefasAlocadas.append(0)
                    particula.append({
                        'tarefa': '0',
                        'processador': random.randint(0, numProcessadores-1)
                    })
                    continue

                if len(particula) == numTarefas-1 and numTarefas-1 not in tarefasAlocadas:
                    tarefasAlocadas.append(numTarefas-1)
                    particula.append({
                        'tarefa': str(numTarefas-1),
                        'processador': random.randint(0, numProcessadores-1)
                    })
                    break

                indiceTarefa = random.randint(0, numTarefas-1)

                if indiceTarefa in tarefasAlocadas:
                    continue

                tarefa = dicionarioTarefas[str(indiceTarefa)]

                predecessores = tarefa['predecessores']
                numPredecessores = len(predecessores)
                predecessoresEncontrados = 0

                if (numPredecessores >= 1):
                    for individuo in particula:
                        tarefaAux = individuo['tarefa']
                        if tarefaAux in predecessores:
                            predecessoresEncontrados += 1

                if predecessoresEncontrados == numPredecessores:
                    particula.append({
                        'tarefa': str(indiceTarefa),
                        'processador': random.randint(0, numProcessadores-1)
                    })
                    tarefasAlocadas.append(indiceTarefa)
                    break

        espacoDeBusca.append(particula)

    return espacoDeBusca


def inicializa_exame(tamanhoEnxame, espacoDeBusca, numProcessadores, numTarefas, dicionarioTarefas):
    enxame = []
    for i in range(tamanhoEnxame):
        posicao = random.randint(0, len(espacoDeBusca)-1)
        fitness = calcula_fitness(
            espacoDeBusca[posicao], numProcessadores, numTarefas, dicionarioTarefas)
        particula = {
            'posicao_atual': posicao,
            'melhor_posicao': posicao,
            'velocidade': 0,
            'fitness_atual': fitness,
            'melhor_fitness': fitness
        }
        enxame.append(particula)

    return enxame


def melhor_fitness_global(enxame, espacoDeBusca, numProcessadores, numTarefas, dicionarioTarefas):
    melhor = {
        'fitness': enxame[0]['fitness_atual'],
        'posicao': enxame[0]['posicao_atual']
    }
    for i in range(len(enxame)):
        fitness = calcula_fitness(espacoDeBusca[enxame[i]['posicao_atual']],
                                  numProcessadores, numTarefas, dicionarioTarefas)
        if fitness < melhor['fitness']:
            melhor['fitness'] = fitness
            melhor['posicao'] = enxame[i]['posicao_atual']

    return melhor


def pso(iteracoes, enxame, espacoDeBusca, numProcessadores, numTarefas, dicionarioTarefas, inercia, C1, C2, vMax):

    melhor_global = melhor_fitness_global(
        enxame, espacoDeBusca, numProcessadores, numTarefas, dicionarioTarefas)

    for _ in range(iteracoes):

        for particula in enxame:

            # Atualiza a velocidade
            velocidade_atual = particula['velocidade']
            posicao_atual = particula['posicao_atual']
            velocidade_atual = inercia * velocidade_atual + C1 * random.random() * \
                (particula['melhor_posicao'] - posicao_atual) + C2 * \
                random.random() * (melhor_global['posicao'] - posicao_atual)

            # Verifica se a velocidade não ultrapassa a velocidade máxima
            # if abs(velocidade_atual) > vMax:
            #     velocidade_atual = velocidade_atual * \
            #         (vMax / abs(velocidade_atual))

            # Atualiza a posição
            posicao_atual = int(posicao_atual + velocidade_atual)

            # Verifica se a posição está dentro do espaço de busca
            if posicao_atual < 0 or posicao_atual >= len(espacoDeBusca):
                posicao_atual = random.randint(0, len(espacoDeBusca)-1)

            particula['posicao_atual'] = posicao_atual
            particula['velocidade'] = velocidade_atual
            fitness_atual = calcula_fitness(
                espacoDeBusca[posicao_atual], numProcessadores, numTarefas, dicionarioTarefas)
            particula['fitness_atual'] = fitness_atual

            # Atualiza a melhor posição local
            if fitness_atual < particula['melhor_fitness']:
                particula['melhor_fitness'] = fitness_atual
                particula['melhor_posicao'] = posicao_atual

            # Atualiza a melhor posição global
            if fitness_atual < melhor_global['fitness']:
                melhor_global['fitness'] = fitness_atual
                melhor_global['posicao'] = posicao_atual

    return enxame


def transformaParticulaEmIndividuo(particula, espacoBusca):
    individuo = {
        'mapeamento': [],
        'sequencia': []
    }

    solucao = espacoBusca[particula['posicao_atual']]

    for tarefa in solucao:
        individuo['mapeamento'].append(tarefa['processador'])
        individuo['sequencia'].append(tarefa['tarefa'])

    return individuo


def geraIndividuos(enxame, espacoBusca):
    individuos = []
    for particula in enxame:
        individuos.append(
            transformaParticulaEmIndividuo(particula, espacoBusca))
    return individuos


if __name__ == '__main__':

    inicio = time.time()

    # Parametros do PSO
    dicionarioTarefas = {}
    numTarefas = 0
    nomeArquivo = 'sparse.stg'
    numProcessadores = 4
    tamanhoPopulacao = 500000
    tamanhoEnxame = 100
    iteracoes = 3000
    C1 = 2
    C2 = 2
    inercia = 0.4
    vMax = 100

    # Parametros do AG
    tamanhoPopulacaoAG = tamanhoEnxame
    taxaCruzamento = 0.4
    taxaMutacao = 0.1
    numGeracoes = 2000

    numTarefas, dicionarioTarefas = ler_arquivo(
        nomeArquivo, numTarefas, dicionarioTarefas)

    # espacoBusca = inicializa_espaco_de_busca(
    #     numTarefas, numProcessadores, tamanhoPopulacao, dicionarioTarefas)

    # controle = input('Deseja executar o PSO? (s/n): ')
    # if (controle == 'n'):
    #     exit()

    # with open("populacao_sparse.txt", "w") as arquivo:
    #     json.dump(espacoBusca, arquivo)

    espacoBusca = []

    with open("populacao_sparse.txt", "r") as arquivo:
        espacoBusca = json.load(arquivo)

    melhor_f = calcula_fitness(
        espacoBusca[0], numProcessadores, numTarefas, dicionarioTarefas)
    media_populacao = 0

    for particula in espacoBusca:
        f = calcula_fitness(particula, numProcessadores,
                            numTarefas, dicionarioTarefas)
        media_populacao += f
        if f < melhor_f:
            melhor_f = f

    media_populacao = media_populacao / len(espacoBusca)
    # print('Melhor fitness possivel:', melhor_f)
    # print('Media populacao:', media_populacao)

    # espacoBusca = random.sample(espacoBusca, tamanhoPopulacao)

    enxame = inicializa_exame(
        tamanhoEnxame, espacoBusca, numProcessadores, numTarefas, dicionarioTarefas)

    # print('Enxame antes do PSO:')
    # for particula in enxame:
    #     print(particula)

    enxame = pso(iteracoes, enxame, espacoBusca, numProcessadores,
                 numTarefas, dicionarioTarefas, inercia, C1, C2, vMax)

    # print('\n\nEnxame depos do PSO:')
    # for particula in enxame:
    #     print(particula)

    # for particula in enxame:
    #     solucao = espacoBusca[particula['posicao_atual']]
    #     print(solucao)

    individuos = geraIndividuos(enxame, espacoBusca)

    # for individuo in individuos:
    #     print(individuo)

    ag.main(individuos, dicionarioTarefas, numProcessadores, numTarefas,
            tamanhoPopulacaoAG, numGeracoes, taxaCruzamento, taxaMutacao)

    melhor_global = melhor_fitness_global(
        enxame, espacoBusca, numProcessadores, numTarefas, dicionarioTarefas)
    print('\n\nMelhor global:', melhor_global)
    print('Melhor fitness possivel:', melhor_f)
    print('Media populacao:', media_populacao)

    fim = time.time()

    print(f'\n\nTempo de execução: {fim - inicio} segundos.')

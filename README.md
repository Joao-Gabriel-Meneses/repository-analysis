# 📊 Saúde de Repositórios Open-Source e o Impacto da IA Generativa

Este repositório contém a arquitetura de mineração de repositórios desenvolvida para a disciplina de **Tópicos Especiais em Linguagem de Programação**. O objetivo é extrair, consolidar e analisar métricas de saúde, inovação e cultura de projetos open-source em dois recortes temporais: **Pré-IA Generativa** (2021 a 2022) e **Pós-IA Generativa** (2022 a 2024).

## 🗂️ Repositórios Analisados
A equipe de 3 membros selecionou 4 repositórios:
- **Base/Obrigatório:** `pallets/flask`
- **Escolhidos:** `lutris/lutris` e `Heroic-Games-Launcher/HeroicGamesLauncher`
- **Adicional (Trio):** `torvalds/linux`

## 🏗️ Arquitetura do Projeto

O processamento dos dados foi dividido em duas frentes para contornar gargalos de tamanho (caso do Kernel do Linux) e limites de requisição da API do GitHub:

1. **Script Local (`repository_miner.py`):** Realiza o *shallow clone* de Flask, Lutris e Heroic. Faz o *parsing* do log do Git em busca de dias com commit, bus factor, gargalos arquiteturais e horários de trabalho. Em seguida, consome a Search API do GitHub para determinar a Taxa de Aceitação de Pull Requests.
2. **Jupyter Notebook (`mineracao_linux_e_graficos.ipynb`):** Desenhado para rodar na nuvem (Google Colab). Clona o colossal Kernel do Linux via hiper-filtro `--filter=blob:none`, extrai suas métricas isoladamente, recebe os CSVs gerados pelo script local e utiliza Pandas e Seaborn para processar o Ranking e as Visualizações Finais.

## 🚀 Como Executar

### Parte 1: Mineração Local
1. Instale as bibliotecas base:
   ```bash
   pip install PyGithub pandas
   ```
2. Defina o seu token pessoal do GitHub no terminal para evitar os limites restritos da API (Search API é muito sensível sem autenticação):
   ```bash
   export GITHUB_TOKEN="seu_token_aqui"
   ```
3. Execute o extrator:
   ```bash
   python repository_miner.py
   ```
   > O script clonará as pastas `flask`, `lutris` e `heroic` localmente. Ao terminar, ele gerará 3 arquivos de saída: `metricas_saude_menores.csv`, `arquivos_top5_menores.csv` e `horas_commits_menores.csv`.

### Parte 2: Consolidando e Plotando (Google Colab)
1. Faça o upload do arquivo `mineracao_linux_e_graficos.ipynb` para o seu [Google Colab](https://colab.research.google.com/).
2. Execute as duas primeiras células para extrair o Kernel do Linux remotamente.
3. Na célula de **Upload**, selecione os **3 arquivos CSV** que foram exportados na Etapa 1.
4. Execute as células de plotagem para renderizar os *Barplots* e *Lineplots* definitivos para a sua apresentação visual.

## 📈 Métricas Avaliadas (Metodologia)
- **Atividade Contínua:** Porcentagem de dias do período que contiveram ao menos 1 commit.
- **Distribuição de Carga (Bus Factor):** Média global de commits dividida por autor/desenvolvedor único.
- **Aceitação da Comunidade:** Porcentagem de *Pull Requests Mesclados (Merged)* em relação aos *Criados*.
- **Gargalos da Arquitetura:** Identificação direta no histórico dos 5 arquivos tocados em mais commits.
- **Cultura de Trabalho:** Volume bruto de commits agregados por horário de Brasília (0h às 23h).

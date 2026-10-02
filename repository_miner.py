import os
import subprocess
import csv
import time
from datetime import datetime
from github import Github, Auth
from github.GithubException import RateLimitExceededException

# Autenticação corrigida (sem DeprecationWarning)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
if GITHUB_TOKEN:
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
else:
    g = Github()

REPOS = {
    "flask": "pallets/flask",
    "lutris": "lutris/lutris",
    "heroic": "Heroic-Games-Launcher/HeroicGamesLauncher"
}

PERIODS = {
    "Pre-IA": ("2021-01-01", "2022-11-29"),
    "Pos-IA": ("2022-11-30", "2024-05-30")
}

def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return result.stdout.strip()

def clone_or_fetch(repo_name, github_path):
    if not os.path.exists(repo_name):
        print(f"A clonar {repo_name}...")
        run_cmd(f"git clone --shallow-since='2020-12-01' https://github.com/{github_path}.git {repo_name}")
    else:
        print(f"A atualizar {repo_name}...")
        run_cmd("git fetch --shallow-since='2020-12-01'", cwd=repo_name)

def extract_git_metrics(repo_name, start_date, end_date):
    d1 = datetime.strptime(start_date, "%Y-%m-%d")
    d2 = datetime.strptime(end_date, "%Y-%m-%d")
    total_days = (d2 - d1).days + 1

    # Atividade Contínua
    dates = run_cmd(f"git log --since='{start_date}T00:00:00' --until='{end_date}T23:59:59' --date=short --format='%ad'", cwd=repo_name).splitlines()
    unique_days = len(set(dates))
    continuous_activity = (unique_days / total_days) * 100 if total_days > 0 else 0

    # Distribuição de Carga (Bus Factor)
    authors = run_cmd(f"git log --since='{start_date}T00:00:00' --until='{end_date}T23:59:59' --format='%aE'", cwd=repo_name).splitlines()
    total_commits = len(authors)
    unique_authors = len(set(authors))
    bus_factor = total_commits / unique_authors if unique_authors > 0 else 0

    # Gargalos da Arquitetura (Top 5 Arquivos)
    files_output = run_cmd(f"git log --since='{start_date}T00:00:00' --until='{end_date}T23:59:59' --name-only --format='' | grep -v '^$'", cwd=repo_name).splitlines()
    file_counts = {}
    for f in files_output:
        file_counts[f] = file_counts.get(f, 0) + 1
    top_5_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    # Cultura de Trabalho (Horas)
    hours_output = run_cmd(f"git log --since='{start_date}T00:00:00' --until='{end_date}T23:59:59' --date=format:'%H' --format='%ad'", cwd=repo_name).splitlines()
    hour_counts = {str(i).zfill(2): 0 for i in range(24)}
    for h in hours_output:
        hour_counts[h] = hour_counts.get(h, 0) + 1

    return continuous_activity, bus_factor, top_5_files, hour_counts

def extract_github_metrics(github_path, start_date, end_date):
    query_total = f"repo:{github_path} is:pr created:{start_date}..{end_date}"
    query_merged = f"repo:{github_path} is:pr is:merged created:{start_date}..{end_date}"
    
    # Função interna para gerir o rate limit de forma reativa (com base no erro)
    def do_search(query):
        while True:
            try:
                return g.search_issues(query).totalCount
            except RateLimitExceededException:
                print(f"  [Aviso] Limite de pesquisa atingido. A aguardar 60 segundos...")
                time.sleep(60)
            except Exception as e:
                print(f"  [Erro] Falha na API: {e}")
                return 0

    total_prs = do_search(query_total)
    time.sleep(2) # Pausa leve para não sobrecarregar a API
    merged_prs = do_search(query_merged)
    
    acceptance_rate = (merged_prs / total_prs) * 100 if total_prs > 0 else 0
    return acceptance_rate

def main():
    saude_data = []
    top5_data = []
    horas_data = []

    print("A iniciar a extração de métricas locais...")
    for repo_local, repo_remote in REPOS.items():
        clone_or_fetch(repo_local, repo_remote)
        
        for period_name, (start_date, end_date) in PERIODS.items():
            print(f"A analisar {repo_local} ({period_name})...")
            
            cont_act, bus_fact, top_files, hours = extract_git_metrics(repo_local, start_date, end_date)
            acc_rate = extract_github_metrics(repo_remote, start_date, end_date)
            
            saude_data.append({
                "Repositorio": repo_local,
                "Periodo": period_name,
                "Atividade_Continua_Pct": cont_act,
                "Commits_por_Autor": bus_fact,
                "Taxa_Aceitacao_PRs": acc_rate
            })
            
            for file_name, count in top_files:
                top5_data.append({
                    "Repositorio": repo_local,
                    "Periodo": period_name,
                    "Arquivo": file_name,
                    "Commits": count
                })
                
            for hour, count in hours.items():
                horas_data.append({
                    "Repositorio": repo_local,
                    "Periodo": period_name,
                    "Hora": int(hour),
                    "Commits": count
                })
    
    print("A guardar os ficheiros CSV...")
    with open('metricas_saude_menores.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Repositorio", "Periodo", "Atividade_Continua_Pct", "Commits_por_Autor", "Taxa_Aceitacao_PRs"])
        writer.writeheader()
        writer.writerows(saude_data)

    with open('arquivos_top5_menores.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Repositorio", "Periodo", "Arquivo", "Commits"])
        writer.writeheader()
        writer.writerows(top5_data)

    with open('horas_commits_menores.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Repositorio", "Periodo", "Hora", "Commits"])
        writer.writeheader()
        writer.writerows(horas_data)
        
    print("Concluído! Ficheiros CSV gerados com sucesso.")

if __name__ == "__main__":
    main()
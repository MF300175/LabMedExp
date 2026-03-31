import pandas as pd
import os

def summarize_ck_metrics(class_csv, method_csv):
    # Lê os arquivos de métricas CK
    df_class = pd.read_csv(class_csv)
    df_method = pd.read_csv(method_csv)

    # Extrai o campo name_with_owner do caminho do arquivo (ex: GrowingGit/GitHub-Chinese-Top-Charts)
    def extract_name_with_owner(path):
        # Espera-se que o caminho contenha o padrão .../owner__repo/...
        try:
            parts = path.split('/')
            for p in parts:
                if '__' in p:
                    owner_repo = p.split('__')
                    if len(owner_repo) == 2:
                        return f"{owner_repo[0]}/{owner_repo[1]}"
            return 'unknown/unknown'
        except Exception:
            return 'unknown/unknown'

    df_class['name_with_owner'] = df_class['file'].apply(extract_name_with_owner)
    df_method['name_with_owner'] = df_method['file'].apply(extract_name_with_owner)

    # Sumariza métricas de qualidade por repositório (média, mediana, desvio padrão)
    metrics = ['cbo', 'dit', 'lcom', 'loc']
    summary = df_class.groupby('name_with_owner')[metrics].agg(['mean', 'median', 'std']).reset_index()
    summary.columns = ['name_with_owner'] + [f'{m}_{stat}' for m in metrics for stat in ['mean','median','std']]
    return summary

def merge_with_process_metrics(summary_df, process_metrics_csv):
    # Lê as métricas de processo (popularidade, releases, idade, loc, comentários)
    df_proc = pd.read_csv(process_metrics_csv)
    # Faz o merge usando 'name_with_owner' como chave
    merged = pd.merge(summary_df, df_proc, on='name_with_owner', how='left')
    return merged

if __name__ == '__main__':
    # Caminhos dos arquivos
    class_csv = os.path.join('data', 'ck_output', 'class.csv')
    method_csv = os.path.join('data', 'ck_output', 'method.csv')
    process_metrics_csv = os.path.join('..', 'Lab-02S01', 'data', 'repos_1000.csv')

    # Sumariza métricas CK
    summary = summarize_ck_metrics(class_csv, method_csv)
    summary.to_csv('summary_ck_metrics_by_repo.csv', index=False)
    print('Sumário de métricas CK salvo em summary_ck_metrics_by_repo.csv')

    # Cruzamento com métricas de processo
    merged = merge_with_process_metrics(summary, process_metrics_csv)
    merged.to_csv('merged_ck_process_metrics.csv', index=False)
    print('Dados cruzados salvos em merged_ck_process_metrics.csv')

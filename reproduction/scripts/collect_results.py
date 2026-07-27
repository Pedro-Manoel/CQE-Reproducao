"""Consolida os CSVs de avaliacao em tabelas Markdown reproduzido-vs-publicado
(Tabelas 3, 4, 5 e 6 do artigo CQE). Marca |dF1| > 2.

Uso:
  python collect_results.py            # imprime no stdout
  python collect_results.py > out.md
"""
import os
import sys
import json

import pandas as pd

HERE = os.path.dirname(__file__)
sys.path.insert(0, HERE)
from published_numbers import PUBLISHED

EVAL_OUT = os.path.abspath(os.path.join(HERE, "..", "..", "CQE_Evaluation",
                                        "data", "evaluation_output"))
RESULTS = os.path.abspath(os.path.join(HERE, "..", "results"))

# nome interno do harness -> nome no artigo
NAMES = {
    "CQE-Numparser": "CQE",
    "quantulum3": "Q3",
    "text-recognizer": "R-Txt",
    "ccg_nlp": "IllQ",
    "GPT3": "GPT-3",
}
ORDER = ["CQE-Numparser", "quantulum3", "ccg_nlp", "text-recognizer", "GPT3"]


def load_csv(dataset):
    path = os.path.join(EVAL_OUT, f"{dataset}.csv")
    if not os.path.exists(path):
        return None
    return pd.read_csv(path, sep="\t")


def cell(df, model, typ):
    """(P,R,F1) reproduzido para (model,type) ou None."""
    if df is None:
        return None
    sub = df[(df.model == model) & (df.type == typ)]
    if sub.empty:
        return None
    r = sub.iloc[0]
    return (round(r.P, 1), round(r.R, 1), round(r.F1, 1))


def fmt_row(model, typ, df, dataset):
    rep = cell(df, model, typ)
    pub = PUBLISHED.get(dataset, {}).get(model, {}).get(typ)
    name = NAMES.get(model, model)
    if rep is None:
        rep_s, d_s = "-", "-"
    else:
        rep_s = f"{rep[0]}/{rep[1]}/{rep[2]}"
    if pub is None:
        pub_s = "-"
    else:
        pub_s = f"{pub[0]}/{pub[1]}/{pub[2]}"
    if rep is not None and pub is not None:
        d = round(rep[2] - pub[2], 1)
        d_s = f"{d:+.1f}" + ("  ⚠️" if abs(d) > 2 else "")
    else:
        d_s = "-"
    return f"| {name} | {rep_s} | {pub_s} | {d_s} |"


def table(title, dataset, types):
    df = load_csv(dataset)
    print(f"\n### {title}\n")
    print("| Modelo | Reproduzido P/R/F1 | Publicado P/R/F1 | ΔF1 |")
    print("|---|---|---|---|")
    for typ in types:
        print(f"| **{typ}** | | | |")
        for model in ORDER:
            # so imprime se ha publicado ou reproduzido para o par
            pub = PUBLISHED.get(dataset, {}).get(model, {}).get(typ)
            rep = cell(df, model, typ)
            if pub is None and rep is None:
                continue
            print(fmt_row(model, typ, df, dataset))


def disambiguation():
    path = os.path.join(RESULTS, "disambiguation_results.json")
    print("\n### Tabela 6 — Desambiguação de unidades (micro P/R/F1)\n")
    if not os.path.exists(path):
        print("_(pendente — Fase 4)_")
        return
    data = json.load(open(path))
    print("| Modelo | Reproduzido P/R/F1 | Publicado P/R/F1 | ΔF1 |")
    print("|---|---|---|---|")
    for key, label in [("CQE", "CQE"), ("quantulum3", "Q3")]:
        rep = data.get(key)
        pub = PUBLISHED["disambiguation"].get(key)
        rep_s = "/".join(f"{x:.1f}" for x in rep) if rep else "-"
        pub_s = "/".join(f"{x:.1f}" for x in pub) if pub else "-"
        d_s = f"{rep[2]-pub[2]:+.1f}" if (rep and pub) else "-"
        print(f"| {label} | {rep_s} | {pub_s} | {d_s} |")


if __name__ == "__main__":
    print("# CQE — Reproduzido vs. Publicado\n")
    print("ΔF1 = F1_reproduzido − F1_publicado. ⚠️ marca |ΔF1| > 2.")
    table("Tabela 3 — NewsQuant (Value, Unit, Change)", "NewsQuant",
          ["value", "value+unit", "value+change"])
    table("Tabela 5 — NewsQuant (Concept)", "NewsQuant",
          ["value+concept_partial", "value+concept_compelete"])
    for ds, ttl in [("currency-model", "currency"), ("dimension-model", "dimension"),
                    ("temperature-model", "temperature"), ("age-model", "age")]:
        table(f"Tabela 4 — {ttl}", ds, ["value", "value+unit"])
    disambiguation()

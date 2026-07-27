"""Fase 3: roda o Illinois Quantifier (Java/CogComp) sobre as sentencas de cada
dataset e salva os 'labels' por sentenca em reproduction/results/illq_<ds>.json.

Estrategia: o servidor remoto do ccg_nlpy esta morto (confirmado). Em vez dele,
rodamos o jar standalone illinois-quantifier-4.0.12 (env conda cqe-illq, Java 8)
via reproduction/illq/RunIllQ.java, que usa getSpans(text, true, null) e produz
labels no MESMO formato '[<change> <value> <unit>]' que o tagger.py espera.

Roda no env cqe-eval (Python), invocando o java do env cqe-illq por caminho.
"""
import os
import sys
import json
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
ILLQ = os.path.join(REPO, "reproduction", "illq")
RESULTS = os.path.join(REPO, "reproduction", "results")
DATA = os.path.join(REPO, "CQE_Evaluation", "data", "formatted_test_set")
JAVA = os.path.expanduser("~/miniconda3/envs/cqe-illq/bin/java")

DATASETS = ["NewsQuant", "currency-model", "dimension-model",
            "temperature-model", "age-model"]


def run_dataset(name):
    rows = json.load(open(os.path.join(DATA, f"{name}.json"), encoding="utf-8"))
    texts = [d["text"] for d in rows]
    # uma sentenca por linha (sem newlines internos nesses datasets)
    infile = os.path.join(RESULTS, f"illq_input_{name}.txt")
    with open(infile, "w", encoding="utf-8") as f:
        for t in texts:
            f.write(t.replace("\n", " ").replace("\r", " ") + "\n")

    cp = f"{ILLQ}/target/dependency/*:{ILLQ}/target/classes"
    proc = subprocess.run([JAVA, "-Xmx4g", "-cp", cp, "RunIllQ", infile],
                          capture_output=True, text=True, encoding="utf-8")
    out = proc.stdout or ""

    # parse: blocos ===LINE=== <texto> seguidos de SPAN\t...\t<label>
    labels_by_text = {}
    cur = None
    for raw in out.splitlines():
        if raw == "===LINE===":
            cur = None
        elif cur is None and raw not in ("===END===",):
            cur = raw
            labels_by_text.setdefault(cur, [])
        elif raw.startswith("SPAN\t") and cur is not None:
            parts = raw.split("\t")
            if len(parts) >= 5:
                labels_by_text[cur].append(parts[4])  # o label '[= v unit]'
    # garante entrada p/ toda sentenca (mesmo sem spans)
    for t in texts:
        labels_by_text.setdefault(t, [])

    outpath = os.path.join(RESULTS, f"illq_{name}.json")
    json.dump(labels_by_text, open(outpath, "w", encoding="utf-8"), ensure_ascii=False)
    n_spans = sum(len(v) for v in labels_by_text.values())
    n_sent_with = sum(1 for v in labels_by_text.values() if v)
    print(f"{name:18} sent={len(texts):4d} sent_with_q={n_sent_with:4d} spans={n_spans:5d} -> {os.path.basename(outpath)}")
    if proc.returncode != 0:
        print("  [java stderr tail]", (proc.stderr or "")[-300:])


if __name__ == "__main__":
    targets = sys.argv[1:] or DATASETS
    for name in targets:
        run_dataset(name)
    print("DONE quantifier")

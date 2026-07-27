"""Fase 4b: retreina do zero os 18 classificadores de desambiguacao
(spacy.TextCatBOW.v1), reproduzindo o pipeline do CQE.

Difere do train_classifier_bert.py original em (documentado):
  - corrige o bug do '+' unario (linha 94) reescrevendo a geracao de DocBin;
  - usa o tokenizer do en_core_web_sm em vez do en_core_web_trf (o classificador
    e bag-of-words; os tokens sao identicos, evitando o download/risco do trf);
  - le os dados do clone CQE_Evaluation/data/units/train;
  - escreve os modelos com os nomes EXATOS que o unit_disambiguator carrega.

Saidas (WSL local, fora do /mnt/c por velocidade):
  ~/cqe_retrain/spacy_train/*.spacy        (DocBins)
  ~/cqe_retrain/unit_models/train_*.spacy  (18 modelos)
"""
import os
import sys
import glob
import json
import subprocess

sys.argv = [sys.argv[0]]  # guarda contra argparse de CQE.CQE em imports

import spacy
from spacy.tokens import DocBin

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
TRAIN_DIR = os.path.join(REPO, "CQE_Evaluation", "data", "units", "train")
CONFIG = os.path.join(REPO, "reproduction", "results", "config.cfg")
WORK = os.path.expanduser("~/cqe_retrain")
DOCBIN_DIR = os.path.join(WORK, "spacy_train")
MODELS_DIR = os.path.join(WORK, "unit_models")

ambigious_units = {
    'c': ['cent', 'celsius'], '¥': ['chinese yuan', 'japanese yen'],
    'kn': ['croatian kuna', 'knot'], 'p': ['point', 'penny'],
    'R': ['south african rand', 'roentgen'], 'b': ['barn', 'bit'],
    "'": ['foot', 'minute'], '′': ['foot', 'minute'], '"': ['inch', 'second'],
    '″': ['inch', 'second'], 'C': ['celsius', 'coulomb'], 'F': ['fahrenheit', 'farad'],
    'kt': ['kiloton', 'knot'], 'B': ['byte', 'bel'], 'P': ['poise', 'pixel'],
    'dram': ['armenian dram', 'dram'], 'pound': ['pound sterling', 'pound-mass'],
    'a': ['acre', 'year'],
}

# nome do modelo conforme unit_disambiguator.py carrega
def model_name(key):
    if key in ("C", "B", "P"):
        return f"train_BIG{key}"
    return {"¥": "train_yen", "′": "train_ascii'",
            "″": "train_ascii_doublequote", '"': "train_doublequote"}.get(
                key, f"train_{key}")

# slug ASCII seguro para o nome do arquivo DocBin
_SLUG = {"¥": "yen", "′": "prime", "″": "dprime", '"': "dquote", "'": "squote"}
def docbin_file(key):
    base = ("BIG" + key) if key in ("C", "B", "P") else _SLUG.get(key, key)
    return os.path.join(DOCBIN_DIR, f"train_set_{base}.spacy")


def load_rows(units):
    rows = []
    for f in glob.glob(os.path.join(TRAIN_DIR, "*.json")):
        for line in json.load(open(f, encoding="utf-8")):
            if line["unit"] in units:
                rows.append((line["text"], line["unit"]))
    return rows


def main():
    os.makedirs(DOCBIN_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)
    nlp = spacy.load("en_core_web_sm")  # so o tokenizer importa p/ BOW

    print("=== Gerando DocBins ===")
    for key, units in ambigious_units.items():
        rows = load_rows(units)
        db = DocBin()
        for text, label in rows:
            doc = nlp.make_doc(text)
            for u in units:
                doc.cats[u] = 1.0 if u == label else 0.0
            db.add(doc)
        db.to_disk(docbin_file(key))
        print(f"  {key!r:6} -> {os.path.basename(docbin_file(key)):22} ({len(rows)} amostras)")

    print("\n=== Treinando 18 classificadores TextCatBOW (seed=0) ===")
    for key in ambigious_units:
        out = os.path.join(MODELS_DIR, model_name(key) + ".spacy")
        train = docbin_file(key)
        cmd = [sys.executable, "-m", "spacy", "train", CONFIG,
               "--output", out, "--paths.train", train, "--paths.dev", train,
               "--system.seed", "0"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        ok = "OK" if r.returncode == 0 else "FALHOU"
        print(f"  {key!r:6} -> {os.path.basename(out):28} [{ok}]")
        if r.returncode != 0:
            print(r.stderr[-800:])
    print("\nDONE retrain")


if __name__ == "__main__":
    main()

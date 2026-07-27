"""Avalia os classificadores RETREINADOS (4b) no test set de desambiguacao,
apontando o unit_disambiguator para ~/cqe_retrain/unit_models via monkeypatch
de get_project_root. Replica a logica do CQE-side de test_unit_classifier.py
(disambiguator instanciado uma vez = resultado identico, so mais rapido)."""
import os
import sys
import json
from pathlib import Path

sys.argv = [sys.argv[0]]

import CQE.unit_classifier.unit_disambiguator as ud

# aponta para os modelos retreinados
_RETRAIN = Path(os.path.expanduser("~/cqe_retrain"))
ud.get_project_root = lambda: _RETRAIN

from sklearn.metrics import f1_score, classification_report

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
TEST = os.path.join(REPO, "CQE_Evaluation", "data", "units", "test",
                    "sentences_test.json")


def main():
    rows = json.load(open(TEST, encoding="utf-8"))
    target_names = list(frozenset(r["unit"] for r in rows))
    tn = {name: i for i, name in enumerate(target_names)}

    dis = ud.unit_disambiguator()  # carrega os 18 modelos retreinados uma vez
    gt, preds = [], []
    for r in rows:
        gt.append(tn[r["unit"]])
        pred = dis.disambiguate(r["text"], r["surface_form"])
        preds.append(tn[pred])

    print("CQE retrained micro-F1:", round(f1_score(gt, preds, average="micro") * 100, 2))
    labels = list(tn.values())
    names = list(tn.keys())
    rep = classification_report(gt, preds, labels=labels, target_names=names,
                                zero_division=0, digits=4)
    print(rep)


if __name__ == "__main__":
    main()

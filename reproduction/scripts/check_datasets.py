"""Valida as contagens de sentencas/quantidades dos datasets do CQE_Evaluation
contra a Tabela 2 do artigo, confirmando que os dados de entrada sao os mesmos."""
import json
import glob
import os

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "CQE_Evaluation",
                    "data", "formatted_test_set")

# Tabela 2 do artigo (sent / quantity) — age/temperature/etc do repo R-Txt.
PAPER = {
    "NewsQuant": (590, 904),
    "currency-model": (180, 255),
    "dimension-model": (93, 121),
    "temperature-model": (36, 34),
    "age-model": (19, 22),
}

print(f"{'dataset':22s} {'sent':>5s} {'quant':>6s} {'with_q':>7s} {'no_q':>5s}   "
      f"{'paper_sent':>10s} {'paper_q':>8s}")
for path in sorted(glob.glob(os.path.join(BASE, "*.json"))):
    name = os.path.splitext(os.path.basename(path))[0]
    data = json.load(open(path, encoding="utf-8"))
    n_sent = len(data)
    n_q = sum(len(d.get("quantities", [])) for d in data)
    n_with = sum(1 for d in data if d.get("quantities"))
    ps, pq = PAPER.get(name, ("-", "-"))
    print(f"{name:22s} {n_sent:5d} {n_q:6d} {n_with:7d} {n_sent-n_with:5d}   "
          f"{ps:>10} {pq:>8}")

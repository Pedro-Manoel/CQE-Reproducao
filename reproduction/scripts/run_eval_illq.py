"""Fase 3: roda a avaliacao completa COM o IllQ injetado (IllQFileTagger lendo
os labels pre-computados do Quantifier Java) substituindo o CCG_NILPTagger
(servidor remoto morto). Regenera os 5 CSVs com a linha ccg_nlp preenchida.

Mantem os mesmos guards documentados do run_eval_all.py."""
import os
import sys

sys.argv = [sys.argv[0]]  # guarda contra argparse de CQE.CQE

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
EVAL = os.path.join(REPO, "CQE_Evaluation")
RESULTS = os.path.join(REPO, "reproduction", "results")
sys.path.insert(0, EVAL)
sys.path.insert(0, HERE)
os.chdir(EVAL)

import evaluate_models as em
from illq_tagger import IllQFileTagger

# guards identicos ao run_eval_all
_of = em.get_fscores
em.get_fscores = lambda tp, g, m: (0.0, 0.0, 0.0) if (not m or not g) else _of(tp, g, m)
_om = em.calculate_metrics
em.calculate_metrics = lambda tr, system_name, attribute_list=("value", "unit"), debug=True: \
    _om(tr, system_name, attribute_list=list(attribute_list), debug=False)
import tagger as _tg
_ogpt = _tg.GPT3Tagger.tag
_tg.GPT3Tagger.tag = lambda self, text: (_ogpt(self, text) or [])

DATASETS = ["NewsQuant", "currency-model", "dimension-model",
            "temperature-model", "age-model"]
gpt_folder = "./data/gpt_3_output/"
output_folder = "./data/evaluation_output"
datasets = sys.argv[1:] or DATASETS  # sys.argv ja foi limpo; usa todos

for name in DATASETS:
    illq_json = os.path.join(RESULTS, f"illq_{name}.json")
    # injeta IllQFileTagger ligado ao json deste dataset
    em.CCG_NILPTagger = (lambda p: (lambda: IllQFileTagger(p)))(illq_json)
    test_file = f"data/formatted_test_set/{name}.json"
    print(f"\n===== {name} (IllQ injetado) =====", flush=True)
    em.evaluate(test_file, gpt_folder, output_folder)

print("\nDONE eval+illq")

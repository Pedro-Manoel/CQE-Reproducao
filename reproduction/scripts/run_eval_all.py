"""Roda o evaluate() do CQE_Evaluation/evaluate_models.py sobre um ou mais
datasets, sem editar o harness oficial. Todos os ajustes sao monkeypatches
locais e documentados:

  1. get_fscores: guarda divisao-por-zero (IllQ morto / parser vazio -> 0/0/0
     em vez de ZeroDivisionError).
  2. calculate_metrics: forca debug=False (o harness imprime por sentenca).
  3. CCG_NILPTagger: por padrao substituido por um stub sem rede (o IllQ real
     e injetado na Fase 3 via run_eval_illq.py). Defina CQE_SKIP_ILLQ=0 para
     usar o CCG_NILPTagger original (servidor remoto).

Uso:
  python run_eval_all.py                 # roda os 5 datasets
  python run_eval_all.py NewsQuant       # roda apenas um
"""
import os
import sys

# CQE/CQE.py chama argparse.parse_args() no import -> precisamos capturar nossos
# args e limpar sys.argv ANTES de importar evaluate_models (que importa CQE).
_ALL = ["NewsQuant", "currency-model", "dimension-model",
        "temperature-model", "age-model"]
_datasets = sys.argv[1:]
sys.argv = [sys.argv[0]]

EVAL = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..",
                                    "CQE_Evaluation"))
sys.path.insert(0, EVAL)
os.chdir(EVAL)

import evaluate_models as em

# 1) guarda divisao-por-zero
_orig_fscores = em.get_fscores
def _safe_fscores(tp, total_gt, total_model):
    if not total_model or not total_gt:
        return (0.0, 0.0, 0.0)
    return _orig_fscores(tp, total_gt, total_model)
em.get_fscores = _safe_fscores

# 2) silencia debug por sentenca
_orig_metrics = em.calculate_metrics
def _quiet_metrics(tagging_results, system_name, attribute_list=("value", "unit"),
                   debug=True):
    return _orig_metrics(tagging_results, system_name,
                         attribute_list=list(attribute_list), debug=False)
em.calculate_metrics = _quiet_metrics

# 3b) GPT3Tagger.tag retorna None quando o texto nao casa exatamente com o
# cache (1/590 sentencas no NewsQuant). Coage para [] (GPT-3 nao detectou nada).
import tagger as _tg
_orig_gpt_tag = _tg.GPT3Tagger.tag
def _safe_gpt_tag(self, text):
    r = _orig_gpt_tag(self, text)
    return r if r is not None else []
_tg.GPT3Tagger.tag = _safe_gpt_tag

# 3) stub do IllQ (sem rede) salvo se CQE_SKIP_ILLQ=0
if os.environ.get("CQE_SKIP_ILLQ", "1") == "1":
    class _StubIllQ:
        name = "ccg_nlp"
        def tag(self, text):
            return []
        def set_dataset_text_recongizer(self):
            pass
    em.CCG_NILPTagger = _StubIllQ
    print("[run_eval_all] IllQ desativado (stub). CQE_SKIP_ILLQ=0 para ativar.")

datasets = _datasets or _ALL

gpt_folder = "./data/gpt_3_output/"
output_folder = "./data/evaluation_output"
os.makedirs(output_folder, exist_ok=True)

for name in datasets:
    test_file = f"data/formatted_test_set/{name}.json"
    print(f"\n===== {name} =====", flush=True)
    em.evaluate(test_file, gpt_folder, output_folder)

print("\nDONE")

"""Fase 5: roda o teste de significancia por permutacao (Riezler & Maxwell 2005,
n=10000) que produz os marcadores dagger (p<0.01) do artigo, com o IllQ injetado
(IllQFileTagger) no lugar do CCG_NILPTagger (servidor morto) e o guard do GPT3.

Executa o permutation_significance_test.py oficial como __main__ via runpy,
apos aplicar os monkeypatches."""
import os
import sys
import runpy

sys.argv = ["permutation_significance_test.py"]  # guarda argparse de CQE.CQE

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
EVAL = os.path.join(REPO, "CQE_Evaluation")
SIG = os.path.join(EVAL, "significance_test")
RESULTS = os.path.join(REPO, "reproduction", "results")

sys.path.insert(0, HERE)    # illq_tagger
sys.path.insert(0, EVAL)    # tagger, evaluate_models
sys.path.insert(0, SIG)     # significance_testing_for_arrary_input
os.chdir(SIG)

from illq_tagger import IllQFileTagger  # importa antes de patchar (fixa a base)
import tagger
import evaluate_models as em

# injeta IllQ (significancia roda NewsQuant)
_illq_json = os.path.join(RESULTS, "illq_NewsQuant.json")
tagger.CCG_NILPTagger = lambda: IllQFileTagger(_illq_json)

# GPT3 None -> [] (1 sentenca sem match no cache)
_ogpt = tagger.GPT3Tagger.tag
tagger.GPT3Tagger.tag = lambda self, t: (_ogpt(self, t) or [])

# guard divisao-por-zero
_of = em.get_fscores
em.get_fscores = lambda tp, g, m: (0.0, 0.0, 0.0) if (not m or not g) else _of(tp, g, m)

runpy.run_path(os.path.join(SIG, "permutation_significance_test.py"),
               run_name="__main__")

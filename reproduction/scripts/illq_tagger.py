"""IllQFileTagger: substituto offline do CCG_NILPTagger do tagger.py.

Le os labels do Illinois Quantifier pre-computados (reproduction/results/
illq_<dataset>.json, gerados por run_quantifier.py) e aplica EXATAMENTE a
mesma logica de parsing/normalizacao do CCG_NILPTagger.tag() original
(tagger.py linhas 451-476), herdando o self.dictionary_unit e
set_dataset_text_recongizer. Assim o servidor remoto morto e contornado sem
mudar a semantica da avaliacao."""
import os
import sys
import json

_HERE = os.path.dirname(os.path.abspath(__file__))
_EVAL = os.path.abspath(os.path.join(_HERE, "..", "..", "CQE_Evaluation"))
if _EVAL not in sys.path:
    sys.path.insert(0, _EVAL)

import tagger as _tg


class IllQFileTagger(_tg.CCG_NILPTagger):
    def __init__(self, illq_json):
        # evita criar a RemotePipeline (rede) ao herdar o __init__ original
        _orig = _tg.remote_pipeline.RemotePipeline
        _tg.remote_pipeline.RemotePipeline = lambda *a, **k: None
        try:
            super().__init__()  # define self.dictionary_unit, self.name='ccg_nlp'
        finally:
            _tg.remote_pipeline.RemotePipeline = _orig
        with open(illq_json, encoding="utf-8") as f:
            self.labels_by_text = json.load(f)

    def tag(self, text):
        labels = self.labels_by_text.get(text)
        if not labels:
            return []
        results = []
        for ccg in labels:
            ccg = ccg.replace("]", "").replace("[", "")
            ccg = " ".join(ccg.split())
            ccg = ccg.replace("per cent", "percent")
            sv = ccg.split(" ")
            if len(sv) < 2:
                continue
            if not sv[1].startswith("Date") and "E-" not in sv[1]:
                if len(sv) > 2:
                    unit_norm = " ".join(sv[2:]).strip()
                    if unit_norm.endswith(" /"):
                        unit_norm = unit_norm[:-2]
                    if unit_norm.startswith("-"):
                        unit_norm = unit_norm[1:]
                    if unit_norm.endswith("s"):
                        unit_norm = unit_norm[:-1]
                    if unit_norm in self.dictionary_unit.keys():
                        unit_norm = self.dictionary_unit[unit_norm]
                else:
                    unit_norm = "-"
                changes = sv[0].strip()
                if changes == "+":
                    changes = "up"
                results.append({"value": sv[1].replace(",", "").strip(),
                                "normalized_unit": unit_norm, "change": changes})
        return results

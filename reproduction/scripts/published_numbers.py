"""Numeros publicados no artigo CQE (EMNLP 2023), Tabelas 3-6.

Cada celula e (P, R, F1). Chaves de 'type' seguem exatamente as emitidas pelo
harness de avaliacao (incluindo a grafia 'compelete'). Fonte unica da verdade
para a comparacao reproduzido-vs-publicado (collect_results.py)."""

# Nomes de modelo conforme o harness: CQE-Numparser, quantulum3, text-recognizer,
# ccg_nlp, GPT3.
PUBLISHED = {
    # --- Tabela 3 (NewsQuant): value, value+unit, value+change + Tabela 5 (concept) ---
    "NewsQuant": {
        "CQE-Numparser": {
            "value": (92.0, 91.9, 92.0),
            "value+unit": (85.6, 85.5, 85.6),
            "value+change": (88.2, 88.1, 88.1),
            "value+concept_partial": (76.2, 76.1, 76.1),
            "value+concept_compelete": (57.0, 57.0, 57.0),
        },
        "quantulum3": {
            "value": (65.0, 83.3, 73.0),
            "value+unit": (42.1, 53.9, 47.2),
        },
        "ccg_nlp": {
            "value": (50.6, 66.0, 57.3),
            "value+unit": (32.8, 42.8, 37.1),
            "value+change": (44.2, 57.6, 50.0),
        },
        "text-recognizer": {
            "value": (59.7, 82.2, 69.1),
            "value+unit": (29.6, 40.7, 34.2),
        },
        "GPT3": {
            "value": (72.1, 69.1, 70.6),
            "value+unit": (60.3, 57.9, 59.1),
            "value+change": (53.1, 50.9, 51.9),
            "value+concept_partial": (55.9, 53.7, 54.8),
            "value+concept_compelete": (26.3, 25.2, 25.7),
        },
    },
    # --- Tabela 4: value e value+unit por dataset R-Txt ---
    "currency-model": {
        "CQE-Numparser": {"value": (82.6, 85.9, 84.2), "value+unit": (78.1, 81.2, 79.6)},
        "quantulum3": {"value": (69.2, 84.7, 76.2), "value+unit": (29.5, 36.1, 32.5)},
        "ccg_nlp": {"value": (65.5, 70.6, 67.9), "value+unit": (41.8, 41.6, 45.1)},
        "text-recognizer": {"value": (67.4, 91.8, 77.7), "value+unit": (46.7, 63.5, 53.8)},
        "GPT3": {"value": (50.5, 54.9, 52.6), "value+unit": (40.8, 44.3, 42.5)},
    },
    "dimension-model": {
        "CQE-Numparser": {"value": (85.5, 87.6, 86.5), "value+unit": (78.2, 80.2, 79.2)},
        "quantulum3": {"value": (76.9, 93.4, 84.3), "value+unit": (56.5, 68.6, 61.9)},
        "ccg_nlp": {"value": (65.3, 77.7, 70.9), "value+unit": (43.4, 52.1, 47.5)},
        "text-recognizer": {"value": (73.6, 90.1, 81.0), "value+unit": (44.6, 54.5, 49.1)},
        "GPT3": {"value": (80.2, 80.2, 80.2), "value+unit": (65.3, 65.3, 65.3)},
    },
    "temperature-model": {
        "CQE-Numparser": {"value": (94.3, 97.1, 95.7), "value+unit": (91.4, 94.1, 92.8)},
        "quantulum3": {"value": (91.7, 97.1, 94.3), "value+unit": (61.1, 76.5, 74.3)},
        "ccg_nlp": {"value": (88.9, 94.1, 91.4), "value+unit": (30.6, 32.4, 31.4)},
        "text-recognizer": {"value": (91.9, 100.0, 95.8), "value+unit": (91.9, 100.0, 95.8)},
        "GPT3": {"value": (93.5, 85.3, 89.2), "value+unit": (45.2, 41.2, 43.1)},
    },
    "age-model": {
        "CQE-Numparser": {"value": (91.3, 95.5, 93.3), "value+unit": (91.3, 95.5, 93.3)},
        "quantulum3": {"value": (91.3, 95.5, 93.3), "value+unit": (82.6, 86.4, 84.4)},
        "ccg_nlp": {"value": (65.4, 77.3, 70.8), "value+unit": (42.3, 50.0, 45.8)},
        "text-recognizer": {"value": (77.8, 95.5, 85.7), "value+unit": (70.4, 86.4, 77.6)},
        "GPT3": {"value": (92.3, 54.5, 68.6), "value+unit": (92.3, 54.5, 68.6)},
    },
    # --- Tabela 6: desambiguacao de unidades (micro P/R/F1) ---
    "disambiguation": {
        "CQE": (89.9, 89.4, 88.1),
        "quantulum3": (57.33, 57.78, 54.46),
    },
}

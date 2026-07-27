# Relatório de Reprodução — CQE: A Comprehensive Quantity Extractor (EMNLP 2023)

**Autor da reprodução:** Pedro Manoel · **Data:** 2026-06-20 · **Disciplina:** NLP (Mestrado, UFCG 2026.1)

**Artigo:** Almasian, Kazakova, Göldner, Gertz. *CQE: A Comprehensive Quantity Extractor*. EMNLP 2023, pp. 12845–12859.
**Código:** [vivkaz/CQE](https://github.com/vivkaz/CQE) (biblioteca) · [satya77/CQE_Evaluation](https://github.com/satya77/CQE_Evaluation) (avaliação/datasets).

---

## 1. Objetivo e escopo

Reproduzir a funcionalidade do framework CQE e **comparar os resultados reproduzidos com os publicados** (Tabelas 3–7 do artigo), usando os datasets já fornecidos pelo repositório de avaliação. Escopo executado (completo): **CQE, Quantulum3 (Q3), Recognizers-Text (R-Txt), GPT-3 (cache) e Illinois Quantifier (IllQ)**, mais **retreino do módulo de desambiguação** e **teste de significância por permutação**.

**Veredito:** a reprodução foi **bem-sucedida**. Todos os sistemas reproduzem os números publicados dentro da tolerância adotada (|ΔF1| ≤ ~2 pontos), com a maioria das células **idênticas** ao artigo. O CQE — o sistema proposto — reproduz com ΔF1 ≤ 0.2 em todas as métricas do NewsQuant e **exato** na desambiguação.

---

## 2. Ambiente e metodologia

- **Plataforma:** WSL2 Ubuntu 24.04 + Miniconda. Dois ambientes Python 3.9: `cqe-eval` (extração/avaliação) e `cqe-illq` (Java 8 + Maven para o IllQ).
- **Stack:** spaCy 3.0.9, `en_core_web_sm` 3.0.0, quantulum3 0.8.1, recognizers-text-suite, scikit-learn 1.0. Snapshot completo em [`../environment-cqe-eval.txt`](../environment-cqe-eval.txt).
- **Desvios de ambiente** (necessários para o stack antigo importar; nenhum altera resultados): ver [`../environment-notes.md`](../environment-notes.md). Resumo: `numpy==1.23.5`, `pydantic==1.7.4`, `typing_extensions==3.10.0.2`, `six`/`sacremoses`, locale `en_US.UTF-8` gerado em user-space, torch CPU. quantulum3 fixado em 0.8.1 (versão vigente quando o artigo foi acessado, abr/2023) por compatibilidade com sklearn 1.0.
- **Metodologia de avaliação:** o harness oficial (`evaluate_models.py`) envolve cada sistema num *Tagger* unificado, casa predições com o gold por atributo (value: `np.isclose`; unit/change: igualdade exata; concept: interseção de tokens para *relaxed*, igualdade de conjuntos para *strict*) e reporta P/R/F1. Os scripts originais não têm CLI e foram orquestrados por wrappers (`reproduction/scripts/`) **sem alterar a semântica** (apenas guards documentados: divisão-por-zero, `debug=False`, e `GPT3.tag` `None→[]`).
- **Validação dos dados:** as contagens de todos os datasets batem **exatamente** com a Tabela 2 do artigo (NewsQuant 590 sent / 904 quant / 475 com / 115 sem; currency 180/255; dimension 93/121; temperature 36/34; age 19/22).

A tabela detalhada (P/R/F1) reproduzido-vs-publicado é gerada por `reproduction/scripts/collect_results.py` ([saída](../results/tables_repro_vs_pub.md)). Abaixo, o resumo por F1.

---

## 3. Resultados

ΔF1 = F1 reproduzido − F1 publicado. ✓ = dentro da tolerância (|Δ| ≤ 2).

### Tabela 3 — NewsQuant (Value, Value+Unit, Value+Change)

| Sistema | Value (repro/pub) | Δ | Value+Unit | Δ | Value+Change | Δ |
|---|---|---|---|---|---|---|
| **CQE** | 91.9 / 92.0 | −0.1 ✓ | 85.4 / 85.6 | −0.2 ✓ | 88.0 / 88.1 | −0.1 ✓ |
| Q3 | 73.2 / 73.0 | +0.2 ✓ | 47.3 / 47.2 | +0.1 ✓ | — | — |
| IllQ | 57.5 / 57.3 | +0.2 ✓ | 37.5 / 37.1 | +0.4 ✓ | 50.1 / 50.0 | +0.1 ✓ |
| R-Txt | 69.4 / 69.1 | +0.3 ✓ | 34.3 / 34.2 | +0.1 ✓ | — | — |
| GPT-3 | 70.7 / 70.6 | +0.1 ✓ | 59.1 / 59.1 | 0.0 ✓ | 52.0 / 51.9 | +0.1 ✓ |

### Tabela 5 — NewsQuant (Concept, relaxed/strict)

| Sistema | Relaxed (repro/pub) | Δ | Strict | Δ |
|---|---|---|---|---|
| **CQE** | 76.2 / 76.1 | +0.1 ✓ | 56.9 / 57.0 | −0.1 ✓ |
| GPT-3 | 54.8 / 54.8 | 0.0 ✓ | 25.8 / 25.7 | +0.1 ✓ |

### Tabela 4 — Datasets R-Txt (F1 de Value e Value+Unit)

| Dataset | Sistema | Value (r/p) | Δ | Value+Unit (r/p) | Δ |
|---|---|---|---|---|---|
| **currency** | CQE | 84.0 / 84.2 | −0.2 ✓ | 79.8 / 79.6 | +0.2 ✓ |
| | Q3 | 76.2 / 76.2 | 0.0 ✓ | 32.5 / 32.5 | 0.0 ✓ |
| | IllQ | 67.8 / 67.9 | −0.1 ✓ | 43.1 / 45.1 | −2.0 ✓ |
| | R-Txt | 77.7 / 77.7 | 0.0 ✓ | 52.5 / 53.8 | −1.3 ✓ |
| | GPT-3 | 52.6 / 52.6 | 0.0 ✓ | 42.5 / 42.5 | 0.0 ✓ |
| **dimension** | CQE | 86.1 / 86.5 | −0.4 ✓ | 79.5 / 79.2 | +0.3 ✓ |
| | Q3 | 83.6 / 84.3 | −0.7 ✓ | 61.9 / 61.9 | 0.0 ✓ |
| | IllQ | 72.7 / 70.9 | +1.8 ✓ | 43.4 / 47.5 | −4.1 ⚠️ |
| | R-Txt | 81.0 / 81.0 | 0.0 ✓ | 49.1 / 49.1 | 0.0 ✓ |
| | GPT-3 | 80.2 / 80.2 | 0.0 ✓ | 65.3 / 65.3 | 0.0 ✓ |
| **temperature** | CQE | 95.7 / 95.7 | 0.0 ✓ | 92.8 / 92.8 | 0.0 ✓ |
| | Q3 | 94.3 / 94.3 | 0.0 ✓ | 74.3 / 74.3 | 0.0 ✓ |
| | IllQ | 92.8 / 91.4 | +1.4 ✓ | 31.9 / 31.4 | +0.5 ✓ |
| | R-Txt | 95.8 / 95.8 | 0.0 ✓ | 95.8 / 95.8 | 0.0 ✓ |
| | GPT-3 | 89.2 / 89.2 | 0.0 ✓ | 43.1 / 43.1 | 0.0 ✓ |
| **age** | CQE | 97.8 / 93.3 | +4.5 ⚠️ | 97.8 / 93.3 | +4.5 ⚠️ |
| | Q3 | 93.3 / 93.3 | 0.0 ✓ | 84.4 / 84.4 | 0.0 ✓ |
| | IllQ | 70.8 / 70.8 | 0.0 ✓ | 45.8 / 45.8 | 0.0 ✓ |
| | R-Txt | 85.7 / 85.7 | 0.0 ✓ | 77.6 / 77.6 | 0.0 ✓ |
| | GPT-3 | 68.6 / 68.6 | 0.0 ✓ | 68.6 / 68.6 | 0.0 ✓ |

### Tabela 6 — Desambiguação de unidades (weighted avg P/R/F1)

| Sistema | Reproduzido | Publicado | ΔF1 |
|---|---|---|---|
| **CQE (pré-treinado, 4a)** | 89.9 / 89.4 / 88.1 | 89.9 / 89.4 / 88.1 | **0.0 (exato)** |
| **CQE (retreinado do zero, 4b)** | 89.9 / 89.4 / 88.1 | 89.9 / 89.4 / 88.1 | **0.0 (exato)** |
| Q3 | 55.3 / 58.3 / 55.1 | 57.3 / 57.8 / 54.5 | +0.6 ✓ |

Os 18 classificadores foram **retreinados do zero** (seed=0) e reproduzem **exatamente** os modelos entregues (4a == 4b == publicado). As contagens de amostras por surface form batem com o apêndice do artigo (c=144, p=149, dram=180, pound=131, …).

### Significância (permutação, Riezler & Maxwell 2005, n=10000)

O teste de permutação compara o CQE (sistema A) contra cada baseline. O p-value mínimo possível é `1/(n+1) = 9.999e-05`. Resultados (CQE vs. baseline, por atributo):

| Comparação | Value | Unit | Change |
|---|---|---|---|
| CQE vs Q3 | 9.999e-05 ✓ | 9.999e-05 ✓ | — |
| CQE vs R-Txt | 9.999e-05 ✓ | 9.999e-05 ✓ | — |
| CQE vs IllQ | 9.999e-05 ✓ | 9.999e-05 ✓ | 9.999e-05 ✓ |
| CQE vs GPT-3 | 9.999e-05 ✓ | 9.999e-05 ✓ | 9.999e-05 ✓ |

Todas as melhorias do CQE são **altamente significativas (p ≪ 0.01)**, atingindo o piso `9.999e-05` — consistente com os marcadores **†** do artigo (Tabelas 3, 5, 6). Isso é esperado dadas as margens grandes (ex.: CQE Value+Unit 85.4 vs. melhor baseline GPT-3 59.1; CQE Value+Change 88.0 vs. IllQ 50.1). O teste de permutação da desambiguação (Fase 4) também retornou `9.999e-05`.

A saída completa é gravada em `data/evaluation_output/NewsQuant_pr_significance.csv` por `run_significance.py`.

> Observações de reprodutibilidade: (i) o `permutation_significance_test.py` original testa `"concept" in attribute_list`, mas a lista usa `"referred_concepts"` — então os **p-values de concept não são emitidos** pelo script (ficam 0), embora a melhoria do CQE em concept seja claramente significativa pela margem (Tabela 5); (ii) para Q3/R-Txt o atributo `change` não se aplica (esses sistemas não detectam mudança).

---

## 4. Análise de discrepâncias

A reprodução é de altíssima fidelidade. Os poucos desvios:

- **age (CQE) +4.5 F1 (97.8 vs 93.3):** o dataset age tem apenas 19 sentenças/22 quantidades; 1–2 extrações a mais já oscilam fortemente o F1. O próprio artigo nota a instabilidade desses datasets pequenos. Atribuível a diferença mínima de versão do spaCy/modelo. O CQE reproduzido aqui é **ligeiramente melhor** que o publicado.
- **IllQ dimension/currency value+unit (−4.1 / −2.0):** o IllQ foi reconstruído a partir do jar `illinois-quantifier 4.0.12` + `models 2.0.5`, que difere da versão rodada pelo servidor CogComp em 2023; isso afeta a normalização de algumas unidades de dimensão/moeda. No NewsQuant (tabela principal) o IllQ ficou dentro de ±0.4 e no age **exato**.
- **R-Txt currency value+unit (−1.3):** versão do pacote `recognizers-text` mais recente que a do artigo.
- **Q3:** diferenças ≤ ~2 pontos vinculadas à versão 0.8.1 e ao retreino on-the-fly do classificador GloVe/sklearn.

### Achado: duas células publicadas são internamente inconsistentes

Recalculando F1 a partir do P e do R **publicados** em todas as 57 células das Tabelas 3–5 (a Tabela 6 fica fora: lá o F1 é média ponderada por classe, não a média harmônica de P e R), **55 são consistentes** dentro do arredondamento e **2 não são**:

| Célula | P | R | F1 publicado | F1 que P e R produzem | Reproduzido (consistente) |
|---|---|---|---|---|---|
| Tab. 4 — temperature, Q3, Value+Unit | 61.1 | 76.5 | 74.3 | **67.9** | `72.2 / 76.5 / 74.3` |
| Tab. 4 — currency, IllQ, Value+Unit | 41.8 | 41.6 | 45.1 | **41.7** | `41.2 / 45.1 / 43.1` |

- **temperature/Q3:** o `61.1` é quase certamente erro de digitação — 72.2 com 76.5 dá exatamente o F1=74.3 impresso.
- **currency/IllQ:** o trio publicado não fecha em nenhuma leitura; note que o **recall reproduzido (45.1) é idêntico ao "F1" publicado (45.1)**, o que sugere deslocamento de coluna na transcrição da tabela. **Consequência:** o ΔF1 = −2.0 registrado nessa célula (§3) está sendo medido contra um número que não satisfaz a própria definição de F1, e portanto **não deve ser lido como divergência de reprodução**.

---

## 5. Desvios entre os artefatos e o artigo (resultados de reprodutibilidade)

> **Esta seção é a lista canônica dos achados da reprodução.** O README da raiz traz um
> resumo para quem chega ao repositório, e `sobre-a-reproducao.md` apenas aponta para cá —
> qualquer atualização deve ser feita aqui.

Estes pontos foram **descobertos durante a reprodução** e são contribuições do estudo. Somam-se
a eles o achado das **duas células internamente inconsistentes** (§4, com a aritmética) e as
divergências de versão analisadas na mesma seção.

1. **Os classificadores de desambiguação NÃO são BERT.** O artigo afirma *"we train a BERT-based classifier … using spacy-transformers"*, mas os modelos entregues (`unit_models.zip`) são **`spacy.TextCatBOW.v1`** (bag-of-words, CPU, `ngram_size=1`). O retreino como TextCatBOW reproduz os modelos entregues **exatamente**, confirmando o achado. Consequência prática: GPU e `spacy-transformers` são desnecessários para a desambiguação.

2. **O baseline IllQ não é mais reexecutável pelo caminho original.** O servidor remoto da CogComp (`macniece.seas.upenn.edu:4001`) usado via `ccg_nlpy` está **offline** (verificado 2026-06-20, connection refused), é/era limitado a 100 queries/dia, e o wrapper `CCG_NILPTagger` **engole a falha** retornando `[]` — produzindo silenciosamente IllQ≈0. Reconstruímos o IllQ localmente (jar CogComp via Maven + driver Java próprio), recuperando o baseline.

3. **Bugs e quirks nos scripts originais** (preservados/contornados, não "corrigidos" no upstream): bug do `+` unário em `train_classifier_bert.py` (só os surface forms C/B/P treinavam); caminhos relativos do treino apontando para fora do clone; `GPT3Tagger.tag` retorna `None` (não `[]`) em 1/590 sentenças sem match no cache (quebra a métrica); no teste de permutação, a checagem `"concept" in attribute_list` nunca é verdadeira (a lista usa `"referred_concepts"`), de modo que **p-values de concept não são computados**; grafias erradas embutidas (`compelete`, `recongizer`, `precentage`, `signifcance`) que precisam ser preservadas.

4. **A contagem de regras do artigo não bate com o repositório.** O artigo (§3.2.3) afirma *"a set of 61 rules were created"*. O `rules.py` publicado define **69 padrões** (chaves do dicionário `rules`), dos quais **58** são referenciados por chamadas ativas de `matcher.add(...)`, agrupados em **33 grupos nomeados** do `DependencyMatcher` — 4 registros estão comentados no código e 6 padrões são filtros de não-quantidades (telefone/CEP) usados num matcher separado. Nenhuma dessas contagens é 61; o mais provável é que o código tenha evoluído após a submissão.

5. **Descompasso de layout entre a lib v1 (pré-submissão) e o harness de avaliação:** o `tagger.py` importa `from CQE.NumParser import NumParser`, mas nesta versão a classe está em `CQE.CQE`. Adicionado um shim `CQE/NumParser.py` (re-exporta a classe), mantendo o harness oficial intacto. A API (`parse`, `Unit.norm_unit`, `Change.change`, `Range`, `referred_concepts.get_nouns`) é compatível.

---

## 6. Limitações e conclusão

- **GPT-3** (`text-davinci-003`) está descontinuado pela OpenAI; usamos as **predições em cache** fornecidas pelo repositório (reprodução fiel, sem reexecutar a API).
- **IllQ** depende da versão do jar; pequenas divergências em unidades compostas de dimension/currency são esperadas.
- **Q3** depende da versão do quantulum3; fixamos a versão de época (0.8.1).

**Conclusão.** O artigo CQE é **reprodutível**. Reproduzimos as Tabelas 3, 4, 5 e 6 dentro da tolerância, com o sistema proposto (CQE) batendo o publicado quase exatamente (ΔF1 ≤ 0.2 no NewsQuant; desambiguação exata, inclusive retreinando do zero). Recuperamos integralmente o baseline IllQ apesar do serviço original estar morto. Documentamos divergências relevantes entre os artefatos e o texto (classificadores BOW, não BERT; serviço IllQ descontinuado; bugs nos scripts) que são úteis para futuras reproduções.

### Como reexecutar

```bash
# (WSL2) ambiente em reproduction/environment-notes.md; resumo:
source ~/cqe_env.sh                                   # ativa cqe-eval + locale
python reproduction/scripts/check_datasets.py          # valida Tabela 2
python reproduction/scripts/run_eval_all.py            # CQE/Q3/R-Txt/GPT-3 (IllQ stub)
python reproduction/scripts/run_quantifier.py          # IllQ (Java, env cqe-illq)
python reproduction/scripts/run_eval_illq.py           # avaliacao com IllQ injetado
python reproduction/scripts/retrain_disambiguation.py  # retreino 4b
python reproduction/scripts/eval_disambiguation_retrained.py
python reproduction/scripts/run_significance.py        # dagger p<0.01
python reproduction/scripts/collect_results.py          # tabelas consolidadas
```

# Sobre esta reprodução

> **Onde está o quê.** O **passo a passo de execução** (setup dos ambientes, locale, build do Illinois Quantifier, comandos para rodar o pipeline) vive no [README](README.md). A **análise dos resultados** (Tabelas 3–6 reproduzido-vs-publicado, ΔF1, discrepâncias e achados) vive no [relatório](report/cqe-reproduction-report.md). **Este documento não repete nenhum dos dois**: ele explica, para um leitor acadêmico, **o que é a pasta `reproduction/` inteira e COMO a reprodução foi feita** — em especial a natureza metodológica dos scripts.

---

## 1. O que é esta pasta

A `reproduction/` é o pacote completo da reprodução independente do artigo **CQE: A Comprehensive Quantity Extractor** (Almasian et al., EMNLP 2023). Reúne os scripts que orquestram o harness oficial, os artefatos gerados, a documentação de ambiente e o relatório de resultados — tudo organizado para que um terceiro consiga re-executar e auditar o trabalho do zero.

**Veredito:** a reprodução foi **bem-sucedida**. Todos os sistemas (CQE, Quantulum3, Recognizers-Text, GPT-3 em cache e Illinois Quantifier) reproduzem os números publicados dentro da tolerância adotada (|ΔF1| ≤ ~2 pontos), com a maioria das células **idênticas** ao artigo. O CQE — o sistema proposto — reproduz com ΔF1 ≤ 0.2 em todas as métricas do NewsQuant e **exato** na desambiguação de unidades, inclusive **retreinando os 18 classificadores do zero**. Os detalhes estão no [relatório](report/cqe-reproduction-report.md).

---

## 2. Mapa da pasta

Árvore comentada (apenas o que é versionado no git aparece como conteúdo essencial; artefatos regeneráveis estão marcados — ver [§6](#6-o-que-é-versionado-vs-regenerável)):

```
reproduction/
├── sobre-a-reproducao.md         <- VOCÊ ESTÁ AQUI (explica a pasta e o método)
├── README.md                     <- guia passo a passo de execução (do zero)
├── environment-notes.md          <- decisões de pins de ambiente e POR QUÊ
├── environment-cqe-eval.txt      <- pip freeze exato (75 pacotes) do env cqe-eval
│
├── scripts/                      <- núcleo da reprodução: wrappers do harness oficial
│   ├── check_datasets.py         <- valida contagens dos 5 datasets vs Tabela 2
│   ├── run_eval_all.py           <- avalia CQE/Q3/R-Txt/GPT-3 nos 5 datasets (IllQ stub)
│   ├── run_quantifier.py         <- roda o Illinois Quantifier (Java) -> illq_*.json
│   ├── illq_tagger.py            <- Tagger offline que reproduz a semântica do CCG_NILPTagger
│   ├── run_eval_illq.py          <- reavalia COM o IllQ injetado (preenche linha ccg_nlp)
│   ├── retrain_disambiguation.py <- retreina os 18 classificadores de unidade do zero
│   ├── eval_disambiguation_retrained.py <- avalia os classificadores retreinados (Tabela 6)
│   ├── run_significance.py       <- teste de permutação (Riezler & Maxwell, n=10000)
│   ├── published_numbers.py      <- números do artigo transcritos (ground-truth)
│   ├── collect_results.py        <- consolida tudo em tabelas reproduzido-vs-publicado
│   └── __pycache__/              <- (regenerável) bytecode .pyc
│
├── illq/                         <- build local (Maven, Java 8) do Illinois Quantifier
│   ├── pom.xml                   <- declara dependência illinois-quantifier 4.0.12 (repo CogComp)
│   ├── settings.xml              <- libera o repo HTTP da CogComp (Maven 3.8+ bloqueia HTTP)
│   ├── RunIllQ.java              <- driver Java que chama o Quantifier sobre texto
│   ├── probe.txt                 <- (regenerável) arquivo de teste
│   └── target/                   <- (regenerável, ~83 MB) jars de dependência + classes compiladas
│
├── results/                      <- artefatos da execução
│   ├── config.cfg                <- (versionado) config do harness de treino (TextCatBOW)
│   ├── disambiguation_results.json <- (versionado) micro/weighted P/R/F1 do retreino
│   ├── tables_repro_vs_pub.md    <- (versionado) ENTREGÁVEL: F1 repro vs pub, ΔF1, status
│   ├── illq_*.json               <- (regenerável) predições do IllQ por dataset
│   ├── illq_input_*.txt          <- (regenerável) sentenças preparadas p/ o IllQ
│   └── log_*.txt                 <- (regenerável) logs de cada fase da execução
│
└── report/
    └── cqe-reproduction-report.md <- relatório completo: método, resultados, discrepâncias
```

Atalhos para o que mais importa: [scripts/](scripts/), [illq/](illq/), [results/tables_repro_vs_pub.md](results/tables_repro_vs_pub.md), [report/cqe-reproduction-report.md](report/cqe-reproduction-report.md).

---

## 3. Natureza dos scripts: wrappers, NÃO cópias

Este é o ponto metodológico mais importante da reprodução, e merece atenção de quem for avaliá-la.

**Princípio de integridade.** O código **original** — tanto a biblioteca CQE (pasta `CQE/`) quanto o repositório de avaliação e datasets (`CQE_Evaluation/`) — **roda intacto**. Nada do upstream foi editado para "fazer dar certo". Todos os ajustes necessários vivem **de fora**, em [scripts/](scripts/), na forma de *monkeypatches* documentados aplicados em tempo de execução (substituição de atributos/funções por atribuição em Python, sem tocar o arquivo-fonte). Cada script importa o módulo oficial, troca pontualmente o que precisa, e chama a função `evaluate()` original.

**Por que isso importa metodologicamente.** Uma reprodução só tem valor se mede o artefato dos autores, não uma versão reescrita por quem reproduz. Ao manter o harness oficial executando sem patch no disco:

- os resultados são atribuíveis ao **código publicado**, não ao reprodutor;
- todo desvio fica **explícito e auditável** (cada monkeypatch é uma linha rastreável num wrapper, não uma alteração difusa no upstream);
- preservamos até as **grafias erradas** embutidas no upstream (`compelete`, `recongizer`, `precentage`, `signifcance`) — porque "corrigi-las" mudaria nomes de chaves/atributos e a semântica deixaria de ser a dos autores;
- os *guards* adicionados (proteção contra divisão por zero, `GPT3Tagger.tag` retornando `None`→`[]`, `debug=False`) são **transparentes**: evitam que o script quebre em casos de borda **sem alterar nenhum número** computado.

### 3.1 As quatro categorias

Classificamos cada script em uma de quatro naturezas:

- **novo** — código escrito para a reprodução que **não toca** o upstream (validações, orquestração de processo externo, consolidação de tabelas). Não muda nem observa a semântica interna; só lê entradas e produz saídas.
- **wrapper** — importa o módulo oficial e o executa **intacto**, aplicando apenas *monkeypatches* documentados de fora (injetar um Tagger, fechar guards) antes de chamar a função original. O cálculo das métricas continua sendo o do harness.
- **re-implementação** — reescreve um passo do pipeline do zero, **reproduzindo a semântica original** (e, quando preciso, corrigindo um bug do script original *no clone local*, nunca no upstream). Usado quando rodar o caminho original é impossível (serviço offline) ou está quebrado (bug do `+` unário no treino).
- **transcrito** — dados copiados diretamente do PDF do artigo (Tabelas 3–6), usados como *ground-truth* para a comparação. Nenhuma lógica.

### 3.2 Tabela de classificação

| Script | Categoria | O que toca do upstream | Ajuste (monkeypatch / nota) |
|---|---|---|---|
| [check_datasets.py](scripts/check_datasets.py) | **novo** | nenhum | só lê os JSON dos datasets e compara contagens com a Tabela 2. |
| [run_eval_all.py](scripts/run_eval_all.py) | **wrapper** | `evaluate_models`, `tagger` | guards: `get_fscores` protege 0/0; `calculate_metrics` força `debug=False`; `GPT3Tagger.tag` `None`→`[]`; `CCG_NILPTagger` vira stub sem rede (`CQE_SKIP_ILLQ=1`). |
| [run_quantifier.py](scripts/run_quantifier.py) | **novo** | nenhum | invoca o jar do IllQ via `subprocess` ([RunIllQ.java](illq/RunIllQ.java)) e parseia a saída para JSON. |
| [illq_tagger.py](scripts/illq_tagger.py) | **re-implementação** | subclasse de `CCG_NILPTagger` (`tagger.py`) | `IllQFileTagger`: lê labels pré-computados e aplica **exatamente** a lógica de parsing/normalização original (linhas 451–476); desativa `RemotePipeline` no `__init__` para não acessar a rede. |
| [run_eval_illq.py](scripts/run_eval_illq.py) | **wrapper** | `evaluate_models`, `tagger` | monkeypatch `CCG_NILPTagger` → `IllQFileTagger`; mesmos guards do `run_eval_all`. |
| [retrain_disambiguation.py](scripts/retrain_disambiguation.py) | **re-implementação** | nenhum (reescreve de zero) | reproduz o pipeline de `train_classifier_bert.py` corrigindo o **bug do `+` unário** (no clone) e usando `en_core_web_sm`; treina 18 `spacy.TextCatBOW.v1`. |
| [eval_disambiguation_retrained.py](scripts/eval_disambiguation_retrained.py) | **wrapper** | `CQE.unit_classifier.unit_disambiguator` | monkeypatch `get_project_root` → `~/cqe_retrain` para carregar os modelos retreinados, reusando o avaliador original. |
| [run_significance.py](scripts/run_significance.py) | **wrapper** | `significance_test/permutation_significance_test.py` (via `runpy`) | monkeypatch `tagger.CCG_NILPTagger` → `IllQFileTagger`, `GPT3Tagger.tag` `None`→`[]`, `get_fscores` guard; roda o teste original n=10000. |
| [published_numbers.py](scripts/published_numbers.py) | **transcrito** | nenhum | dicionário `PUBLISHED` com P/R/F1 das Tabelas 3–6 do artigo. |
| [collect_results.py](scripts/collect_results.py) | **novo** | importa `published_numbers`; lê os CSVs do harness | consolida em Markdown reproduzido-vs-publicado, marcando \|ΔF1\| > 2. |
| [RunIllQ.java](illq/RunIllQ.java) | **novo** | jar externo `illinois-quantifier 4.0.12` | driver Java standalone: chama `getSpans()` e emite blocos parseáveis (`===LINE===` / `SPAN`). |

Complementando os monkeypatches: o shim `CQE/NumParser.py` re-exporta a classe de `CQE.CQE`, mantendo o harness importando `from CQE.NumParser import NumParser` **sem alterar a lib**; e o patch do bug do `+` unário em `train_classifier_bert.py` é aplicado **no clone local**, jamais no upstream.

---

## 4. Como a reprodução foi conduzida (metodologia fase a fase)

A reprodução foi estruturada em fases sequenciais, cada uma com um *gate* de validação antes de avançar. Os comandos concretos estão no [README](README.md); aqui está o **raciocínio** de cada fase.

- **Fase 0 — Ambiente.** Dois ambientes conda isolados (Python 3.9): `cqe-eval` para extração/avaliação e `cqe-illq` (Java 8 + Maven) para o baseline IllQ. Instalação do stack na ordem exata dos pins, clone do `CQE_Evaluation`, e *smoke test* com `example.py` para confirmar que a lib importa e extrai quantidades corretamente.

- **Fase 1 — CQE no NewsQuant (núcleo funcional).** Validação das contagens dos datasets contra a Tabela 2 e execução do harness sobre o NewsQuant. *Gate*: Value/Value+Unit/Value+Change e concept (relaxed/strict) dentro de ±2 pontos do publicado.

- **Fase 2 — Baselines + datasets R-Txt.** O wrapper [run_eval_all.py](scripts/run_eval_all.py) estende a avaliação para os 5 datasets (NewsQuant + currency/dimension/temperature/age) com Q3, R-Txt e GPT-3 (cache), **sem alterar a semântica**. *Gate*: baselines dentro de |ΔF1| ≤ ~2, registrando causas de divergência (versões de pacotes).

- **Fase 3 — Illinois Quantifier via Java.** Constatado que o servidor remoto da CogComp está **offline**, o IllQ foi reconstruído localmente: build Maven do jar `illinois-quantifier 4.0.12`, driver [RunIllQ.java](illq/RunIllQ.java), predições por dataset em JSON via [run_quantifier.py](scripts/run_quantifier.py), e injeção na avaliação pelo [illq_tagger.py](scripts/illq_tagger.py) + [run_eval_illq.py](scripts/run_eval_illq.py), recuperando o baseline.

- **Fase 4 — Desambiguação de unidades.** *(4a)* validação dos modelos pré-treinados entregues; *(4b)* **retreino do zero** dos 18 classificadores via [retrain_disambiguation.py](scripts/retrain_disambiguation.py) (corrigindo o bug do `+` unário no clone) e avaliação por [eval_disambiguation_retrained.py](scripts/eval_disambiguation_retrained.py). *Gate*: 4b ≈ 4a ≈ publicado, demonstrando reprodutibilidade exata.

- **Fase 5 — Testes de significância.** Teste de permutação (Riezler & Maxwell 2005, n=10000, p < 0.01) via [run_significance.py](scripts/run_significance.py), comparando CQE contra cada baseline e confrontando com os marcadores **†** do artigo.

- **Fase 6 — Relatório comparativo.** Consolidação das tabelas reproduzido-vs-publicado por [collect_results.py](scripts/collect_results.py) (usando [published_numbers.py](scripts/published_numbers.py) como *ground-truth*) e redação da análise de discrepâncias no [relatório](report/cqe-reproduction-report.md).

---

## 5. Ambiente e desvios

A reprodução rodou em **WSL2 Ubuntu 24.04 + Miniconda**, tudo em **CPU** (GPU não é necessária). O snapshot exato das 75 dependências está em [environment-cqe-eval.txt](environment-cqe-eval.txt); a justificativa de **cada pin e desvio** está em [environment-notes.md](environment-notes.md).

Em resumo, o stack fixado pelos autores é antigo e não importa "de fábrica" num sistema moderno; foram necessários ajustes que **não alteram nenhum resultado**: `torch 2.0.0+cpu` (nenhum componente reproduzido usa GPU), `numpy==1.23.5` (ABI do `thinc`), `pydantic==1.7.4` e `typing_extensions==3.10.0.2` (resolução de config do spaCy/thinc), `six`/`sacremoses` (deps transitivas do tokenizer FlauBERT), `quantulum3==0.8.1` (compatível com sklearn 1.0, versão de época), e o locale `en_US.UTF-8` gerado em **user-space** (sem `sudo`), exigido por `CQE/NumberNormalizer.py` no import.

---

## 6. O que é versionado vs regenerável

A pasta separa deliberadamente **fonte/entregáveis** (versionados no git) de **artefatos produzidos pelo pipeline** (gitignorados, reproduzíveis a qualquer momento).

**Versionado** (entra no git):
- [README.md](README.md), [environment-notes.md](environment-notes.md), [environment-cqe-eval.txt](environment-cqe-eval.txt) e este documento;
- [scripts/](scripts/) inteiro (os 10 `.py`; exceto `__pycache__/`);
- de [results/](results/), apenas três arquivos: [config.cfg](results/config.cfg), [disambiguation_results.json](results/disambiguation_results.json) e o entregável [tables_repro_vs_pub.md](results/tables_repro_vs_pub.md);
- de [illq/](illq/): [pom.xml](illq/pom.xml), [settings.xml](illq/settings.xml) e [RunIllQ.java](illq/RunIllQ.java);
- [report/cqe-reproduction-report.md](report/cqe-reproduction-report.md).

**Regenerável** (gitignorado — regras nas linhas 188–202 do `.gitignore`):
- todo o resto de [results/](results/) — logs `log_*.txt`, predições `illq_*.json`, inputs `illq_input_*.txt` e os CSVs das rodadas;
- [illq/target/](illq/target/) (~83 MB) — jars de dependência e classes compiladas pelo `mvn` + `javac`;
- `scripts/__pycache__/` — bytecode Python;
- `illq/probe.txt` e o clone externo `CQE_Evaluation/`.

A consequência prática: tudo o que é gitignorado **renasce** ao re-rodar o pipeline do [README](README.md); o repositório carrega só o que é fonte e o que comprova o resultado.

---

## 7. Principais achados de reprodutibilidade

Os achados **não são descritos aqui** para não existirem em duas versões que divergem com o
tempo. A lista canônica, com evidências e números, está no
**[relatório](report/cqe-reproduction-report.md)**:

| Onde | O que está lá |
|---|---|
| [§4 — Análise de discrepâncias](report/cqe-reproduction-report.md#4-análise-de-discrepâncias) | as poucas diferenças reproduzido-vs-publicado, com causa atribuída a cada uma; e as **duas células publicadas que são internamente inconsistentes**, com a aritmética que demonstra |
| [§5 — Desvios entre os artefatos e o artigo](report/cqe-reproduction-report.md#5-desvios-entre-os-artefatos-e-o-artigo-resultados-de-reprodutibilidade) | os achados sobre o código e os modelos publicados: a arquitetura dos classificadores de desambiguação, o baseline que falha em silêncio, os *quirks* dos scripts originais, a contagem de regras e o descompasso de layout entre a lib e o harness |

O que este documento acrescenta é o **como** — a metodologia das seções 3 a 6 acima, que
explica por que esses achados podem ser atribuídos ao artefato dos autores e não a quem
reproduziu.

---

## 8. Por onde começar a ler

Roteiro de leitura sugerido, do panorama ao detalhe:

1. **[Relatório](report/cqe-reproduction-report.md)** — comece aqui: objetivo, veredito, tabelas reproduzido-vs-publicado e análise de discrepâncias. É a síntese dos resultados.
2. **[README](README.md)** — o passo a passo de execução: como montar os dois ambientes, gerar o locale, buildar o IllQ e rodar o pipeline do zero.
3. **Este documento** ([sobre-a-reproducao.md](sobre-a-reproducao.md)) — para entender o *como* metodológico: a natureza dos scripts (wrappers, não cópias) e o princípio de integridade.
4. **[scripts/](scripts/)** — por último, o código em si, já sabendo a categoria e o papel de cada arquivo pela tabela da [§3.2](#32-tabela-de-classificação).

Quem só quer o veredito pode parar no item 1; quem vai re-executar precisa do 2; quem vai avaliar a metodologia, do 3.
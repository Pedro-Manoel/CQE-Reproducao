# Reprodução do CQE — Guia passo a passo (máquina nova)

Este guia reproduz **do zero**, em uma máquina nova, os resultados do artigo
**CQE: A Comprehensive Quantity Extractor** (EMNLP 2023) — Tabelas 3, 4, 5 e 6 e o
teste de significância. É auto-contido: do clone até as tabelas comparativas
reproduzido-vs-publicado.

> O resultado e a análise estão em [`report/cqe-reproduction-report.md`](report/cqe-reproduction-report.md).
> As decisões de ambiente (pins e por quê) estão em [`environment-notes.md`](environment-notes.md).

---

## 0. Visão geral

A reprodução usa **dois ambientes conda** (Python 3.9):

| Ambiente | Para quê | Conteúdo |
|---|---|---|
| **`cqe-eval`** | extração + avaliação (CQE, Q3, R-Txt, GPT-3) + retreino + significância | stack Python (spaCy 3.0.9, …) |
| **`cqe-illq`** | baseline **Illinois Quantifier** | Java 8 + Maven (jar CogComp) |

O pipeline Python roda em `cqe-eval`; ele **chama o `java` do `cqe-illq` por caminho**
(o IllQ é pré-computado num passo separado e injetado na avaliação).

**Plataforma testada:** WSL2 Ubuntu 24.04. Funciona igual em **Linux nativo x86_64**
(num Linux com `sudo`, o passo do locale fica até mais simples — ver §3).
GPU **não** é necessária (tudo roda em CPU).

Tempo aproximado numa máquina comum: ~30–60 min (a maior parte é baixar dependências
e o jar do IllQ).

---

## 1. Pré-requisitos

- **conda/miniconda** instalado.
- **git**.
- Conexão de internet (baixa pacotes pip, o modelo spaCy e o jar do IllQ via Maven).
- ~3 GB de disco livre (o jar do IllQ + dependências dão ~1 GB).

> ⚠️ **Arquitetura:** os pins são antigos e têm wheels para **x86_64**. Em Linux **ARM**
> a instalação pode falhar (sem wheels para esses pins).

---

## 2. Clonar os dois repositórios

Este repositório é um **fork** da biblioteca CQE (pasta `CQE/`, intacta) acrescido da pasta
**`reproduction/`**. O repositório de **avaliação + datasets** (`CQE_Evaluation`) **não** está
versionado aqui (está no `.gitignore`) e precisa ser clonado para dentro da raiz, com
**exatamente** esse nome.

```bash
# 1) este repositório (lib CQE + reproduction/)
git clone https://github.com/Pedro-Manoel/CQE-Reproducao.git
cd CQE-Reproducao

# 2) o repo de avaliação/datasets, DENTRO da raiz, com o nome CQE_Evaluation/
git clone https://github.com/satya77/CQE_Evaluation.git CQE_Evaluation
```

Layout esperado depois disso:

```
CQE-Reproducao/           <- raiz deste repo
├── CQE/                  <- biblioteca (unit.json, rules.py, unit_models.zip, …)
├── CQE_Evaluation/       <- clonado no passo 2 (datasets, harness, cache GPT-3)
├── reproduction/         <- este guia, scripts, illq/, report/
├── setup.py
└── requirements.txt
```

> O nome `CQE_Evaluation/` é obrigatório: os scripts resolvem os caminhos dos datasets e do
> harness a partir dele.

> Os datasets já vêm prontos no `CQE_Evaluation/` (não precisam ser recriados),
> incluindo o **cache do GPT-3** em `CQE_Evaluation/data/gpt_3_output/`
> (`text-davinci-003` foi descontinuado; usamos as predições em cache).

---

## 3. Ambiente `cqe-eval` (Python) + locale

### 3.1 Criar o ambiente e instalar

```bash
conda create -y -n cqe-eval python=3.9
conda activate cqe-eval

# instala o snapshot exato (75 pacotes), MENOS a linha editável do próprio CQE
grep -v '^-e ' reproduction/environment-cqe-eval.txt > /tmp/req.txt
pip install --extra-index-url https://download.pytorch.org/whl/cpu -r /tmp/req.txt

# instala a lib CQE local (com o shim CQE/NumParser.py) sem mexer nos pins
pip install -e . --no-deps
```

> Por que assim: o `environment-cqe-eval.txt` tem `torch==2.0.0+cpu` (precisa do índice
> extra do PyTorch) e uma linha `-e git+…/CQE.git@<commit>` que apontaria para o GitHub —
> nós a removemos e instalamos a **cópia local** com `pip install -e . --no-deps`, que inclui
> o shim `CQE/NumParser.py` (o harness importa `from CQE.NumParser import NumParser`).

Confirme a sanidade das dependências:

```bash
pip check          # deve sair limpo
```

### 3.2 Locale `en_US.UTF-8`

`CQE/NumberNormalizer.py` faz `locale.setlocale(LC_ALL, 'en_US.UTF-8')` no import — então
esse locale precisa existir.

**Linux nativo (com sudo) — recomendado:**
```bash
sudo locale-gen en_US.UTF-8 || sudo localedef -i en_US -f UTF-8 en_US.UTF-8
```

**Sem sudo (foi o caso no WSL) — gerar em user-space:**
```bash
mkdir -p ~/.locale
localedef -i en_US -f UTF-8 ~/.locale/en_US.UTF-8
export LOCPATH=$HOME/.locale
```

### 3.3 Helper de ativação (opcional, mas recomendado)

Cria um `~/cqe_env.sh` que ativa o env e exporta o locale numa tacada:

```bash
cat > ~/cqe_env.sh <<'EOF'
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate cqe-eval
export LOCPATH=$HOME/.locale        # remova se gerou o locale com sudo
export LC_ALL=en_US.UTF-8
EOF
```

A partir daí, em cada sessão: `source ~/cqe_env.sh`.

### 3.4 Smoke test

```bash
python example.py
```
A saída deve bater com o README da lib (ex.: `(=,2.1,[%],percentage,[sp, 500])`, …).
Os modelos de desambiguação (`CQE/unit_models.zip`) são **descompactados automaticamente**
no primeiro uso do `NumParser` — não precisa baixar nada à parte.

---

## 4. Ambiente `cqe-illq` (Java) + build do Illinois Quantifier

O servidor remoto da CogComp usado originalmente está **offline**; reconstruímos o IllQ
localmente a partir do jar `illinois-quantifier 4.0.12` via Maven.

```bash
conda create -y -n cqe-illq -c conda-forge openjdk=8 maven
conda activate cqe-illq

cd reproduction/illq

# baixa o jar do IllQ + dependências (repo HTTP da CogComp liberado via settings.xml)
mvn -s settings.xml dependency:copy-dependencies      # -> target/dependency/*.jar

# compila o driver RunIllQ.java
mkdir -p target/classes
javac -cp "target/dependency/*" -d target/classes RunIllQ.java

cd ../..
```

> `settings.xml` tem um mirror `mirrorOf=cogcomp` apontando para `http://cogcomp.org/m2repo/`
> — necessário porque o Maven 3.8+ bloqueia repositórios HTTP por padrão.

Volte para o env de avaliação para rodar o pipeline:

```bash
conda activate cqe-eval     # ou: source ~/cqe_env.sh
```

> ⚠️ **Caminho do Java:** [`scripts/run_quantifier.py`](scripts/run_quantifier.py#L21) chama
> `~/miniconda3/envs/cqe-illq/bin/java`. Se seu conda **não** for `~/miniconda3` (ex.: `~/anaconda3`,
> conda do sistema) **ou** o env tiver outro nome, ajuste essa linha. Cheque o caminho com:
> `conda run -n cqe-illq which java`.

---

## 5. Rodar a reprodução

Tudo abaixo roda no env **`cqe-eval`**, a partir da **raiz do repo**. Cada script é um
wrapper que orquestra o harness oficial **sem alterar a semântica** (só guards documentados).

```bash
source ~/cqe_env.sh        # (ou: conda activate cqe-eval + export do locale)

# 5.1 valida os datasets contra a Tabela 2 do artigo
python reproduction/scripts/check_datasets.py

# 5.2 avaliação principal: CQE, Q3, R-Txt, GPT-3 (IllQ ainda em stub)
python reproduction/scripts/run_eval_all.py

# 5.3 IllQ: roda o Quantifier (Java) sobre os 5 datasets -> reproduction/results/illq_*.json
python reproduction/scripts/run_quantifier.py

# 5.4 reavalia os 5 sistemas COM o IllQ injetado (regenera os CSVs com a linha ccg_nlp)
python reproduction/scripts/run_eval_illq.py

# 5.5 desambiguação: retreina os 18 classificadores do zero (4b) e avalia
python reproduction/scripts/retrain_disambiguation.py
python reproduction/scripts/eval_disambiguation_retrained.py

# 5.6 teste de significância por permutação (marcadores † do artigo)
python reproduction/scripts/run_significance.py

# 5.7 consolida tudo em tabelas reproduzido-vs-publicado
python reproduction/scripts/collect_results.py > reproduction/results/tables_repro_vs_pub.md
```

### O que cada passo produz

| Passo | Saída | Onde |
|---|---|---|
| 5.1 | contagens sent/quant (deve bater com Tabela 2) | stdout |
| 5.2 / 5.4 | CSVs P/R/F1 por dataset | `CQE_Evaluation/data/evaluation_output/*.csv` |
| 5.3 | labels do IllQ por sentença | `reproduction/results/illq_*.json` |
| 5.5 | 18 modelos retreinados + micro-F1 | `~/cqe_retrain/unit_models/`, stdout |
| 5.6 | p-values do teste de permutação | `CQE_Evaluation/data/evaluation_output/NewsQuant_pr_significance.csv` |
| 5.7 | **tabelas comparativas** (o entregável) | `reproduction/results/tables_repro_vs_pub.md` |

> A pasta `reproduction/results/` (exceto `config.cfg`, `disambiguation_results.json` e
> `tables_repro_vs_pub.md`, que são versionados) é **regenerável** e está no `.gitignore`.

---

## 6. O que esperar (validação)

- **check_datasets:** NewsQuant 590/904, currency 180/255, dimension 93/121,
  temperature 36/34, age 19/22 (idêntico à Tabela 2).
- **CQE no NewsQuant:** Value/Value+Unit/Value+Change ≈ 91.9 / 85.4 / 88.0 (ΔF1 ≤ 0.2).
- **Desambiguação (Tabela 6):** micro P/R/F1 = **89.9 / 89.4 / 88.1** — o retreino 4b reproduz
  **exatamente** os modelos pré-treinados (4a) e o publicado.
- **Significância:** CQE vs. cada baseline atinge o piso `9.999e-05` (p ≪ 0.01) em value/unit/change.

Tolerância adotada: `|ΔF1| ≤ ~2`. As (poucas) discrepâncias esperadas estão explicadas
na §4 do [relatório](report/cqe-reproduction-report.md) (datasets pequenos como `age`;
versão do jar do IllQ; versão do `recognizers-text`).

---

## 7. Solução de problemas (gotchas conhecidos)

| Sintoma | Causa / correção |
|---|---|
| `unsupported locale setting` no import do CQE | locale `en_US.UTF-8` ausente — ver §3.2 (gere com sudo ou via `localedef` + `LOCPATH`). |
| `numpy.dtype size changed` / ABI do `thinc` | numpy errado — tem que ser `numpy==1.23.5` (já fixado no freeze). |
| `TypeError: issubclass() arg 1 must be a class` (spaCy) | `typing_extensions` 4.x — tem que ser `3.10.0.2` (já no freeze). Não é o pydantic. |
| `import transformers` falha (FlauBERT) | faltam `six`/`sacremoses` (já no freeze). |
| `ModuleNotFoundError: CQE.NumParser` | rode `pip install -e . --no-deps` na raiz (instala o shim `CQE/NumParser.py`). |
| `unrecognized arguments: NewsQuant` | `CQE/CQE.py` chama `argparse` no import; os wrappers já limpam `sys.argv` — use sempre os scripts de `reproduction/scripts/`, não o harness direto. |
| `quantulum3` quebra com `sklearn` (`log_loss`) | tem que ser `quantulum3==0.8.1` com `sklearn==1.0` (já no freeze). |
| IllQ sai vazio / `java: command not found` | env `cqe-illq` não buildado, ou caminho do `java` em `run_quantifier.py` aponta para outro lugar — ver §4. |
| Maven: `blocked mirror for repositories: ... HTTP` | use `mvn -s settings.xml …` (o `settings.xml` libera o repo HTTP da CogComp). |
| `ZeroDivisionError` na métrica de um sistema | já tratado pelos guards dos wrappers (sistema sem predições → 0/0/0). |

---

## 8. Notas sobre reprodutibilidade (achados do estudo)

Detalhes completos na §5 do [relatório](report/cqe-reproduction-report.md). Em resumo:

1. **Os classificadores de desambiguação NÃO são BERT** — são `spacy.TextCatBOW.v1`
   (bag-of-words, CPU). Por isso GPU/`spacy-transformers` são dispensáveis e o retreino
   do zero reproduz os modelos entregues exatamente.
2. **O IllQ não é mais reexecutável pelo caminho original** (servidor CogComp offline);
   por isso ele é reconstruído localmente em Java (§4).
3. **Quirks dos scripts originais** (bug do `+` no treino, `GPT3.tag→None`, `concept` vs
   `referred_concepts` no teste de significância) são contornados pelos wrappers, sem
   alterar a semântica da avaliação.
```

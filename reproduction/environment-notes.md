# Notas de Ambiente — Reprodução CQE

Ambiente: **WSL2 Ubuntu 24.04 + Miniconda, env `cqe-eval` (Python 3.9.25)**, GPU RTX 4070 Ti SUPER disponível (não utilizada — ver abaixo).

Snapshot completo de pacotes em [`environment-cqe-eval.txt`](environment-cqe-eval.txt) (`pip freeze`, 75 pacotes).

## Desvios em relação ao `requirements.txt` original (e por quê)

O stack fixado pelos autores (spacy 3.0.9, torch 2.0.0, spacy-transformers 1.0.4) é antigo e **não importa "de fábrica"** num sistema moderno. Os ajustes abaixo foram necessários para fazê-lo rodar; nenhum altera os resultados da extração/avaliação.

| Ajuste | Valor | Motivo |
|---|---|---|
| **torch** | `2.0.0+cpu` (em vez de cu118) | Nenhum componente reproduzido usa GPU: os classificadores de desambiguação são `spacy.TextCatBOW.v1` (CPU) e o parser usa `en_core_web_sm` (CPU). O build CPU é menor/rápido e dá resultados idênticos. |
| **numpy** | pin `1.23.5` | `numpy 2.0.2` (puxado por padrão) quebra a ABI compilada do `thinc 8.0.17` (`numpy.dtype size changed`). |
| **pydantic** | pin `1.7.4` | Versão exigida pelo spaCy 3.0.9 (`>=1.7.4,<1.8`). |
| **typing_extensions** | pin `3.10.0.2` | `typing_extensions 4.x` quebra a resolução de config do thinc/pydantic (`TypeError: issubclass() arg 1 must be a class`). 3.10.0.2 ainda satisfaz o torch 2.0. |
| **six**, **sacremoses** | adicionados | Deps transitivas do tokenizer FlauBERT do `transformers==4.9.2` (sem elas, `import transformers` falha). |
| **locale `en_US.UTF-8`** | gerado em user-space | `CQE/NumberNormalizer.py` faz `locale.setlocale(LC_ALL, 'en_US.UTF-8')` no import. Como não há `sudo`, o locale foi gerado com `localedef -i en_US -f UTF-8 ~/.locale/en_US.UTF-8` e exposto via `export LOCPATH=$HOME/.locale`. |

## Pinos preservados (do requirements original)

`spacy==3.0.9`, `spacy-transformers==1.0.4`, `transformers==4.9.2`, `protobuf==3.20.1`, `emoji==1.7.0`, `inflect==5.4.0`, `fuzzywuzzy==0.18.0`, `scikit-learn==1.0`, `stemming==1.0.1`, modelo `en_core_web_sm==3.0.0`. `pip check` limpo.

## Helper de ativação

`~/cqe_env.sh` (no WSL) faz `source` do conda, `conda activate cqe-eval` e exporta as variáveis de locale. Usar em toda execução:
```bash
source ~/cqe_env.sh
```

## Notas de execução

- `conda activate` em shell **não-interativo** (`wsl bash -lc`) ajusta o PATH, mas as variáveis de locale precisam ser exportadas explicitamente (por isso o helper).
- `spacy-transformers`/`torch` ficam instalados (declarados pela lib), mas **não são importados** na inferência do CQE nem na avaliação — confirmado: o parser e o desambiguador (TextCatBOW) não dependem deles em runtime.
- Smoke test (`example.py`) **passou**: saída idêntica à documentada no README da biblioteca.

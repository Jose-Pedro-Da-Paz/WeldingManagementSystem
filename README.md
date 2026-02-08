# Welding Declarative Rule Engine MVP

Motor declarativo para validação de documentos de soldagem (pWPS/PQR/WPS/WPQ/continuidade) com rule packs JSON carregados em runtime.

## Objetivo

- Nenhuma lógica normativa hardcoded no Python.
- Adicionar nova norma = adicionar `rules/<norma>/rules.json`.
- Contrato estável de saída: `status`, `findings`, `required_tests`, `approval_ranges`, `computed`, `debug`.

## Estrutura

- `engine/`
  - `loader.py`: carrega rule packs com `includes` e `overrides`.
  - `schema.py` + `engine/schema/rule_pack.schema.json`: valida schema JSON.
  - `evaluator.py`: DSL condicional (`eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `in`, `not_in`, `exists`, `not_exists`, `changed`, `regex`, `all/any/not`).
  - `math/functions.py`: funções pluggable (`RANGE_THICKNESS`, `RANGE_DIAMETER`, `RANGE_POSITION`, `NEEDS_REQUALIFICATION`).
  - `explanations.py`: construção padronizada de findings.
- `rules/`
  - `iso_15614_1/rules.json`
  - `iso_9606_1/rules.json`
  - `iso_3834/rules.json`
  - `ped_2014_68_eu/rules.json`
  - `common/materials.json`, `common/processes.json`, `common/positions.json`
- `tests/test_rule_engine.py`: schema, operadores, changed, includes e cenários por norma.

## Exemplo de uso

```python
from pathlib import Path
from engine.loader import RulePackLoader
from engine.evaluator import RuleEvaluator

loader = RulePackLoader(Path("rules"))
pack = loader.load("iso_15614_1/rules.json")

payload = {
  "doc_type": "PQR",
  "standard": "ISO_15614_1",
  "context": {"organization_country": "BR", "product_form": "plate", "industry": "pressure_equipment"},
  "inputs": {
    "process": "135",
    "base_material_group": "1.2",
    "thickness_tested_mm": 12,
    "joint_type": "BW",
    "position": "PA"
  },
  "history": {"previous_versions": []}
}

previous_payload = {
  **payload,
  "inputs": {**payload["inputs"], "process": "141"}
}

result = RuleEvaluator(pack, debug=True).evaluate(payload, previous_payload=previous_payload)
```

## Cobertura atual (MVP)

### ISO 15614-1
- Variáveis essenciais/suplementares essenciais: placeholders estruturados.
- Invalidação por mudança de variável essencial (`process`) e aviso para mudança de junta.
- Testes requeridos por condição de processo e forma do produto.
- Faixa de aprovação de espessura via função pluggable.

### ISO 9606-1
- Variáveis essenciais de WPQ estruturadas (processo, posição, continuidade).
- Regra de continuidade/expiração em placeholder (`months_since_last_continuity > 6`).
- Faixa de aprovação de posição via função pluggable.

### ISO 3834
- Checklist de compliance (coordenador de soldagem, rastreabilidade).
- Regras de completude documental e finding de não conformidade.

### PED 2014/68/EU
- Rule pack de gating para dossiê de equipamento sob pressão.
- Composição com `includes` de ISO 15614-1 + ISO 9606-1.
- Regras de completude/validade de WPS/PQR/WPQ em alto nível.

## Limites e verificação normativa

Os packs estão com cobertura parcial e placeholders. Campos normativos contêm `needs_verification: true` e, quando aplicável, `confidence: "unknown"`, para revisão em fontes licenciadas.

## Testes

```bash
pytest
python -m compileall engine backend
```

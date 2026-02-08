# Welding Management System MVP

MVP para gestão de qualificação de soldagem com foco em **WPS / PQR / WPQ** e motor de regras declarativo.

## Estrutura

- `backend/`: Django + DRF + JWT, modelos de domínio e avaliação de regras.
- `backend/engine`: loader/evaluator/explanations e regras JSON por norma.
- `frontend/`: React com UI de formulários dinâmicos e indicadores de status.

## Princípios implementados

- Regras normativas **fora do código Python**, carregadas de JSON.
- Fluxo de procedimentos preparado para `pWPS -> PQR -> WPS`.
- Entidades mínimas para documentos, versionamento e trilha de auditoria.
- Endpoint de avaliação normativa: `POST /api/rules/evaluate/`.

## Exemplo de payload para avaliação

```json
{
  "standard_slug": "iso_15614",
  "current": {
    "base_material_group": "FM2",
    "process": "135"
  },
  "previous": {
    "base_material_group": "FM1",
    "process": "141"
  }
}
```

# Welding Declarative Rule Engine MVP

Motor declarativo para validação de documentos de soldagem (pWPS/PQR/WPS/WPQ/continuidade) com rule packs JSON carregados em runtime, mais módulo de **Certificado de Operador de Soldador**.

## Objetivo

- Nenhuma lógica normativa hardcoded no Python.
- Adicionar nova norma = adicionar `rules/<norma>/rules.json`.
- Contrato estável de saída: `status`, `findings`, `required_tests`, `approval_ranges`, `computed`, `debug`.

## Estrutura

- `engine/` (loader/evaluator/schema/functions)
- `rules/` (packs ISO/PED + catálogos comuns)
- `backend/core` (API DRF, modelos, exportação PDF básica)
- `frontend/` (wizard e preview do certificado)

## Módulo de Certificado (ISO 14732 + PED)

### Backend
- Modelo principal: `WelderOperatorCertificate`
- Subentidades: `CertificateProcessEquipment`, `MechanizedWeldingDetails`, `AutomaticWeldingDetails`, `CertificateResultDocument`, `CertificateSignature`, `CertificateRevalidation`
- Regras de consistência:
  - `certificate_number` único por organização
  - `valid_until` calculado a partir de `weld_date` e `requalification_basis` (3y/6y)
  - `functional_knowledge_test_status=NOT_ACCEPTABLE` => `global_status=REJECTED`

### API
- `GET/POST /api/certificates/`
- `GET/PUT/PATCH/DELETE /api/certificates/{id}/`
- `POST /api/certificates/{id}/export-pdf/`
- `POST /api/rules/evaluate/`

### Frontend
- Wizard em 6 abas para o certificado
- Revalidações dinâmicas (empresa/supervisor e decision-maker)
- Preview estrutural do certificado
- Botão para exportação PDF (integração de chamada ao endpoint no próximo passo de wiring)

## Testes

```bash
pytest -q
python -m compileall engine backend frontend
```

## API (modo temporário)

Para facilitar a configuração do motor de regras no MVP, a API DRF está temporariamente sem exigência de autenticação (`AllowAny`).
Quando a fase de configuração terminar, restaurar `IsAuthenticated` nas configurações globais e nas views necessárias.

---
type: 'Task Contract'
title: 'Integracion obligatoria de calidad de producto en CI'
description: 'Ejecutar la politica del producto sobre la revision de CI con referencia explicita y runner congelado.'
tags: ['quality', 'ci', 'integration']
task: product-quality-ci
intent: 'Exigir aprobacion automatica de quality/product.json en el CI del proyecto.'
target: .github/workflows/validate.yml
language: yaml
signature: 'validate-contracts.validate: mandatory product quality approval'
test_command: 'python -m unittest tests/test_product_quality_ci.py'
budget:
  cyclomatic_max: 12
  nesting_max: 4
tests: tests/test_product_quality_ci.py
tests_sha256: '3e399f07d149ed00a3026e8411a62a361f9a6ab36ecf37f3ccf6b7c747e1a36c'
touch_only: ['.github/workflows/validate.yml', 'quality/product.json']
deps_allowed: ['stdlib']
forbids: ['llm']
---

## Intent
Aplicar [calidad de producto en CI](../product-quality-ci.md) sobre el checkout
completo, conservando la frontera de [aprobacion humana](../quality-approval.md).

## Interface
- Workflow nativo push main y pull_request, matriz Ubuntu/Windows.
- Politica default quality/product.json en inputs, job y paso de aprobacion.
- KDD_QUALITY_APPROVED_REF explicito, SHA completo, ancestro del checkout.
- Paso Check product quality approval configuration antes de oraculos/suites.
- Paso Approve project quality (when configured), id quality: ejecutor leido
  del objeto Git aprobado, aplicado al working tree e indice actuales.

## Invariants
- quality es evidencia requerida por defecto; ausencia o SHA invalido falla.
- No usar HEAD ni la rama base como aprobacion implicita.
- No ejecutar el verify_quality.py propuesto antes de verificar su integridad:
  extraer el runner stdlib desde el SHA aprobado a un archivo temporal externo.
- Los checks originales contracts/functional/adversarial/cli se conservan y
  ejecutan dos veces. Un fallo nunca se convierte en PASS ni SKIP satisfactorio.
- Conservar todos los protected existentes y agregar contrato/oraculo de esta
  integracion, el concepto y los dos artefactos exactos de TASK-001 cerrada.
- Nodo y evidencia de TASK-001 salen del permiso mutable: son historicos.
- No agregar permisos genericos, globs, excludes o proyecciones de revision.
- Conservar validacion independiente del diario, baseline, otros gates,
  resumen de calidad real, ambos OS y ambas pasadas completas de la suite.
- El rol de configuracion puede preparar el workflow revisable; el SHA que
  congela ese workflow y la politica se aprueba por humano antes de publicar.

## Examples
- Politica integra, referencia aprobada y TASK-001 cerrada -> PASS real 2x.
- Nombre de rama, SHA inexistente o no ancestral -> fallo de configuracion.
- Runner candidato imprime PASS falso -> rechazo por el runner aprobado.
- Evidencia historica modificada o codigo no declarado -> rechazo.

## Do / Don't
- DO probar cuerpos Python extraidos del workflow real en copias Git aisladas.
- DO preservar oraculos previos y sus sellos.
- DON'T ampliar pm a carpetas ni resellar pruebas existentes para obtener verde.

## Tests
tests/test_product_quality_ci.py usa clones locales aislados y subprocess
reales. Comprueba defaults, precondiciones, ejecucion doble, resumen PASS,
fallos funcionales, runner/politica/oraculo alterados y perimetro con evidencia.

## Constraints
PARAR y reportar si falta aprobacion de la nueva referencia o hace falta
relajar protecciones. No modifica codigo del saludo ni del repositorio KDD
original. El budget YAML es declarativo; no se afirma una medicion AST Python.

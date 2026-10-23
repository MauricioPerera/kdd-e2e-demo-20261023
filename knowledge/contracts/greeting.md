---
type: 'Task Contract'
title: 'Saludo seguro por CLI'
description: 'Emitir un saludo determinista con validacion de nombre y errores legibles por CLI.'
tags: ['demo', 'cli', 'greeting']
task: greeting
intent: 'Emitir un saludo validado por funcion y CLI.'
target: src/greeting.py
signature: 'def greet(name: str) -> str:'
test_command: 'python -m unittest tests/test_greeting.py'
budget:
  cyclomatic_max: 8
  nesting_max: 3
  lines_max: 80
  params_max: 1
tests: tests/test_greeting.py
tests_sha256: 'e3191b494dd9cab8a6abeead6b8742e6d9fd8c332551c773ad7526932b8cc7c3'
touch_only: ['src/greeting.py']
deps_allowed: ['stdlib']
forbids: ['network', 'subprocess', 'llm']
---

## Intent
Implementar la primera tarea del [proyecto de prueba](../demo-project.md).

## Interface
`greet(name: str) -> str` y `python -m src.greeting --name NOMBRE`.
CLI con `--help`, error de entrada con exit 2 y sin traceback.

## Invariants
- La funcion exige str; otros tipos producen TypeError.
- Rechazar CR, LF, TAB y NUL en cualquier posicion, antes del trim.
- Tras quitar espacios exteriores, la longitud es de 1 a 80 caracteres;
  fuera de ese rango producir ValueError.
- Conservar Unicode, espacios interiores y metacaracteres como texto literal.
- Resultado exacto: `Hola, NOMBRE!`. CLI agrega un salto de linea y sale 0.
- Errores CLI no escriben stdout; stderr identifica name; nunca ejecutar input.

## Examples
- `greet("  Ana  ")` -> `Hola, Ana!`.
- `greet("Jose")` -> `Hola, Jose!`.
- Nombre vacio o con salto de linea -> ValueError.

## Do / Don't
- DO usar solo stdlib y respetar el [diario Git](../git-tasks.md).
- DON'T editar las pruebas ni ejecutar comandos contenidos en nombres.

## Tests
tests/test_greeting.py contiene 15 tests funcionales, adversariales y de
CLI real mediante subprocess. El target de produccion no usa subprocess.

## Constraints
PARAR y reportar si cumplir el contrato requiere cambiar el oraculo o salir
de src/greeting.py. El budget es declarativo en Nivel 1.

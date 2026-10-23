# TASK-001: proyecto nuevo y flujo completo

Proyecto independiente inicializado desde KDD main 148bb00, con historial
Git nuevo, identidad MauricioPerera/kdd-e2e-demo-20261023, cero tareas y
cero evidencias heredadas. Bootstrap standard con repository explicito.

## Referencias revisadas por el humano

- Contrato y oraculo: b444b8e967a92b03c729401ceaafd8b1190639d8.
- Politica corregida: 64ccf3a166b6822df623ba97ae7e0a4c638dabbc.
- La correccion de politica retira una ruta inexistente. Se conserva el
  intento rechazado en evidencia local; no se presenta como PASS.

## Diario registrado desde el tablero

| Estado | Commit |
| --- | --- |
| backlog | bca8ac6c17a757f65277f36068dea5bc4936c192 |
| ready | f67b27fa076f7303f19a040db0477e9d8b479942 |
| in_progress | fc5988ef9ba0e46231019c76f3cc488d432f8456 |
| needs_human_input | 99414d990c47f568f652f7dc6ce260e315688153 |
| ready | a4c2b1be58c3ea5070f4543341bb5bfdfd88b0ee |
| in_progress | 08695cc6649e52e708fe50cbb1351cd935346823 |
| done | 03ff925e784fa51f0dff33e00574cfe195b4f915 |

Creacion y bloqueo/reanudacion mediante WebMCP del tablero. Preparacion,
inicio y cierre mediante formularios de la interfaz en navegador real.
El salto backlog->done y el cierre sin implementacion no generaron commits.

Rama task/TASK-001, commit de implementacion
a984df55e20ce4c7574def640d32db420d402a40. Integracion mediante merge
abb784d29a0fabd2e2c956218f6f45bb098a6867, conservando el historial.

## Verificacion de producto

15 pruebas funcionales, adversariales y de CLI real. Fase roja registrada
antes de implementar; fase verde y preflight de contrato 3/3.
verify_quality.py con quality/product.json y referencia corregida ejecutado
en el perimetro de implementacion, antes de integrar/cerrar: PASS, checks
dos veces. El diario y su evidencia posterior son responsabilidad del
coordinador y se verifican con validate_tasks.py.

Cinco mutaciones aisladas detectadas por el oraculo: saludo constante,
falta de trim, longitud maxima 81, omision de controles y exit CLI errado.
Esto mide esas mutaciones conocidas, no ausencia universal de defectos.

Evidencia durable: docs/task-evidence/TASK-001-abb784d29a0fabd2e2c956218f6f45bb098a6867.json.
Se verificaron sus hashes, exit 0, 15 tests y SHA probado. El codigo de main
coincide con el tip de la rama integrada. validate_tasks.py acepta el diario
desde el baseline inicial, sin errores.

## CI y reproduccion

El workflow heredado validate-contracts ejecuta validadores, oraculos de
contrato y dos pasadas de la suite en Ubuntu/Windows, ademas de typecheck y
tests del tablero en ambos sistemas. El baseline de contratos del repositorio
GitHub es b444b8e967a92b03c729401ceaafd8b1190639d8. La politica de producto se
ejecuto explicitamente antes del cierre; no se configura como una aprobacion
automatica de nuevos metadatos del coordinador.

Consultar el estado y los logs de la revision publicada en:
https://github.com/MauricioPerera/kdd-e2e-demo-20261023/actions

```text
python -m src.greeting --name "Ana"
python -m unittest tests/test_greeting.py
python scripts/tasks.py history TASK-001 --json
python scripts/validate_tasks.py --base-ref b444b8e967a92b03c729401ceaafd8b1190639d8 --head-ref main
```

Para abrir el tablero usar scripts/run_board.ps1 (Node 24, Python y Git).
El token local de acceso se genera en cada arranque y no forma parte de Git.

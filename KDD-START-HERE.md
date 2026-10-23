# Primeros pasos con KDD

Este proyecto (KDD E2E Demo) fue inicializado con el perfil `standard`.

## Qué hacer ahora

1. Lee `knowledge/index.md` para conocer las reglas del proyecto.
2. Crea un test que describa el resultado esperado.
3. Crea un contrato en `knowledge/contracts/` y sella su test.
4. Si usas `standard` o `strict`, pide a una persona que apruebe el commit
   con contrato y test y te entregue su SHA completo.
5. Ejecuta el perfil elegido:

```text
python scripts/run_profile.py --profile standard --approved-ref <SHA_APROBADO>
```

Para una tarea concreta, valida también su budget:

```text
python scripts/validate_budgets.py knowledge/contracts --repo-root . --contract <task>
```

KDD comprueba las reglas declaradas; una persona sigue revisando si esas reglas
representan la necesidad real del producto. Consulta `docs/KDD-PARA-PERSONAS.md`
si quieres una explicación sin tecnicismos.

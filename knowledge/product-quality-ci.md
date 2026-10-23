---
type: 'Concept'
title: 'Calidad de producto obligatoria en CI'
description: 'Aprobacion del checkout completo con politica congelada y evidencia Git exacta.'
tags: ['quality', 'ci', 'approval']
---

# Calidad de producto en CI

El [proyecto](demo-project.md) usa quality/product.json como politica nativa
de CI. Se aplica el [protocolo de aprobacion](quality-approval.md) a todo el
checkout que se publica, sin filtrar archivos ni volver a una revision antigua
para obtener un resultado verde.

La configuracion declarativa, politica y oraculos integran un commit revisado
por el humano. Ese SHA completo se registra en KDD_APPROVED_BASELINE_REF y
KDD_QUALITY_APPROVED_REF. El agente no los actualiza sin esa aprobacion.
La politica tambien congela el workflow, por lo que su configuracion final
debe estar incluida en el commit que el revisor aprueba antes de publicar.

Los dos jobs validate requieren politica presente y SHA aprobado ancestro.
El ejecutor verify_quality.py se extrae de ese commit, evitando ejecutar una
copia del runner alterada por el candidato. El ejecutor compara tambien la
copia actual protegida y realiza los checks originales dos veces.

TASK-001 ya esta cerrada. Su nodo y JSON historico se agregan como archivos
protegidos exactos. No se permiten globs para futuras evidencias: otra tarea
requiere revisar su perimetro. El [validador del diario](contracts/task-validation.md)
continua auditando estados y evidencia como paso independiente del CI.

El resumen quality informa PASS solamente tras el gate real exitoso. Una
politica ausente, referencia faltante, no ancestral o alteracion protegida
impide aprobar. Se mantienen Ubuntu/Windows, los demas gates y la suite 2x.
La compatibilidad opcional del paso generico no permite un CI nativo verde
sin calidad: la precondicion del proyecto y required_evidence la hacen obligatoria.

El [contrato de integracion](contracts/product-quality-ci.md) fija estas
garantias y su oraculo de Git y subprocess reales.

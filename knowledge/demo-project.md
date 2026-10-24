---
type: 'Concept'
title: 'Proyecto de prueba independiente de KDD'
description: 'Un saludo por CLI sirve para recorrer el diario Git y verificar un proyecto nuevo.'
tags: ['demo', 'project', 'cli']
---

# KDD E2E Demo

Proyecto de prueba, sin datos reales, inicializado desde KDD main 148bb00.
Su historial Git comienza desde cero. No hereda tareas ni aprobaciones.

La primera tarea implementa [el saludo](contracts/greeting.md). El tablero
registra el recorrido completo, incluido bloqueo y reanudacion. Las pruebas
funcionales, adversariales y de CLI son el oraculo de producto.

La politica quality/product.json se aplica al checkout completo mediante
[la integracion obligatoria de CI](product-quality-ci.md), con referencia
aprobada explicita. Los artefactos historicos de TASK-001 estan protegidos;
[el validador del diario](contracts/task-validation.md) audita sus estados
y evidencia por separado. Ubuntu y Windows ejecutan tambien dos pasadas de
la suite. Una validacion verde comprueba las garantias declaradas y no
equivale a una garantia universal de calidad ni a una aprobacion humana.

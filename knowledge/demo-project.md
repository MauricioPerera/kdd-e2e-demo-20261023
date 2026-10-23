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

La politica quality/product.json aprueba el perimetro del implementador en
la rama de tarea, antes de integrar y cerrar. Los metadatos y la evidencia
posterior del coordinador se auditan con [el validador del diario](contracts/task-validation.md).
El CI heredado comprueba los oraculos actuales y el diario en Ubuntu y
Windows, con dos pasadas de la suite. Una validacion estructural verde no
equivale a una garantia universal de calidad ni a una aprobacion humana.

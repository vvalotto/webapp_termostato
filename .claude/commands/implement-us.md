# Comando: implement-us

Implementa una Historia de Usuario siguiendo las 10 fases del Claude Dev Kit.

## Uso

```
/implement-us US-XXX
```

## Instrucciones

Cuando el usuario ejecute este comando:

1. Leer el skill principal: `.claude/skills/implement-us/skill.md`
2. Leer la configuración del proyecto: `.claude/skills/implement-us/config.json` y `.claude/skills/implement-us/customizations/flask-webapp.json`
3. El argumento `$ARGUMENTS` contiene el ID de la historia (ej: `US-001`)
4. Ejecutar las fases secuencialmente leyendo cada archivo de fase:
   - Fase 0: `.claude/skills/implement-us/phases/phase-0-validation.md`
   - Fase 1: `.claude/skills/implement-us/phases/phase-1-bdd.md`
   - Fase 2: `.claude/skills/implement-us/phases/phase-2-planning.md` *(STOP — esperar aprobación)*
   - Fase 3: `.claude/skills/implement-us/phases/phase-3-implementation.md`
   - Fase 4: `.claude/skills/implement-us/phases/phase-4-unit-tests.md`
   - Fase 5: `.claude/skills/implement-us/phases/phase-5-integration-tests.md`
   - Fase 6: `.claude/skills/implement-us/phases/phase-6-bdd-validation.md`
   - Fase 7: `.claude/skills/implement-us/phases/phase-7-quality-gates.md`
   - Fase 8: `.claude/skills/implement-us/phases/phase-8-documentation.md`
   - Fase 9: `.claude/skills/implement-us/phases/phase-9-final-report.md` *(STOP — reporte debe existir en disco)*

## Variables

- `$ARGUMENTS`: ID de la historia de usuario (ej: `US-001`)

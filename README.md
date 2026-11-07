# Nómina Clara

Nómina Clara es nuestro proyecto de la materia Compiladores (Ingeniería de Software, UCC Pasto). Es una página web donde el contador de una empresa pequeña escribe las reglas de nómina en un lenguaje en español, y nuestro compilador las pasa por las 7 fases vistas en clase hasta calcular el valor a pagar de cada empleado.

Equipo: Daniers, Ramírez y Mora.

## Qué hay en este repositorio

Dejé lista la estructura completa para que cada uno trabaje en paralelo desde el primer día:

- La API (`api/compile.py`) y el orquestador (`compiler/pipeline.py`) ya funcionan.
- Los formatos compartidos ya están definidos y no deberían cambiar sin avisar a los demás: `Token`, los nodos del AST, `Symbol` y `TacInstruction`.
- Cada fase está como esqueleto con un `TODO` que dice qué hay que hacer. Mientras una fase lanza `NotImplementedError`, el pipeline la marca como **pendiente** y la página la pinta en amarillo; las fases siguientes quedan en gris.
- El generador de código objetivo (`code_generator.py`) ya trae el código del profesor de la semana 10 traducido al inglés. Le falta agregar división, comparaciones, saltos y etiquetas.
- La página Angular ya tiene editor, tabla de empleados, barra de fases, un panel por fase y la tabla de nómina.

Convención: todo el código (archivos, clases, funciones y variables) va en inglés; los comentarios van en español. Los textos de la página están en `public/i18n/es.json`.

## Cómo correrlo en local

Necesito Node 22 o superior y Python 3.12 o superior, las mismas versiones que usa el CI. El compilador no usa librerías externas de Python.

```bash
npm install
python dev_server.py      # terminal 1: API en http://localhost:3000/api/compile
npm start                 # terminal 2: página en http://localhost:4200
```

En Mac o Linux, si `python` no existe, usen `python3` en todos los comandos.

Angular redirige `/api` al servidor de Python con `proxy.conf.json`, así que la página funciona igual que en Vercel.

## Pruebas

```bash
python -m unittest discover -s tests -t .
```

Las pruebas de una fase pendiente salen como `skipped`. A medida que implementamos cada fase, sus pruebas empiezan a correr de verdad. Las pruebas usan los programas de `examples/`.

Ojo: si el resultado dice `OK (skipped=N)`, eso no significa que la fase esté lista, solo que sus pruebas se saltaron porque sigue pendiente. Una fase está lista cuando sus pruebas corren y pasan sin salir como `skipped`.

## Estructura y responsables

| Archivo | Fase | Semana | Responsable |
| --- | --- | --- | --- |
| `compiler/tokens.py`, `compiler/lexer.py` | 1. Lexer | 2 | Daniers |
| `compiler/ast_nodes.py`, `compiler/parser.py` | 2. Parser y AST | 3 y 4 | Daniers |
| `compiler/symbol_table.py`, `compiler/type_checker.py` | 3. Tabla y tipos | 5 y 6 | Ramírez |
| `compiler/ir.py`, `compiler/ir_generator.py` | 4. TAC | 7 | Mora |
| `compiler/memory_manager.py` | 5. Memoria | 8 | Ramírez |
| `compiler/optimizer.py` | 6. Optimización | 9 | Mora |
| `compiler/code_generator.py` | 7. Código objetivo | 10 | Mora |
| `compiler/virtual_machine.py` | Ejecución de la nómina | 4 y 8 | Ramírez |
| `compiler/pipeline.py`, `api/compile.py`, `dev_server.py` | Orquestador y API | 1 | Daniers |
| `src/app/features/phases/panels/*` | Un panel por fase | — | El dueño de cada fase |

## Contrato de la API

`POST /api/compile` recibe:

```json
{ "source": "constante SMMLV: dinero = $1.750.905 ...", "employees": [{ "nombre": "Ana Ortiz", "salario": 1750905, "extras": 6 }] }
```

Y responde:

```json
{
  "ok": true,
  "status": { "lexer": "passed", "parser": "passed", "semantic": "passed", "ir": "passed", "memory": "passed", "optimizer": "passed", "codegen": "passed", "execution": "passed" },
  "phases": { "tokens": [], "ast": {}, "symbols": [], "tac": {}, "memory": {}, "optimized": {}, "assembly": {} },
  "payroll": [{ "name": "Ana Ortiz", "values": { "devengado": 2054716 }, "pay": 1914643 }],
  "errors": []
}
```

Cada estado puede ser `passed`, `failed`, `pending` o `skipped`. Los errores traen `phase` (`lexical`, `syntax`, `semantic` o `runtime`), `message`, `line` y `col`.

## Cómo trabajamos con Git

- Una rama por persona: `feature/lexer-parser`, `feature/semantic-memory` y `feature/backend`.
- Nada entra a `main` sin que otro del equipo lo revise.
- Antes de subir, corremos las pruebas.

## Despliegue en Vercel

1. Subo el repositorio a GitHub.
2. En Vercel: Add New → Project → importo el repositorio → Deploy.

Vercel detecta Angular para la página y convierte `api/compile.py` en una función serverless de Python en `/api/compile`. No hay que configurar nada más; `vercel.json` solo evita que la función cargue `node_modules`.

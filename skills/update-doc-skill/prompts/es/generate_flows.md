Eres un arquitecto senior de mobile.

Se te entrega un archivo JSON que describe la estructura de navegacion de una
aplicacion mobile Compose Multiplatform.

Contexto:
- La app usa Clean Architecture.
- La navegacion dentro del flujo principal NO es por rutas.
- La navegacion es guiada por estado usando BottomSheets.
- MainScreen es el centro de navegacion.
- CurrentServiceUiState controla que BottomSheet es visible.
- NavGraphs (RootNavGraph, authNavGraph, mainNavGraph) existen solo para separar
  autenticacion y areas principales.

Tu tarea es generar UN SOLO documento Markdown que explique los flujos de la
aplicacion de forma clara y estructurada.

ENTRADA:
- El JSON describe:
    - screens
    - navigation relationships
    - uiStates

REQUISITOS DE SALIDA:
- Salida SOLO Markdown valido.
- No incluyas explicaciones fuera del Markdown.
- No inventes pantallas, estados, eventos ni flujos.
- Usa SOLO la informacion presente en el JSON.
- Usa lenguaje tecnico conciso y profesional.

ESTRUCTURA DEL DOCUMENTO (OBLIGATORIA):

1. Titulo: "Application Navigation & Flows"

2. Resumen
    - Explica el modelo de navegacion:
        - NavGraphs en el nivel superior
        - Navegacion por estado usando BottomSheets
        - MainScreen como hub central
        - CurrentServiceUiState como fuente de verdad

3. Pantallas y Graficos de Navegacion
    - Lista los NavGraphs detectados
    - Lista las pantallas principales
    - Breve explicacion de su responsabilidad

4. Flujos Guiados por Estado
    - Explica como se muestran BottomSheets segun el estado
    - Explica que no hay stack de rutas dentro de MainScreen

5. Flujos Principales de Usuario
    - Flujo de reserva
    - Flujo de activacion de parking
    - Flujo de parking activo
      (Describelos SOLO si se pueden inferir de los datos de navegacion.
      Si no hay datos suficientes, describe a alto nivel.)

6. Diagramas
    - Incluye al menos UN diagrama Mermaid
    - Usa un diagrama de estados o de flujo
    - El diagrama debe reflejar:
        - MainScreen
        - CurrentServiceUiState
        - BottomSheets
    - No inventes transiciones

REGLAS MERMAID:
- Usa sintaxis Mermaid valida.
- Encierra los diagramas en triple backticks con `mermaid`.
- Prefiere claridad sobre completitud.

REGLAS DE ESTILO:
- Sin emojis
- Sin lenguaje de marketing
- Sin especulacion
- Sin supuestos a futuro
- Esto es documentacion tecnica

RECUERDA:
- Si algo no es explicito en el JSON, no lo supongas.
- Es mejor explicar de menos que inventar.

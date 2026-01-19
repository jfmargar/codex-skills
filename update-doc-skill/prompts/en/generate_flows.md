You are a senior mobile architect.

You are given a JSON file that describes the navigation structure of a
Compose Multiplatform mobile application.

Context:
- The app uses Clean Architecture.
- Navigation inside the main flow is NOT route-based.
- Navigation is state-driven using BottomSheets.
- MainScreen is the navigation hub.
- CurrentServiceUiState controls which BottomSheet is visible.
- NavGraphs (RootNavGraph, authNavGraph, mainNavGraph) exist only to split
  authentication and main areas.

Your task is to generate a SINGLE Markdown document that explains the
application flows in a clear and structured way.

INPUT:
- The JSON describes:
    - screens
    - navigation relationships
    - uiStates

OUTPUT REQUIREMENTS:
- Output ONLY valid Markdown.
- Do NOT include explanations outside the Markdown.
- Do NOT invent screens, states, events, or flows.
- Use ONLY the information present in the JSON.
- Use concise, professional technical language.

DOCUMENT STRUCTURE (MANDATORY):

1. Title: "Application Navigation & Flows"

2. Overview
    - Explain the navigation model:
        - NavGraphs at top level
        - State-driven navigation using BottomSheets
        - MainScreen as the central hub
        - CurrentServiceUiState as the source of truth

3. Screens & Navigation Graphs
    - List detected NavGraphs
    - List main Screens
    - Short explanation of their responsibility

4. State-Driven Flows
    - Explain how BottomSheets are shown based on state
    - Explain that there is no route stack inside MainScreen

5. Main User Flows
    - Reservation flow
    - Parking activation flow
    - Active parking flow
      (Describe them ONLY if they can be inferred from the navigation data.
      If not enough data exists, describe them at a high level.)

6. Diagrams
    - Include at least ONE Mermaid diagram
    - Use a state diagram or flow diagram
    - Diagram must reflect:
        - MainScreen
        - CurrentServiceUiState
        - BottomSheets
    - Do NOT invent transitions

MERMAID RULES:
- Use valid Mermaid syntax.
- Wrap diagrams in triple backticks with `mermaid`.
- Prefer clarity over completeness.

STYLE RULES:
- No emojis
- No marketing language
- No speculation
- No future assumptions
- This is technical documentation

REMEMBER:
- If something is not explicit in the JSON, do NOT guess it.
- Under-explain rather than invent.
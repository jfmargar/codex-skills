# Modulo base: arquitectura

[Volver al README](../README.md)

{{dabase_overview}}

## Estructura principal

```mermaid
graph TD;
A[{{dabase_node}}] --> B[{{dabase_root}}];
B --> C[{{dabase_data}}];
B --> D[{{dabase_domain}}];
B --> E[{{dabase_injection}}];
B --> F[{{dabase_ui}}];
B --> G[{{dabase_utils}}];
```

{{dabase_structure_notes}}

## Base UI

```mermaid
graph LR;
V[{{base_view}}] --> P[{{base_presenter}}];
P --> A[{{base_activity}}];
A --> S[{{base_scenes}}];
```

{{base_ui_notes}}

## Inyeccion de dependencias

```mermaid
graph TD;
K[{{di_component}}] --> C[{{di_context}}];
K --> R[{{di_router}}];
K --> S[{{di_secured}}];
K --> U[{{di_unsecured}}];
```

{{di_notes}}

## Datos y red

{{network_notes}}

## Recursos

{{resource_notes}}

# Arquitectura del proyecto

[Volver al README](../README.md)

{{project_overview}}

## Vista general

Modulos principales:

{{modules_list}}

Servicios externos principales:

{{external_services}}

## Diagrama de alto nivel

```mermaid
graph TD;
A[{{node_entry}}] --> B[{{node_app}}];
B --> C[{{node_app_init}}];
B --> D[{{node_presenters}}];
B --> E[{{node_api_module}}];
B --> F[{{node_router}}];
D --> G[{{node_base_ui}}];
E --> H[{{node_api}}];
B --> I[{{node_firebase}}];
B --> J[{{node_assets}}];
```

## Flujo de arranque

{{startup_flow}}

## Capas y responsabilidad

{{layers}}

## Navegacion

{{navigation_summary}}

## Puntos clave de configuracion

{{config_points}}

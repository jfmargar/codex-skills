# Customizacion del modulo base en esta app

[Volver al README](../README.md)

{{custom_overview}}

## Inyeccion y configuracion base

```mermaid
graph TD;
A[{{custom_app_presenters}}] --> B[{{custom_injector}}];
B --> C[{{custom_context}}];
B --> D[{{custom_api_module}}];
B --> E[{{custom_router}}];
```

{{custom_injection_notes}}

## Configuracion de API y entorno

{{custom_api_config}}

## Personalizacion de navegacion

```mermaid
graph LR;
N[{{custom_navigate}}] --> R[{{custom_router_node}}];
R --> C[{{custom_corporates}}];
R --> Nw[{{custom_news}}];
R --> F[{{custom_filter}}];
R --> D[{{custom_documents}}];
R --> S[{{custom_send}}];
```

{{custom_navigation_notes}}

## Recursos y UI

{{custom_ui_notes}}

## Firebase

{{custom_firebase_notes}}

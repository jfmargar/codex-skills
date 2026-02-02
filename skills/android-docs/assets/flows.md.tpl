# Flujos principales

[Volver al README](../README.md)

{{flows_overview}}

## 1) Arranque y navegacion inicial

```mermaid
sequenceDiagram
    participant App as {{flow_app}}
    participant Splash as {{flow_splash}}
    participant Presenter as {{flow_presenter}}
    participant Nav as {{flow_nav}}
    participant Login as {{flow_login}}
    participant News as {{flow_news}}
    participant Corp as {{flow_corp}}

    App->>App: onCreate()
    App->>App: setBaseUrl and setLoginUrl
    Splash->>Presenter: onViewCreated()
    Presenter->>Presenter: check token
    alt token disponible
        Presenter->>Splash: goToApp()
        Splash->>Nav: goToNews or goToCorporates
        Nav->>News: startActivity()
        Nav->>Corp: startActivity()
    else sin token
        Presenter->>Splash: goToAuthorizationIfNeeded()
        Splash->>Nav: goToLogin()
        Nav->>Login: startActivity()
    end
```

{{flow_startup_notes}}

## 2) Inyeccion de dependencias

```mermaid
graph TD;
A[{{flow_injector_root}}] --> B[{{flow_injector}}];
B --> C[{{flow_context}}];
B --> D[{{flow_api_module}}];
B --> E[{{flow_router}}];
D --> F[{{flow_api_services}}];
```

{{flow_di_notes}}

## 3) Navegacion principal

```mermaid
graph LR;
S[{{flow_splash}}] --> C[{{flow_corporates}}];
S --> N[{{flow_news}}];
N --> D[{{flow_news_detail}}];
N --> F[{{flow_filter}}];
N --> Docs[{{flow_documents}}];
Docs --> Edit[{{flow_edit}}];
Docs --> Send[{{flow_send}}];
N --> Gen[{{flow_generate}}];
N --> Full[{{flow_fullscreen}}];
```

{{flow_navigation_notes}}

## 4) Flujo de datos

```mermaid
graph LR;
UI[{{flow_ui}}] --> API[{{flow_api}}];
API --> NET[{{flow_net}}];
NET --> SIMBIU[{{flow_backend}}];
UI --> PREFS[{{flow_prefs}}];
```

{{flow_data_notes}}

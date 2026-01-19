# Arquitectura limpia y capas

Este repositorio aplica Clean Architecture en un proyecto Kotlin Multiplatform (KMP).

## Capas y dependencias
- **Domain (shared)**: lógica de negocio y modelos puros. Los casos de uso pueden depender de repositorios y coroutines; evita dependencias de UI o plataforma.
- **Data (shared)**: implementaciones de repositorios, mappers y acceso a datos. Depende de Domain.
- **UI (shared)**: Compose Multiplatform. Solo depende de ViewModels, no contiene lógica de negocio.
- **Plataforma**: `androidMain` y `iosMain` contienen integraciones específicas (Activity, ViewController, permisos, etc.).

## Reglas globales
- Domain no depende de UI ni plataformas específicas.
- UI depende solo de ViewModels.
- No hay lógica de negocio en UI.
- No exponer estado mutable públicamente.
- Preferir composición sobre herencia.
- KMP: el módulo compartido es dueño del dominio y los contratos de datos.

## Ubicación sugerida
- Domain: `composeApp/src/commonMain/kotlin/.../domain`
- Data: `composeApp/src/commonMain/kotlin/.../data`
- UI: `composeApp/src/commonMain/kotlin/.../ui`
- Integraciones de plataforma: `composeApp/src/androidMain` y `composeApp/src/iosMain`

## Flujos de servicio (responsabilidades por capa)
- Domain resuelve el estado funcional con `ServiceFlowStateResolverUseCase` a partir de `GET /api/app/services/current`.
- UI traduce `ServiceFlowState` a sheets y modos de activacion en `MainViewModel` y `MainScreen`.
- Las fases de activacion se expresan como `ParkingActivationPhase` (`Activation`, `Reopening`, `Finishing`).

## Cumplimiento arquitectónico
Si un cambio propuesto viola estas reglas:
- Explicar por qué es inválido.
- Proponer una alternativa compatible.
- No implementar soluciones que rompan la arquitectura.

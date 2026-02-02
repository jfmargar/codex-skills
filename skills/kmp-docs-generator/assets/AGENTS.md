# Repository Guidelines

## Project Structure & Module Organization

Modulos detectados:

{{modules}}

## Build, Test, and Development Commands

- `./gradlew build`
- `./gradlew :composeApp:assembleDebug` (si existe `composeApp`)
- iOS: abrir `iosApp` en Xcode y ejecutar el scheme correspondiente (si aplica)

## Coding Style & Naming Conventions

- Kotlin: 4 espacios, `PascalCase` para clases y `camelCase` para funciones/vars.
- Compose: UI en `commonMain` cuando sea posible; usar `androidMain`/`iosMain` solo para APIs de plataforma.

## Testing Guidelines

- Tests compartidos en `commonTest` cuando exista.
- Priorizar lógica compartida y casos de uso.

## Reference Docs

- `docs/overview.md`
- `docs/architecture.md`
- `docs/navigation.md`

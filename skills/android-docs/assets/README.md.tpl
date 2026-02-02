{{project_summary}}

Documentacion de arquitectura y flujos:
- [docs/arquitectura.md](docs/arquitectura.md): vista general, modulos y diagrama de alto nivel.
- [docs/dabase-arquitectura.md](docs/dabase-arquitectura.md): estructura interna del modulo base.
- [docs/customizacion-dabase.md](docs/customizacion-dabase.md): como la app integra y personaliza el modulo base.
- [docs/flows.md](docs/flows.md): flujos principales (arranque, DI, navegacion y datos).
- [docs/structure.json](docs/structure.json): rutas clave del proyecto.

Comandos habituales:
- `./gradlew clean`
- `./gradlew assembleDebug`
- `./gradlew assembleDevDebug`
- `./gradlew assembleRelease`
- `./gradlew lint`

Notas:
- `app/google-services.json` es requerido para Firebase.
- El release usa variables de entorno: `APK_KSTOREPWD`, `APK_KEYPWD`, `APK_KEYALIAS`.

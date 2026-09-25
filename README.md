# smartdata_football

Rama `main` reservada para los **pases de despliegue** (CI/CD / Databricks) que se configurarán después.

El código del entregable (notebooks, datasets, preparación, seguridad, etc.) está en la rama:

- [`construccion`](https://github.com/CesarValenciaM/smartdata_football/tree/construccion)

Flujo previsto:
1. Desarrollar y versionar en `construccion`
2. Configurar los pases en `main`
3. Promover cambios hacia `main` cuando el despliegue esté listo

# Databricks App – SmartData Football

App Streamlit que incrusta el dashboard AI/BI publicado mediante un iframe.

| Archivo | Descripción |
|---|---|
| `app.py` | Página Streamlit con el iframe del dashboard embed. |
| `app.yaml` | Comando de arranque de la Databricks App. |
| `requirements.txt` | Dependencias (`streamlit`). |

## Despliegue

1. Publica el dashboard AI/BI con **Embed credentials** y copia la URL de **Share → Embed dashboard**.
2. En el workspace, un admin debe permitir el dominio `*.databricksapps.com` en **Settings → Security → Embed dashboards**.
3. En **Compute → Apps**, crea o edita la app y apunta el código fuente a esta carpeta (`dashboard/dashboard_app`).
4. **Deploy** y, cuando esté **Running**, abre la URL `*.databricksapps.com`.

Si cambias la URL de embed, actualiza la constante en `app.py` y vuelve a desplegar.

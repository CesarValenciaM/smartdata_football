# Dashboard Power BI – SmartData Football

Dashboard interactivo sobre las 5 tablas gold del share `football_share`, leídas por **Delta Sharing**:
`season_stats`, `standings`, `calendar_stats`, `club_elo` y `match_predictions`.

| Archivo | Descripción |
|---|---|
| `dashboard.pbix` | Archivo único que se versiona en git (guardado desde Desktop). |
| `dashboard.pbip` | Proyecto editable (local, no se versiona). |
| `dashboard.SemanticModel/` | Modelo (TMDL): las 5 tablas Delta Sharing, dimensiones `Ligas`, `Temporadas` y `Clubes`, relaciones y la tabla `Medidas`. |
| `dashboard.Report/` | Reporte (PBIR): 4 páginas más la ficha de club y tema `SmartDataFootball.json` (colores por liga). |
| `Fútbol Big Five - Resumen por Temporada.lvdash.json` | Dashboard de Databricks (AI/BI). |

## Modelo

- `Ligas`, `Temporadas` y `Clubes` salen de las propias consultas (`season_stats` y `standings`) y filtran todas las tablas de hechos.
- Los segmentadores usan esas dimensiones, así que una misma selección de liga o temporada aplica a todas las páginas.

## Interactividad

- Navegación entre páginas desde el encabezado.
- Segmentadores de **Liga** (botones) y **Temporada** sincronizados entre páginas.
- Botón **Limpiar filtros** (en Desktop: Ctrl + clic).
- Tarjeta **Selección** que muestra qué se está viendo (ej. `La Liga · 3 temporadas`).
- Filtrado cruzado: clic en una barra, línea, porción o fila filtra el resto.
- **Drillthrough por club**: clic derecho en un club (tabla de posiciones o gráfico de Elo) ▸ *Obtener detalles* ▸ *Club*.

## Páginas

Cada página responde una pregunta, con un máximo de 4 KPIs y 3 gráficos. Los títulos son dinámicos y dicen la conclusión (por ejemplo, la liga que lidera la métrica elegida).

1. **Resumen** (¿cómo es el fútbol de las Big Five?):
   - KPIs de partidos, goles por partido, % de victorias locales y precisión de tiro.
   - Goles por partido por temporada.
   - Goles por partido según el mes de la temporada.
   - Reparto local / empate / visitante por liga.
2. **Ligas** (¿en qué se diferencia cada liga?): selector de métrica (goles por partido, % victorias locales, precisión de tiro, conversión, tarjetas por partido, remontadas por 100 partidos) con ranking por liga y evolución por temporada.
3. **Posiciones** (¿quién ganó y quién viene fuerte?):
   - Liga y temporada de selección única (por defecto Premier League 2024/25).
   - Clasificación con colores por zona y Elo al cierre de la temporada.
4. **Predicciones** (¿se puede anticipar el resultado?): acierto del modelo, acierto apostando siempre por el local, mejora, acierto por liga y probabilidades partido a partido. Por defecto muestra el conjunto `prueba`, que es la última temporada.
5. **Club** (oculta, se abre con clic derecho en un club ▸ *Obtener detalles* ▸ *Club*): Elo actual y máximo, títulos, % de victorias, evolución del Elo y partidos. Tiene un botón Volver.

Para ver el detalle de cualquier gráfico: clic derecho ▸ *Mostrar como tabla*.

## Uso

1. Las tablas nuevas tienen que existir en el share: correr `WF_FOOTBALL` y luego `6.DeltaSharing`.
2. Abrir `dashboard.pbip` con Power BI Desktop.
3. **Inicio → Actualizar** (si pide credencial, pegar el *bearer token* del archivo `config.share`).
4. **Archivo → Guardar como → `dashboard.pbix`** para tener el archivo único que se sube a git.

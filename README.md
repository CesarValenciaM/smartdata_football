# smartdata_football

Pipeline de ingeniería de datos para fútbol de las 5 grandes ligas europeas, con la misma arquitectura medallion del proyecto [CICDSMARTDATA3007](https://github.com/AnthonyHuaccachiA/CICDSMARTDATA3007) (F1).

Usa Databricks, Azure Data Lake, Unity Catalog y un job de GitHub Actions.

**Convención de nombres (Unity Catalog):**

| Nivel | Nombre |
|---|---|
| Proyecto / repo / carpeta Workspace | `smartdata_football` |
| Catálogo | `football_dev` (dominio + ambiente) |
| Schemas | `bronze`, `silver`, `gold` |
| Tabla gold | `season_stats` |

El contenedor ADLS de la capa gold sigue llamándose `golden` (igual que en el curso/F1) para no exigir un contenedor nuevo. El schema de Unity Catalog sí es `gold`.

## Origen de los datos

La data completa sale de [Football Stats - Top 5 Leagues European 2018–2025](https://www.kaggle.com/datasets/clemendes/football-stats-top-5-leagues-2018-to-2025) (`archive.zip` → `stats_top5_leagues._2018_2025.csv`): 12 532 partidos, 144 clubes, 7 temporadas (2018/19–2024/25), 5 ligas.

El CSV original es plano (`Div`, `League`, `Date`, `HomeTeam`, `AwayTeam`, `FTHG`, `FTAG`, `Season`, etc.). Aquí se **normalizó** en 3 archivos, igual que en F1 (2 CSV + 1 JSON):

| Kaggle (plano) | Este proyecto | Análogo F1 |
|---|---|---|
| `Div` / `League` | `datasets/leagues.csv` | `circuits.csv` |
| partidos y goles | `datasets/matches.csv` | `races.csv` |
| `HomeTeam` / `AwayTeam` | `datasets/clubs.json` | `constructors.json` |

`datasets/` ya tiene el dataset **completo**, listo para subir al contenedor `raw` de ADLS. El filtro silver `season_year >= 2010` deja pasar todas las temporadas de este archivo (empiezan en 2018).

## Flujo

```
raw (ADLS)
  leagues.csv  +  matches.csv  +  clubs.json
        │
        ▼
bronze (football_dev.bronze)
  leagues  |  matches (particionado por season_year)  |  clubs
        │
        ▼  join + reglas de negocio
silver (football_dev.silver.matches_transformed)
        │
        ▼  agregación por temporada / país / liga  +  tabla de posiciones por club
gold (football_dev.gold.season_stats  |  football_dev.gold.standings)
```

Job `WF_FOOTBALL`:

1. Preparación del ambiente
2. Ingesta de ligas, partidos y clubes (en paralelo)
3. Transformación bronze → silver
4. Carga silver → gold
5. Grants de Unity Catalog

## Catálogo de archivos

### Raíz

| Archivo | Qué es |
|---|---|
| `README.md` | Este documento: propósito, origen de datos, flujo y catálogo de archivos. |

### `datasets/` — datos de entrada (capa raw)

| Archivo | Formato | Qué contiene | Cómo se usa |
|---|---|---|---|
| `datasets/leagues.csv` | CSV con header | 5 ligas: Premier League, La Liga, Serie A, Bundesliga, Ligue 1. Columnas: `league_id`, `league_ref`, `name`, `country`, `country_code`, `confederation`, `tier`, `founded_year`. | Lo lee `2.Ingest_leagues_data`. |
| `datasets/matches.csv` | CSV con header | 12 532 partidos (2018/19–2024/25). Columnas: `match_id`, `season_year`, `round`, `match_date`, `league_id`, `home_club`, `away_club`, `home_goals`, `away_goals`, `ht_home_goals`, `ht_away_goals` y estadísticas por equipo (`home_`/`away_`): `shots`, `shots_on_target`, `corners`, `fouls`, `yellow_cards`, `red_cards`. `round` es la jornada (1–38, o 1–34 en ligas de 18 clubes), asignada por orden cronológico dentro de cada liga y temporada; los partidos aplazados cuentan en la jornada en que se jugaron. | Lo lee `2.Ingest_matches_data`. |
| `datasets/clubs.json` | JSON array | 144 clubes con `club_id`, `club_ref`, `name`, `country`, `city`, `founded_year`, `league_id`. | Lo lee `2.Ingest_clubs`. |

Hay que copiar estos 3 archivos al contenedor ADLS `raw` antes de correr la ingesta.

### `proceso/` — pipeline principal (el que despliega el CI/CD)

| Archivo | Capa | Qué hace |
|---|---|---|
| `proceso/1.Preparacion_Ambiente.ipynb` | Infra | Crea external locations (`exlt-raw`, `exlt-bronze`, `exlt-silver`, `exlt-golden`, `exlt-metastore`), el catálogo `football_dev`, schemas y tablas Delta vacías. Widget: `storageName`. |
| `proceso/2.Ingest_leagues_data.ipynb` | Bronze | Lee `leagues.csv`, aplica schema y escribe `football_dev.bronze.leagues` con `ingestion_date`. |
| `proceso/2.Ingest_matches_data.ipynb` | Bronze | Lee `matches.csv` y escribe `football_dev.bronze.matches` particionado por `season_year`. |
| `proceso/2.Ingest_clubs.ipynb` | Bronze | Lee `clubs.json` (multiline) y escribe `football_dev.bronze.clubs`. |
| `proceso/3.Transform.ipynb` | Silver | Cruza las **3** tablas bronze. Filtra `season_year >= 2010`. Crea `result_type`, `goal_diff_category`, `match_intensity`, `is_classic`, `season_age`, `ht_result`, `is_comeback`, `second_half_goals` y totales de tiros, córners, faltas y tarjetas. Escribe `football_dev.silver.matches_transformed`. |
| `proceso/4.Load.ipynb` | Gold | Escribe `football_dev.gold.season_stats` (KPIs por temporada, país y liga) y `football_dev.gold.standings` (tabla de posiciones por temporada y liga, con funciones de ventana). |
| `proceso/5.Grants_Medallion.ipynb` | Seguridad | `GRANT` de catálogo, schema y `SELECT` sobre las tablas bronze, silver y gold. |
| `proceso/6.DeltaSharing.ipynb` | Consumo | Crea el share `FOOTBALL_SHARE` con `gold.season_stats` y `gold.standings` y el recipient que consume Power BI. |

Widgets comunes de ingesta: `container`, `catalogo`, `esquema`, `storageName`.  
Widgets de transform/load: `catalogo`, `esquema_source`, `esquema_sink`.

### `PrepAmb/` — copia de preparación

| Archivo | Qué es |
|---|---|
| `PrepAmb/1.- Preparacion_Ambiente.ipynb` | Misma lógica que `proceso/1.Preparacion_Ambiente.ipynb`. Se deja aparte, como en el proyecto F1, para correr la preparación de forma aislada. |

### `seguridad/` — laboratorio de permisos

| Archivo | Qué es |
|---|---|
| `seguridad/4. Grants-Medallion.ipynb` | Ejemplos más amplios: `GRANT`/`REVOKE`, `SHOW GRANTS`, external locations, grupo `data_engineers`. No forma parte del job `WF_FOOTBALL`. |

### `reversion/` — teardown

| Archivo | Qué es |
|---|---|
| `reversion/1. Drop-Medallion.ipynb` | Borra tablas y carpetas Delta de fútbol (`.../football/...`) y el catálogo `football_dev`. No toca `catalog_au` (F1). |

### `dashboard/`

| Archivo | Qué es |
|---|---|
| `dashboard/Fútbol Big Five - Resumen por Temporada.lvdash.json` | Dashboard de Databricks (AI/BI) sobre `gold.season_stats`. |
| `dashboard/dashboard.pbix` | Dashboard de Power BI conectado por Delta Sharing (`football_share.gold.season_stats`). |

### `.github/workflows/` — CI/CD

| Archivo | Qué es |
|---|---|
| `.github/workflows/deploy-notebook.yml` | Al hacer push a `main`: exporta los notebooks de `proceso/` desde el workspace origen, los importa a `/smartdata_football`, recrea el job `WF_FOOTBALL` en el cluster `cluster_SD`, lo ejecuta y lo monitorea. |

Secrets necesarios: `DATABRICKS_ORIGIN_HOST`, `DATABRICKS_ORIGIN_TOKEN`, `DATABRICKS_DEST_HOST`, `DATABRICKS_DEST_TOKEN`.

## Tablas que crea el pipeline

### Bronze

- `football_dev.bronze.leagues`
- `football_dev.bronze.matches` (particionada por `season_year`)
- `football_dev.bronze.clubs`

### Silver — `football_dev.silver.matches_transformed`

Columnas de negocio:

| Columna | Significado |
|---|---|
| `result_type` | `Local`, `Empate` o `Visitante` |
| `goal_diff_category` | `Ajustado` (0–1), `Normal` (2), `Goleada` (3+) |
| `match_intensity` | `Baja` (≤2 goles), `Media` (3–4), `Alta` (5+) |
| `is_classic` | `Clasico` o `Regular` (Madrid–Barça, United–Liverpool, Milan–Inter, etc.) |
| `season_age` | Años desde la temporada |
| `ht_result` | Resultado al descanso: `Local`, `Empate` o `Visitante` |
| `is_comeback` | `true` si el equipo que perdía al descanso ganó el partido |
| `second_half_goals` | Goles marcados en el segundo tiempo |
| `home_*` / `away_*` | Tiros, tiros a puerta, córners, faltas, amarillas y rojas por equipo |
| `total_shots`, `total_shots_on_target`, `total_corners`, `total_fouls`, `total_cards` | Totales del partido |

### Gold — `football_dev.gold.season_stats`

KPIs por temporada, país y liga: `conteo`, `total_goals`, `max_goals`, `min_goals`, `classic_count`, `home_win_count`, `away_win_count`, `draw_count`, `comeback_count`, `second_half_goals`, `total_shots`, `total_shots_on_target`, `total_corners`, `total_fouls`, `total_yellow_cards`, `total_red_cards`.

Con ellas se derivan precisión de tiro (`total_shots_on_target / total_shots`), conversión (`total_goals / total_shots_on_target`), tarjetas por partido y % de goles en el segundo tiempo.

### Gold — `football_dev.gold.standings`

Tabla de posiciones por temporada y liga (682 filas: 18 o 20 clubes por liga):

| Columna | Significado |
|---|---|
| `position` | Puesto final. Desempate: puntos, diferencia de goles, goles a favor y nombre |
| `played`, `wins`, `draws`, `losses` | Partidos jugados, ganados, empatados y perdidos |
| `goals_for`, `goals_against`, `goal_diff`, `points` | Goles a favor, en contra, diferencia y puntos (3 / 1 / 0) |
| `home_points`, `away_points` | Puntos de local y de visitante |
| `shots`, `shots_on_target`, `yellow_cards`, `red_cards` | Estadísticas acumuladas del club |
| `last5_form` | Últimos 5 resultados en orden cronológico, p. ej. `WWDLW` |
| `zone` | `Campeon`, `Champions League` (2.º–4.º), `Descenso` (últimos 3) o `Media tabla` |

El desempate es simplificado: algunas ligas usan enfrentamiento directo, y Ligue 1 2019/20 se cerró por promedio de puntos (temporada suspendida por COVID).

## Cómo ejecutarlo

1. Sube `datasets/leagues.csv`, `matches.csv` y `clubs.json` al contenedor `raw` de ADLS.
2. Importa la carpeta `proceso/` a Databricks.
3. Corre `1.Preparacion_Ambiente` y luego el resto, o deja que `WF_FOOTBALL` lo orqueste.
4. Consulta gold:

```sql
SELECT * FROM football_dev.gold.season_stats
ORDER BY season_year DESC, country;

SELECT season_year, league_name, club, points, last5_form
FROM football_dev.gold.standings
WHERE zone = 'Campeon'
ORDER BY season_year DESC, league_name;
```

## Equivalencia con el proyecto F1

| F1 (`CICDSMARTDATA3007`) | Fútbol (`smartdata_football`) |
|---|---|
| `catalog_au` | `football_dev` |
| `circuits` / `races` / `constructors` | `leagues` / `matches` / `clubs` |
| filtro `race_year > 1978` | filtro `season_year >= 2010` |
| `altitude_category`, `race_type`, `near_equator` | `goal_diff_category`, `result_type`, `match_intensity`, `is_classic` |
| `golden_raced_partitioned` | `season_stats` |
| job `WF_ADB` | job `WF_FOOTBALL` |
| `constructors` no se usaba en silver | las 3 fuentes sí se cruzan en silver |

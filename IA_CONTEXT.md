# Contexto del Proyecto para IA

## 1. Resumen ejecutivo

Este repositorio implementa una aplicacion de mantenimiento predictivo (PHM, Prognostics and Health Management) sobre el benchmark NASA C-MAPSS para motores turbofan.

Objetivo del sistema:
- recibir datos operativos y de sensores de un motor,
- estimar su Remaining Useful Life (RUL),
- convertir esa prediccion en riesgo y recomendaciones accionables,
- mostrar los resultados en un dashboard trazable y auditable.

La idea central del proyecto es que un buen sistema PHM no termina en un modelo predictivo. La arquitectura completa es:

`Predictive Layer -> Agent Layer -> Dashboard Layer`

Tambien hay una linea academica/documental asociada:
- paper final en `doc/paper/`
- presentaciones en `doc/ppt/`
- planes de trabajo en `plan1_eda.md` a `plan7_ppt.md`

## 2. Problema que resuelve

El proyecto usa datos de NASA C-MAPSS para estimar RUL de unidades turbofan a partir de:
- `dataset_id`
- `unit_id`
- `cycle`
- `op_setting_1..3`
- `sensor_1..21`

No se limita a predecir RUL. Tambien:
- calcula `risk_score` y `risk_level`,
- genera recomendaciones de mantenimiento,
- permite escenarios what-if,
- conserva trazabilidad tecnica y audit logs.

## 3. Arquitectura del sistema

### 3.1 Predictive Layer

Ubicacion principal: `src/predictive_layer/`

Responsabilidades:
- cargar y preparar datos,
- entrenar varios modelos de RUL,
- comparar modelos,
- seleccionar un champion,
- servir inferencia con banda de confianza calibrada.

Modelos implementados:
- `rf` = RandomForestRegressor
- `hgb` = HistGradientBoostingRegressor
- `lstm`
- `gru`

Estado actual del champion:
- archivo: `out/predictive_layer/champion_record.json`
- champion actual: `rf`
- fallback: `hgb`
- mejor RMSE bruto global: `gru`
- razon de seleccion: el sistema privilegia estabilidad e integracion, no solo el menor error bruto

Datos relevantes del champion record:
- `champion_model = rf`
- `fallback_model = hgb`
- `best_overall_model = gru`
- `selection_reason = "Best stable baseline selected for integration readiness."`

Archivos clave:
- `src/predictive_layer/run_plan3_predictive_layer.py`
- `src/predictive_layer/train_rf.py`
- `src/predictive_layer/train_hgb.py`
- `src/predictive_layer/train_lstm.py`
- `src/predictive_layer/train_gru_or_tcn.py`
- `src/predictive_layer/evaluate_models.py`
- `src/predictive_layer/inference_service.py`
- `src/predictive_layer/predict.py`
- `src/predictive_layer/calibration.py`

Artefactos importantes:
- modelos entrenados en `out/predictive_layer/models/`
- metricas y comparaciones en `out/predictive_layer/`
- predicciones validadas en archivos parquet del mismo directorio

### 3.2 Agent Layer

Ubicacion principal: `src/agent_layer/`

Responsabilidades:
- consumir la salida del predictive layer,
- calcular riesgo de forma deterministica,
- construir recomendaciones,
- ejecutar escenarios what-if,
- usar LLM solo de forma auxiliar y no central.

Punto importante del diseno:
- el LLM NO es la fuente de verdad para prediccion ni riesgo
- el nucleo de decision es deterministico y auditable
- el LLM puede ayudar a interpretar texto libre en escenarios y a mejorar redaccion de explicaciones

Flujo principal de decision:
1. validar payload
2. llamar al predictive layer
3. calcular `risk_score` y `risk_level`
4. construir recomendacion
5. guardar audit log

Archivo principal:
- `src/agent_layer/orchestrator.py`

Otros archivos clave:
- `src/agent_layer/risk_engine.py`
- `src/agent_layer/recommender.py`
- `src/agent_layer/scenario_rules.py`
- `src/agent_layer/scenario_interpreter.py`
- `src/agent_layer/llm_client.py`
- `src/agent_layer/tools.py`

Salidas del agent layer:
- `rul_pred`
- `confidence_band`
- `risk_level`
- `risk_score`
- `recommendation_text`
- `service_status`
- `trace`
- `audit_record_id`

Escenarios:
- entrada por texto tipo `cycle +25`, `sensor_11 -0.1`, `set op_setting_1 to 0.6`
- parser deterministico primero
- parser asistido por LLM solo si el deterministico falla y hay API key
- validacion deterministica obligatoria

Audit log:
- `out/agent_layer/audit_log.jsonl`

### 3.3 Dashboard Layer

Ubicacion principal: `src/dashboard_layer/`

Tecnologia:
- `Streamlit`

Archivo de entrada:
- `src/dashboard_layer/app.py`

Responsabilidades:
- capturar input manual o por CSV,
- ejecutar flujo de decision,
- visualizar resumen, analisis, escenarios y auditoria tecnica,
- mostrar historia temporal y contexto de flota cuando hay dataset disponible.

Tabs principales del dashboard:
- `Summary`
- `Analysis`
- `Scenarios`
- `Technical Audit`

Comportamientos importantes observados en `app.py`:
- soporta modo manual y modo file upload
- calcula historial reciente de RUL por unidad
- muestra interpretacion del estado del motor
- ejecuta escenarios y conserva detalles de parsing/validacion

Archivos clave:
- `src/dashboard_layer/app.py`
- `src/dashboard_layer/backend_adapter.py`
- `src/dashboard_layer/components.py`

## 4. Flujo de datos end-to-end

1. El usuario entrega un payload con datos de operacion y sensores.
2. El dashboard envia el payload al agent layer.
3. El agent layer reduce y adapta el payload al formato esperado por el predictive layer.
4. El predictive layer devuelve:
   - prediccion puntual de RUL
   - banda de confianza
   - estado del servicio
5. El agent layer calcula:
   - risk score
   - risk level
   - recomendacion
6. El dashboard presenta:
   - decision
   - explicacion
   - historial temporal
   - escenarios
   - trazabilidad tecnica

## 5. Estructura del repositorio

Directorios mas importantes:
- `data/`: datos C-MAPSS y ejemplos de entrada
- `src/eda/`: EDA y generacion de preprocessing
- `src/research/`: sintesis documental/metodologica
- `src/predictive_layer/`: entrenamiento, evaluacion, inferencia
- `src/agent_layer/`: riesgo, recomendaciones, escenarios, LLM auxiliar
- `src/dashboard_layer/`: app Streamlit
- `out/`: artefactos generados, contratos, metricas, auditoria
- `fig/`: figuras de EDA y del dashboard
- `doc/paper/`: paper academico y assets
- `doc/ppt/`: presentaciones y speaker notes

## 6. Archivos que explican mejor el proyecto

Si Gemini necesita entender el proyecto rapido, priorizar estos archivos:

1. `README.md`
2. `USER_GUIDE.md`
3. `src/dashboard_layer/app.py`
4. `src/agent_layer/orchestrator.py`
5. `src/predictive_layer/inference_service.py`
6. `src/predictive_layer/run_plan3_predictive_layer.py`
7. `out/predictive_layer/champion_record.json`
8. `plan6_academic_paper.md`
9. `doc/paper/main.tex`
10. `doc/ppt/02_slide_content_4m.md`

## 7. Como ejecutar el proyecto

Entorno Conda:

```powershell
conda env create -f environment.yml
conda activate cmapss
```

Lanzar dashboard:

```powershell
streamlit run src/dashboard_layer/app.py
```

Regenerar artefactos principales:

```powershell
conda run -n cmapss python src/eda/run_plan1_eda.py
conda run -n cmapss python src/research/run_plan2_research.py
conda run -n cmapss python -m src.agent_layer.run_plan4_agent_layer
conda run -n cmapss python -m src.dashboard_layer.run_plan5_dashboard_layer
```

Pipeline del predictive layer:

```powershell
conda run -n cmapss python -c "import os, runpy; os.environ['KMP_DUPLICATE_LIB_OK']='TRUE'; import torch; runpy.run_module('src.predictive_layer.run_plan3_predictive_layer', run_name='__main__')"
```

## 8. Dependencias y entorno

Archivo de entorno:
- `environment.yml`

Tecnologias visibles en el repo:
- Python
- Streamlit
- pandas
- plotly
- scikit-learn
- PyTorch
- joblib
- parquet artifacts

LLM opcional:
- el agent layer puede usar `GEMINI_API_KEY`
- el modelo por defecto mencionado en el codigo es `gemini-2.5-flash` como fallback de nombre en escenarios

Importante:
- aunque Gemini puede participar en parsing o explicacion, la logica deterministica sigue siendo la fuente de verdad

## 9. Convenciones y decisiones de diseno

Decisiones clave del proyecto:
- mejor modelo bruto no implica modelo desplegado
- el champion se elige por estabilidad e integracion
- la capa de agente es deterministic-first
- el dashboard prioriza trazabilidad y auditabilidad
- el sistema separa claramente:
  - prediccion
  - riesgo
  - recomendacion
  - visualizacion

## 10. Estado documental y academico

El proyecto no solo contiene codigo; tambien tiene una narrativa academica madura:

- planes:
  - `plan1_eda.md`
  - `plan2_research.md`
  - `plan3_predictive_layer.md`
  - `plan4_agent_layer.md`
  - `plan5_dashboard_layer.md`
  - `plan6_academic_paper.md`
  - `plan7_ppt.md`

- paper:
  - `doc/paper/main.tex`
  - `doc/paper/main.pdf`
  - figuras y tablas en `doc/paper/assets/`

- presentaciones:
  - `doc/ppt/final_presentation_v2.pptx`
  - `doc/ppt/final_presentation_4m.pptx`
  - `doc/ppt/speaker_notes_4m.md`

## 11. Limitaciones y advertencias para Gemini

Gemini no deberia asumir lo siguiente:
- que el mejor RMSE (`gru`) es el modelo desplegado
- que el LLM toma decisiones de riesgo
- que el dashboard es solo una visualizacion superficial
- que el proyecto termina en entrenamiento de modelos

Gemini deberia recordar:
- la arquitectura completa es de tres capas
- el proyecto prioriza auditabilidad e integracion real
- los artefactos en `out/` son parte esencial del sistema
- hay una capa academica y una capa de producto/demo

## 12. Tipos de consultas que Gemini puede responder bien con este contexto

Con este archivo, Gemini deberia poder ayudar en tareas como:
- explicar la arquitectura del proyecto
- resumir el paper o la presentacion
- proponer mejoras al dashboard
- revisar consistencia entre paper, codigo y PPT
- sugerir refactors
- ayudar a escribir documentacion tecnica
- generar prompts o listas de verificacion para nuevas iteraciones
- responder preguntas sobre flujo de datos, modelos y decisiones de diseno

## 13. Prompt sugerido para usar este archivo en Gemini

Puedes pasar este archivo a Gemini con una instruccion como esta:

```text
Este archivo resume el contexto de mi proyecto. Usalo como fuente principal para entender la arquitectura, los artefactos y las decisiones de diseno. Si necesitas profundizar, pide archivos concretos por ruta. No asumas que el mejor modelo por RMSE es el desplegado. No asumas que el LLM toma decisiones de riesgo. Prioriza respuestas alineadas con la arquitectura Predictive -> Agent -> Dashboard y con el enfoque de auditabilidad del proyecto.
```

## 14. Recomendacion practica

Este archivo sirve como contexto base. Si la consulta en Gemini es muy especifica, conviene adjuntar ademas:
- el archivo fuente relevante,
- 1 o 2 artefactos del directorio `out/` relacionados con esa parte,
- y, si aplica, el fragmento del paper o PPT correspondiente.

Por ejemplo:
- para preguntas de inferencia: adjuntar `src/predictive_layer/inference_service.py`
- para escenarios: adjuntar `src/agent_layer/orchestrator.py` y `src/agent_layer/scenario_rules.py`
- para dashboard: adjuntar `src/dashboard_layer/app.py`

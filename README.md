# Monitor COVID-19 en Uruguay — README de despliegue

Guía breve para **hostear** esta app Dash en **Render.com** (y correrla localmente) siguiendo el flujo del repo de referencia: *“dash-app-render-deployment”* de Thushara R. Bandara. https://github.com/thusharabandara/dash-app-render-deployment

> Tu script ya expone `server = app.server` → perfecto para producción con **Gunicorn** y para Render.

---

## 0) Prerequisitos
* Una cuenta en Render  https://render.com/.
* Una cuenta en github y un repositorio que contenga la app de Dash que quieren subir.

## 1) Requisitos

* **Python 3.10+** (recomendado 3.12)
* Cuenta en **GitHub** (código en un repo)
* Cuenta en **Render** (plan gratuito alcanza para empezar)
* Salida a Internet desde el host (la app descarga CSV y CSS remotos)

### Dependencias mínimas

Crea `requirements.txt` en la raíz del repo con algo como:

```
dash>=2.17
plotly>=5.22
pandas>=2.2
dash-bootstrap-components>=1.6
gunicorn>=22.0
```

> En Render podés no fijar versiones (excepto `dash`) si querés alinearte al repo de referencia; yo prefiero fijarlas levemente para reproducibilidad.

---

## 2) Estructura de archivos

```
project/
├─ app.py               # el script que pegaste
├─ requirements.txt
└─ (opcional) README.md
```

Si tu archivo no se llama `app.py`, ajustá los comandos `app:server` → `<archivo>:server`.

---

## 3) Correr localmente (desarrollo)

```bash
python -m venv .venv
source .venv/bin/activate    # En Windows también podés usar: .venv/Scripts/activate
pip install -r requirements.txt
python app.py                 # corre en http://127.0.0.1:8050
```

> Para debug local podés usar `app.run(debug=True)`. En producción usaremos Gunicorn (Render lo lanza por nosotros).

---

## 4) Desplegar en Render

1. Subí el código a **GitHub** (repo público o privado con acceso a Render).

2. En **Render Dashboard** creá **New → Web Service** y conectá el repo.

3. Configurá:

* **Environment**: Python
* **Start Command**:

  ```
  gunicorn app:server
  ```

  (si tu archivo es `main.py` entonces `gunicorn main:server`).
* **Region**, **Branch**: las que prefieras.
* (Opcional) **Env Var** `PYTHON_VERSION=3.12.4` para fijar la versión de Python.

4. Hacé clic en **Create Web Service**. Render instalará dependencias desde `requirements.txt`, construirá y levantará la app. Al terminar, tendrás una **URL pública**.

5. Cada push a la rama configurada dispara un **auto-deploy**.

---

## 5) Producción con Gunicorn (opcional fuera de Render)

Si querés correrla en un servidor propio:

```bash
pip install -r requirements.txt
gunicorn --bind 0.0.0.0:8050 --workers 2 app:server
```

* Ajustá `--workers` según CPU (2–4 suele estar bien). Para exponerla en internet, ponela detrás de Nginx/Caddy con TLS.

---

## 6) Buenas prácticas

* No usar `debug=True` en producción.
* Revisá que **todas** las libs usadas estén en `requirements.txt`.
* La app descarga datos y CSS remotos: asegurá **conectividad saliente**.
* Si querés fijar pandas/plotly por compatibilidad, hacelo en `requirements.txt` y redeploy.

---

## 7) Troubleshooting

**❌  ModuleNotFoundError** al desplegar
Falta la lib en `requirements.txt`. Agregala y hacé *New Deploy*.

**❌  Error al iniciar: `ModuleNotFoundError: app` o 404**
El Start Command debe apuntar al archivo correcto: `gunicorn <archivo>:server`.

**❌  Timeout o datos vacíos**
Las URLs de datos pueden estar caídas o lentas. Verificá que estén accesibles desde el servidor.

**❌  `server` no encontrado**
Asegurate de tener `server = app.server` (tu script ya lo incluye).

---

## 8) Checklist rápido

* [ ] `requirements.txt` creado y subido
* [ ] `server = app.server` en el código (✅)
* [ ] Start Command en Render: `gunicorn app:server`
* [ ] (Opcional) `PYTHON_VERSION` seteado
* [ ] Deploy exitoso y URL pública funcionando

---

## 9) Referencias

* Repo guía (Render) — pasos y `Start Command` con Gunicorn.: https://github.com/thusharabandara/dash-app-render-deployment
* Doc oficial de Dash — sección de despliegue con Gunicorn/Procfile.

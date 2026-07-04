# Hugging Face Space deployment

The backend runs as a Docker Space: **https://huggingface.co/spaces/Gabriel-Matos13/rain-predictor**

A Space is its own git repo and needs a `Dockerfile` and a `README.md` (with HF
config frontmatter) at its **root** — unlike this project, where the Dockerfile
lives under `api/`. The two files in this folder are exactly those root files.

## Space layout

The Space contains this project's `api/`, `model/`, and `data/` folders unchanged
(so the relative paths in `model_service.py` resolve identically), plus:

```
(space root)/
├── README.md      # HF frontmatter: sdk=docker, app_port=7860   (this folder)
├── Dockerfile     # root build; COPY paths are project-root-relative (this folder)
├── api/           # main.py, schemas.py, weather.py, model_service.py, requirements.txt
├── model/         # model.pkl, feature_config.json
└── data/          # santo_domingo_historical.csv
```

## Redeploy

With the `hf` CLI (`pip install huggingface_hub`) authenticated via `hf auth login`:

```bash
# assemble a staging folder = these two files + api/ model/ data/
hf upload Gabriel-Matos13/rain-predictor <staging-folder> . --repo-type space
```

HF rebuilds the image automatically on every push. The API is then reachable at
`https://gabriel-matos13-rain-predictor.hf.space` (e.g. `/health`, `/predict`, `/docs`).

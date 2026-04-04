# Code Debug Environment — Full File Structure

```
code-debug-env/
├── openenv.yaml                  ← OpenEnv manifest (required)
├── inference.py                  ← Baseline agent script (must be in root)
├── pyproject.toml                ← Dependencies
├── README.md                     ← Docs with action/obs spaces
├── .dockerignore
├── models.py                     ← Pydantic Action/Observation/State
├── client.py                     ← EnvClient (for training code)
├── __init__.py                   ← Exports
└── server/
    ├── __init__.py
    ├── app.py                    ← FastAPI server
    ├── environment.py            ← Core logic: reset/step/state
    ├── tasks/
    │   ├── __init__.py
    │   ├── task_easy.py          ← 15 buggy code samples
    │   ├── task_medium.py        ← 15 buggy code samples
    │   └── task_hard.py          ← 15 buggy code samples
    ├── graders/
    │   ├── __init__.py
    │   ├── grader_easy.py
    │   ├── grader_medium.py
    │   └── grader_hard.py
    ├── requirements.txt
    └── Dockerfile
```

# Job Ingestion and Search System

Ingests job postings from heterogeneous JSON feeds, normalizes them into a common internal representation, evaluates them against publication criteria, and exposes the approved set through a searchable UI.

Rejected postings are not discarded: they are logged with structured rejection reasons and surfaced in the UI alongside approved ones, because the reasons a feed fails are the most useful artifact when diagnosing feed quality.

## Stack


| Layer    | Choice                                  | Why                                                            |
| -------- | --------------------------------------- | -------------------------------------------------------------- |
| Backend  | Python 3.12, FastAPI, Pydantic v2       | Typed models with runtime validation at the ingestion boundary |
| Frontend | React 19, TypeScript, Vite              | Required by the brief; Vite for fast iteration                 |
| Tooling  | uv, ruff, mypy (strict), pytest, vitest | Type checking enforced from the first commit, not retrofitted  |
| Runtime  | Docker Compose                          | One command to run the whole system                            |


## Quick start

```bash
make up

```

- API: [http://localhost:8000](http://localhost:8000)
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- UI: [http://localhost:5173](http://localhost:5173)

Stop with `make down`.

The feed is read from `data/jobs.json`, mounted read-only into the backend container. The path is configurable via the `JOBS_FEED_PATH` environment variable.

## Local development without Docker

Backend:

```bash
cd backend
uv sync
uv run uvicorn jobs.api.main:app --reload

```

`uv` provisions Python 3.12 itself — no system Python version is required or modified.

Frontend:

```bash
cd frontend
npm install
npm run dev

```

The dev server proxies `/api` to the backend, so the frontend never holds a backend URL. No CORS configuration is needed in either environment.

## Testing

```bash
make test      # backend (pytest) + frontend (vitest)
make lint      # ruff, mypy strict, tsc

```

Backend tests are organized per architectural layer: adapters, normalization, each approval rule, the rule engine, storage, and API. A single parametrized acceptance test runs the full sample feed against a hand-derived expectations table (`tests/fixtures/expected_[decisions.py](http://decisions.py)`).

That table was written before the implementation, from the criteria in the brief, and is not generated from running code. When implementation and table disagree, the first question is which of the two is wrong.

## Project structure

```
backend/src/jobs/
├── models/          # RawJob, CanonicalJob, Decision, enums
├── ingestion/       # feed loading
│   └── adapters/    # one adapter per feed shape
├── normalization/   # location, salary, currency conversion
├── approval/        # rule engine
│   └── rules/       # one file per approval criterion
├── storage/         # job repository, rejection log
├── api/             # FastAPI application and routes
└── config/          # rule set, thresholds, exchange rates

frontend/src/
├── api/             # typed API client
├── components/      # table, filters, tabs
├── hooks/           # data fetching and query state
└── types/           # shared types

data/jobs.json       # sample feed (committed — the system needs it to run)

```

## Docker: development vs production

The images in this repository are **development images**. They mount source directories as volumes and run hot-reloading dev servers — Uvicorn with `--reload`, Vite in dev mode. This is deliberate: it makes the system inspectable while working on it, and it is what `make up` gives a reviewer.

They are explicitly not production images. A production setup would differ in several ways:

- **Frontend**: multi-stage build producing a static bundle served by nginx, rather than the Vite dev server. The dev server is unoptimized, single-process, and not intended to face traffic.
- **Backend**: Uvicorn without `--reload`, behind a process manager, with worker count tuned to the host.
- **Source**: copied into the image at build time rather than bind-mounted, so the image is a self-contained, reproducible artifact.
- **Feed ingestion**: currently runs at application startup against a local file. In production this would be a scheduled or event-driven job writing to a persistent store, decoupled from the API process lifecycle.
- **Storage**: the repository is an in-memory implementation behind a protocol. Swapping in a database implementation requires no changes to the pipeline, the rules, or the API layer.

The distinction is called out rather than papered over: the brief asks for production-ready *structure and design*, and mocked infrastructure is explicitly permitted. The seams where real infrastructure would attach are protocols, not concrete classes.

## Design notes

See [`DECISIONS.md`](http://DECISIONS.md) for the interpretation choices made while implementing the approval criteria — including how remote postings outside the US and Canada are treated, how salaries with missing units or currencies are resolved, and why hourly rates are not converted to annual figures for the purpose of threshold checks.
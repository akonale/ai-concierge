## Start everything for dev
- Copy backend/env.example to .env
- Copy frontnd/env.exaple to .env.local

```shell
docker-compose up -d
```
And open http://localhost:3000

## Start one at a time

### Start vector db

```shell
docker run -v ./chroma-data:/data -p 8000:8000 chromadb/chroma
```

### Start backend
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

### Start frontend

```bash
cd frontend
npm run dev
```

### Browser
localhost:3000


## Production

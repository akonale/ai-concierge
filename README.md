## Start backend

```shell
docker run -v ./chroma-data:/data -p 5000:5000 chromadb/chroma
```

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## Start frontend

```bash
cd frontend
npm run dev
```
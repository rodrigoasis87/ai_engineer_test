from fastapi import FastAPI
from app.routers import rag_router, agent_router, react_router

app = FastAPI(title="AI Engineer Test API", version="1.0.0")

# Registrar routers
app.include_router(rag_router.router)
app.include_router(agent_router.router)
app.include_router(react_router.router)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
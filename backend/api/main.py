from fastapi import FastAPI
from .routers.games import router

app = FastAPI(title='Belote', version='0.1.0')

@app.get('/health')
def health():
    return {'status': 'ok'}

app.include_router(router)
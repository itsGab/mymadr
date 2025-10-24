from fastapi import FastAPI

from mymadr.routers import contas, livros, romancistas

app = FastAPI()

app.include_router(romancistas.router)
app.include_router(livros.router)
app.include_router(contas.router)


@app.get('/')
def read_root():
    return {'message': 'Hello there!'}

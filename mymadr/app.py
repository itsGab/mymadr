from fastapi import FastAPI

from mymadr.routers import contas, livros, romancistas

# TODO definir se vai usar!
tags_metadata = [
    {
        "name": "user",
        "description": "Usuarios"
    },
    {
        "name": "auth",
        "description": "Autorizacoes!!!"
    }
]


app = FastAPI(openapi_tags=tags_metadata)

app.include_router(romancistas.router)
app.include_router(livros.router)
app.include_router(contas.router)


@app.get("/")
def read_root():
    return {"message": "Hello there!"}

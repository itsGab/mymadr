from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from mymadr.routers import contas, livros, romancistas

""" TODO revisar código

Revisar todo o código para ver o que vale a pena ou nao fazer um relatório
sobre.

e.g.:
- @app.exception_handler -> para se adequar a `response` esperada.

"""

# TODO definir se vai usar!
tags_metadata = [
    {"name": "user", "description": "Usuarios"},
    {"name": "auth", "description": "Autorizacoes!!!"},
]


app = FastAPI(openapi_tags=tags_metadata)

app.include_router(romancistas.router)
app.include_router(livros.router)
app.include_router(contas.router)


@app.get("/")
def read_root():
    return {"message": "Hello there!"}


@app.exception_handler(HTTPException)
def message_http_exception_handler(request: Request, exc: HTTPException):
    """Função para mudar o `detail` do http exception para `message`,
    se encaixando no formato de saída esperado, Message, do schemas."""
    return JSONResponse(
        status_code=exc.status_code,
        content={'message': exc.detail},
        headers=getattr(exc, "headers", None)
    )

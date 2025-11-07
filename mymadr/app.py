from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from mymadr.routers import accounts, books, novelist

""" TODO revisar código

Revisar todo o código para ver o que vale a pena ou nao fazer um relatório
sobre.

e.g.:
- @app.exception_handler -> para se adequar a `response` esperada.

"""

# TODO definir se vai usar!
tags_metadata = [
    {"name": "conta", "description": "Gerenciamento de contas"},
    {"name": "romancista", "description": "Gerenciamento de romancistas"},
    {"name": "livro", "description": "Gerenciamento de livros"},
    {"name": "auth", "description": "Autorizações"},
]


app = FastAPI(openapi_tags=tags_metadata)

app.include_router(novelist.router)
app.include_router(books.router)
app.include_router(accounts.router)


@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Hello there!"}


@app.exception_handler(HTTPException)
def message_http_exception_handler(request: Request, exc: HTTPException):
    """Função para mudar o `detail` do http exception para `message`,
    se encaixando no formato de saída esperado, Message, do schemas."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
        headers=getattr(exc, "headers", None),
    )

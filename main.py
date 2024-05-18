from fastapi import FastAPI, Request
from pydantic import BaseModel
import ply.lex as lex
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permitir CORS para el frontend en React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# List of token names
tokens = [
    'ID', 'PLUS', 'EQUAL', 'ACENTO', 'ERROR',
    'OPEN_PAREN', 'CLOSE_PAREN', 'OPEN_BRACE', 'CLOSE_BRACE', 'COMMA', 'SEMICOLON'
]

# Reserved words
reserved = {
    'int': 'INT', 'suma': 'SUMA', 'read': 'READ', 'printf': 'PRINTF',
    'programa': 'PROGRAMA', 'end': 'END'
}
allowed_ids = {'a', 'b', 'c', 'la', 'es'}

tokens = tokens + list(reserved.values())

t_PLUS = r'\+'
t_EQUAL = r'='
t_OPEN_PAREN = r'\('
t_CLOSE_PAREN = r'\)'
t_OPEN_BRACE = r'\{'
t_CLOSE_BRACE = r'\}'
t_COMMA = r','
t_SEMICOLON = r';'
t_ACENTO = r'"'
t_ignore = ' \t\n\r'


def t_id(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.value = t.value.lower()
    if t.value in reserved:
        t.type = reserved[t.value]
    elif t.value in allowed_ids:
        t.type = 'ID'
    else:
        t.type = 'ERROR'
    return t


def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.type = 'ERROR'
    t.value = t.value[0]
    t.lexer.skip(1)
    return t


class CodeInput(BaseModel):
    code: str


@app.post("/analyze/")
async def analyze_code(input: CodeInput):
    counters = {tok: 0 for tok in tokens}
    counters.update({val: 0 for val in reserved.values()})
    token_data = []
    lexical_errors = []

    lexer = lex.lex()
    lexer.input(input.code)

    while True:
        tok = lexer.token()
        if not tok:
            break
        entry = {'token': tok.value, 'PR': '', 'ID': '', 'SIM': '', 'ERROR': ''}
        if tok.type in reserved.values():
            entry['PR'] = 'X'
        elif tok.type == 'ID':
            entry['ID'] = 'X'
        elif tok.type == 'ERROR':
            entry['ERROR'] = 'X'
            lexical_errors.append(f"Error Lexico: '{tok.value}'")
        else:
            entry['SIM'] = 'X'
        counters[tok.type] += 1
        token_data.append(entry)

    total_reserved = sum(counters[val] for val in reserved.values())
    total_errors = counters['ERROR'] if 'ERROR' in counters else 0

    return {
        "token_data": token_data,
        "counters": counters,
        "total_reserved": total_reserved,
        "lexical_errors": lexical_errors,
        "total_errors": total_errors,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

"""Laboratório educacional executável SOMENTE em localhost."""
import hashlib
import secrets
import sqlite3
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI(title="VulnLab API", description="Laboratório local de BOLA/IDOR")
security = HTTPBearer()
# Demonstração: em memória, sem persistência nem contas reais.
DB = sqlite3.connect(":memory:", check_same_thread=False)
DB.row_factory = sqlite3.Row
DB.executescript("""
CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT);
CREATE TABLE invoices(id INTEGER PRIMARY KEY, owner_id INTEGER, description TEXT, amount REAL);
""")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()  # Apenas para ambiente didático local!

DB.executemany("INSERT INTO users VALUES (?,?,?)", [(1,"alice",hash_password("alice123")),(2,"bob",hash_password("bob123"))])
DB.executemany("INSERT INTO invoices VALUES (?,?,?,?)", [(1,1,"Livro",42.0),(2,2,"Notebook",400.0)])
DB.commit()
TOKENS = {}

@app.post("/login")
def login(username: str, password: str):
    user = DB.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not user or not secrets.compare_digest(user["password_hash"], hash_password(password)):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = secrets.token_urlsafe(32)
    TOKENS[token] = user["id"]
    return {"access_token": token, "token_type": "bearer"}

def get_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    user_id = TOKENS.get(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token inválido")
    return user_id

def get_invoice(invoice_id):
    invoice = DB.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Não encontrada")
    return dict(invoice)

@app.get("/lab/invoices/{invoice_id}")
def vulnerable_invoice(invoice_id: int, current_user: int = Depends(get_user)):
    # INTENCIONALMENTE VULNERÁVEL: autentica, mas NÃO verifica owner_id.
    return get_invoice(invoice_id)

@app.get("/secure/invoices/{invoice_id}")
def secure_invoice(invoice_id: int, current_user: int = Depends(get_user)):
    invoice = get_invoice(invoice_id)
    if invoice["owner_id"] != current_user:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return invoice

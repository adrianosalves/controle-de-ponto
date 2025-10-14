# main.py
from db.database import init_db
from app import app

# Inicializa o banco antes de rodar
init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
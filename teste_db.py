from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

def test_connection():
    try:
        load_dotenv()
        # Pega a URL diretamente da variável de ambiente
        database_url = os.environ.get('DATABASE_URL')
        
        # Se não encontrar no .env, usa a URL diretamente
        if not database_url:
            database_url = "postgresql://fullstock_user:B2Yky7kpkarVvcgopLy22bU6dAnYqsol@dpg-d7an5s2dbo4c73dvibg0-a.virginia-postgres.render.com/fullstock_7sa1"
        
        # Corrige o formato para SQLAlchemy
        if database_url and database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        print(f"Conectando ao banco: {database_url.replace('B2Yky7kpkarVvcgopLy22bU6dAnYqsol', '****')}")
        
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Conexão bem sucedida!")
            print(f"Versão PostgreSQL: {conn.execute(text('SELECT version()')).fetchone()[0]}")
        return True
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

if __name__ == "__main__":
    test_connection()
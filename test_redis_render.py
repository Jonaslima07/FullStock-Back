import redis
import os
from dotenv import load_dotenv

load_dotenv()

# Testar com Redis do Render
redis_url = os.getenv("REDIS_URL", "redis://red-d7b8ouggjchc739324j0:6379")

print(f"Testando conexão com: {redis_url}")

try:
    r = redis.from_url(redis_url)
    r.ping()
    print("✅ Conexão com Redis estabelecida com sucesso!")
    
    # Testar operações básicas
    r.set("teste", "FullStock funcionando!")
    valor = r.get("teste")
    print(f"✅ Teste de leitura/escrita: {valor.decode('utf-8')}")
    
    # Limpar teste
    r.delete("teste")
    print("✅ Todos os testes passaram!")
    
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
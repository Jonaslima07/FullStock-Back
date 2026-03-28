from locust import HttpUser, task, between

class UsuarioTeste(HttpUser):
    host = "http://localhost:5000"
    wait_time = between(1, 3)

    def on_start(self):
        

        response = self.client.post("/usuarios/login", json={
            "email": "jonaslima23122003@gmail.com",
            "senha": "mundoBike123"
        })

        print("STATUS LOGIN:", response.status_code)

        if response.status_code == 200:
            try:
                data = response.json()
                self.token = data.get("access_token")

                if not self.token:
                    print("❌ Token não encontrado!")
            except Exception as e:
                print("❌ Erro JSON:", e)
                self.token = None
        else:
            print(f"❌ Falha no login: {response.status_code}")
            self.token = None

        # ⚠️ NÃO zerar o token aqui!
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    @task(3)
    def listar_produtos(self):
        if not self.token:
            return

        response = self.client.get("/produtos", headers=self.headers)

        if response.status_code != 200:
            print("Erro listar:", response.status_code, response.text)

    @task(1)
    def criar_produto(self):
        if not self.token:
            return

        response = self.client.post(
            "/produtos",
            json={
                "nome": "Produto Teste",
                "categoria": "Alimento",
                "marca": "Marca Teste",
                "quantidade": 10,
                "preco": 5.5,
                "data_validade": "2026-12-31",
                "unidade": "UN"
            },
            headers=self.headers
        )

        if response.status_code not in [200, 201]:
            print("Erro criar:", response.status_code, response.text)
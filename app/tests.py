from django.test import TestCase

from .models import Produto


class EstoqueTests(TestCase):
    def test_cadastro_e_atualizacao(self):
        self.assertContains(self.client.get("/"), "Grupo 03")
        resposta = self.client.post("/", {"nome": "Café", "quantidade": 10})
        self.assertRedirects(resposta, "/")
        for _ in range(2):
            pagina = self.client.get(resposta.url)
            self.assertContains(pagina, "<td>Café</td><td>10</td>")
        self.assertEqual(list(Produto.objects.values_list("nome", "quantidade")), [("Café", 10)])

    def test_dados_invalidos(self):
        for nome, qtd, campo in [("", 1, "nome"), ("   ", 1, "nome"), ("Café", -1, "quantidade"),
                                  ("Café", "1.5", "quantidade")]:
            with self.subTest(nome=nome, quantidade=qtd):
                resposta = self.client.post("/", {"nome": nome, "quantidade": qtd})
                self.assertIn(campo, resposta.context["form"].errors)
                self.assertFalse(Produto.objects.exists())

    def test_zero(self):
        self.client.post("/", {"nome": "Arroz", "quantidade": 0})
        self.assertEqual(Produto.objects.get().quantidade, 0)

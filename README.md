# Gerenciador de Estoque · Grupo 03

## Executar no Windows

Use Docker Desktop em execução com contêineres Linux e Docker Compose. O Django também roda no Compose. O Python e o venv do Windows são opcionais para esse modo de execução.

No PowerShell, prepare a configuração na primeira execução:

```powershell
cd D:\Dev\Gerenciador-de-Estoque
docker compose version
if (!(Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

Preencha as três variáveis com valores distintos, longos e aleatórios (letras e números). Salve o arquivo. O MySQL cria as contas e os bancos na primeira inicialização do volume. Alterar o arquivo posteriormente exige atualizar também as senhas no banco.

```powershell
docker compose up -d --build
docker compose ps
docker compose logs estoque
Start-Process http://localhost:8003
Start-Process http://localhost:9003
```

O primeiro build precisa de internet. O Django aguarda o MySQL, aplica as migrações e inicia o servidor de desenvolvimento. No WordPress, conclua o instalador web para criar as tabelas e a conta do blog. Para interromper mantendo os dados, execute `docker compose down`. Para voltar, execute `docker compose up -d`. Após editar o Python ou o HTML, repita o comando com `--build`.

## Acessos

| Serviço | Teste no próprio Windows | Cliente Windows com a VM configurada |
| --- | --- | --- |
| Estoque | http://localhost:8003 | http://estoque.local:8003 |
| WordPress | http://localhost:9003 | http://blog.estoque.local:9003 |
| MySQL no DBeaver | 127.0.0.1, porta 3303 | estoque.local, porta 3303 |

Na VM Linux, crie o .env e execute o mesmo comando Compose na pasta do projeto. Os nomes do grupo dependem de resolução no cliente para o IP real da VM na rede 192.168.13.0/24. A porta 9003 encaminha para a 80 do WordPress e a 3303 para a 3306 do MySQL. Dentro da rede Docker, Django e WordPress acessam mysql:3306. Ao fazer uma instalação nova do blog na VM, abra o instalador pelo domínio definitivo. Se reutilizar o volume instalado via localhost, atualize os dois endereços em Configurações → Geral do WordPress ao trocar de domínio.

## Conferir o cadastro no DBeaver

1. Abra o estoque, cadastre **Café** com quantidade **10** e anote o ID da linha. Atualize a página.
2. No DBeaver, crie uma conexão MySQL com o host e porta da tabela acima. Use o usuário `grupo03`, a senha de `MYSQL_PASSWORD` e o banco `estoque`.
3. No editor SQL, consulte o registro usando o ID da tela. Substitua 1 pelo ID anotado:

```sql
SELECT id, nome, quantidade FROM estoque.produto WHERE id = 1;
SELECT id, nome, quantidade FROM estoque.produto ORDER BY id DESC;
```

4. Compare a listagem antes e depois de atualizar. Cadastros enviados separadamente podem ter o mesmo nome. Para conferir o blog, abra outra conexão com os mesmos dados e banco `wordpress`. Execute `SHOW TABLES;` depois de finalizar o instalador.

## Explicar na apresentação

O GET em / chega à view estoque (app/views.py) pela rota de projeto/urls.py. A view consulta Produto e renderiza o formulário e a lista. Ao clicar em Cadastrar, o navegador envia nome, quantidade e token CSRF em um POST para /. O Django verifica o token e a view passa os campos para ProdutoForm. Se os dados forem inválidos, ela mostra os erros. Se forem válidos, form.save() usa o ORM para inserir uma linha em estoque.produto. A resposta 302 redireciona o navegador para um GET, que consulta o banco e mostra a lista atualizada. Pressionar F5 repete esse último GET.

A migração app/migrations/0001_initial.py cria a tabela automaticamente. O arquivo sql/criar_tabela.sql é o equivalente para anexar ao relatório. Executá-lo manualmente antes da migração causaria conflito. O script sql/inicializar.sql, usado pelo contêiner MySQL na criação do volume, prepara o segundo banco e a permissão do usuário. Os volumes mysql_data e wordpress_data guardam os dados entre reinicializações.

Para conferir o Django e obter o SQL gerado pelo próprio backend MySQL:

```powershell
docker compose exec estoque python manage.py check
docker compose exec estoque python manage.py sqlmigrate app 0001
```

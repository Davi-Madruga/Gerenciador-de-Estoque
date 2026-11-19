# Do notebook vazio ao estoque funcionando na VM

**Objetivo do Grupo 3:** abrir o estoque no navegador do Windows, cadastrar um produto e conferir que o MySQL dentro do Debian guardou os dados. O mesmo servidor também hospeda o WordPress.

## Antes de começar: em qual computador estou?

| O que aparece na tela | Onde você está | O que fazer ali |
|---|---|---|
| Menu Iniciar, navegador ou terminal com `PS C:\...>` | Windows do notebook, o **cliente** | Abrir o VirtualBox, testar os sites e capturar a rede |
| Lista de máquinas no VirtualBox | Gerenciador da VM | Criar a máquina, conectar placas de rede e ligar ou desligar |
| Janela preta com `davi@servidor-estoque:~$` | Debian dentro da VM, o **servidor** | Clonar o projeto e executar Docker |

A VM tem disco, memória e placas de rede virtuais. A ISO é o instalador do Debian. O arquivo de disco criado pelo VirtualBox guarda o sistema, o repositório e os dados entre sessões. Depois da primeira instalação você apenas liga a VM. **Os prefixos acima servem para reconhecer a tela. Digite apenas os comandos dos blocos.**

## 1. Windows · Baixar as ferramentas

1. Instale o [VirtualBox para Windows hosts](https://www.virtualbox.org/wiki/Downloads).
2. Baixe a [ISO Debian 13 netinst para PC de 64 bits](https://www.debian.org/distrib/netinst). Escolha **amd64** para notebook Intel ou AMD de 64 bits. Deixe o arquivo .iso em Downloads.
3. Para os testes do trabalho, instale [Wireshark para Windows](https://www.wireshark.org/download.html) com o Npcap oferecido pelo instalador e [DBeaver Community](https://dbeaver.io/download/) para visualizar os bancos.

## 2. VirtualBox · Criar a VM e instalar o Debian

1. Clique em **Novo**. Nome: **Servidor-Estoque**. Em **Imagem ISO**, selecione o arquivo baixado. Escolha instalação manual (marque **Pular instalação desassistida**, se essa for a opção exibida).
2. Para reproduzir o teste do PC, use **2048 MB de RAM, 1 processador e 20 GB de disco virtual**, com alocação dinâmica. Mantenha o adaptador 1 em **NAT**. Ele permite que o Debian baixe programas pela internet.
3. Clique em **Finalizar → Iniciar**. No menu Debian, escolha **Graphical install**. Selecione idioma, país e teclado.
4. Nome da máquina: **servidor-estoque**. Domínio: deixe vazio. Deixe a senha de root vazia, crie o usuário **davi** e escolha sua senha. Esse usuário poderá administrar a VM com sudo.
5. Em **Particionar discos**, escolha **Assistido → usar o disco inteiro**. Confirme que é o **VBOX HARDDISK de aproximadamente 21,5 GB**. Escolha **Todos os arquivos em uma partição**. No resumo, procure **ext4 /**. Finalize e confirme a escrita nesse disco virtual.
6. Mídia adicional: **Não**. Espelho: **deb.debian.org**. Em uma rede doméstica comum, deixe o proxy vazio.
7. Em **Seleção de software**, marque **servidor SSH** e **utilitários de sistema padrão**. Desmarque a área de trabalho e o GNOME. O SSH permitirá colar comandos pelo terminal do Windows.
8. Instale o **GRUB** em **/dev/sda (VBOX HARDDISK)**. Conclua e reinicie. Se voltar ao instalador, ejete a ISO em **Dispositivos → Discos ópticos** e reinicie a VM.
9. Entre como **davi**. A senha fica invisível enquanto você digita. Ao aparecer `davi@servidor-estoque:~$`, o Debian está pronto. Execute `sudo poweroff` para desligá-lo antes do próximo passo.

## 3. VirtualBox · Criar a rede entre o notebook e a VM

O grupo deve usar **192.168.13.0/24**. Vamos dar ao Windows o endereço **192.168.13.1** e ao Debian o **192.168.13.10**. A segunda placa cria uma rede privada entre eles. A primeira continua dando internet ao Debian.

1. No gerenciador do VirtualBox, abra **Ferramentas → Rede** (Gerenciador de redes). Em **Redes exclusivas de hospedeiro / Host-only**, crie uma rede dedicada.
2. Selecione a rede Host-only criada e abra **Propriedades → Adaptador → Configurar adaptador manualmente**. Em **Endereço IPv4**, digite **192.168.13.1**. Em **Máscara de rede IPv4**, digite **255.255.255.0**. Clique em **Aplicar**. Esse é o endereço do **Windows** na rede virtual. Faça essa alteração apenas no adaptador Host-only. Desative o DHCP dessa rede e anote o nome do adaptador.
3. No **PowerShell do Windows**, execute `Get-NetIPAddress -IPAddress 192.168.13.1 -AddressFamily IPv4`. Confira se aparecem o IP **192.168.13.1** e **PrefixLength 24**. Se o Windows não encontrar o endereço, volte às propriedades e confira se clicou em **Aplicar**.
4. Selecione a VM desligada → **Configurações → Rede → Adaptador 2**. Habilite-o, escolha **Adaptador exclusivo de hospedeiro**, selecione o mesmo nome anotado e marque **Cabo conectado**. Ligue a VM e entre no Debian.

## 4. Debian · Dar um IP fixo à segunda placa

Na janela preta da VM, execute:

```bash
ip -br link
ip route
```

A interface da linha **default** é a placa NAT. A outra interface Ethernet é a Host-only. Ignore **lo**. A seguir usamos **enp0s8** como exemplo. Se sua segunda placa tiver outro nome, use o nome que apareceu.

No Debian mínimo instalado acima, confira se `cat /etc/network/interfaces` inclui a pasta **interfaces.d**. Crie a configuração da segunda placa:

```bash
sudo nano /etc/network/interfaces.d/estoque
```

Dentro do editor, digite estas três linhas:

```text
auto enp0s8
iface enp0s8 inet static
    address 192.168.13.10/24
```

Salve com **Ctrl+O**, **Enter**, **Ctrl+X**. Ative e confira:

```bash
sudo ifup enp0s8
ip -br addr
```

**Confira:** a segunda placa deve exibir **192.168.13.10/24**.

### Ainda no Debian · Preparar o servidor SSH

Na janela da VM no VirtualBox, execute um comando por vez:

1. Instale o servidor SSH: `sudo apt install -y openssh-server`
2. Inicie o serviço e configure-o para iniciar sempre que a VM ligar: `sudo systemctl enable --now ssh`
3. Confira o estado do serviço: `systemctl is-active ssh`

Quando aparecer **active**, siga para o PowerShell do Windows. O Debian está pronto para receber a conexão SSH na porta TCP **22**.

## 5. Windows · Entrar no Debian pelo PowerShell

Abra o **PowerShell no Windows** e execute:

```powershell
ping 192.168.13.10
ssh davi@192.168.13.10
```

Na primeira conexão, digite **yes** e informe a senha de davi. Quando o prompt mudar de `PS C:\...>` para `davi@servidor-estoque:~$`, você estará operando o **Debian** nessa mesma janela. Mantenha-a aberta para os próximos três passos. Assim você pode colar os comandos pelo Windows.

## 6. Debian via SSH · Instalar Git e Docker

Em uma VM nova, instale o Docker **dentro do Debian**. O comando `apt install` abaixo baixa e instala o Docker, o Compose e as ferramentas do projeto. Você pode pular a instalação do Docker Desktop e do WSL no Windows. Se importou a VM pronta, confira com `sudo docker ps` e `sudo docker compose version`. Se ambos funcionarem, o Docker já está instalado.

```bash
sudo apt update
sudo apt install -y git docker.io docker-cli docker-compose docker-buildx
sudo systemctl enable --now docker
sudo docker ps
sudo docker compose version
```

**Confira:** uma tabela vazia em docker ps é normal na primeira execução. O último comando deve mostrar a versão do Compose.

## 7. Debian via SSH · Clonar o projeto dentro da VM

Na janela que mostra **davi@servidor-estoque**, execute os comandos abaixo. O primeiro baixa o projeto do GitHub para a pasta **~/estoque** no disco da VM. O segundo entra nessa pasta e o terceiro lista os arquivos.

```bash
git clone https://github.com/Davi-Madruga/Gerenciador-de-Estoque.git ~/estoque
cd ~/estoque
ls -a
```

**Confira:** devem aparecer **docker-compose.yml**, **Dockerfile**, **manage.py** e **.env.example**. Se o grupo usa outra branch, mude para ela com `git switch NOME_DA_BRANCH` antes de continuar. Para um repositório privado, utilize uma credencial GitHub autorizada para leitura.

## 8. Debian via SSH · Criar o .env e iniciar o projeto

Ainda em **~/estoque**, cole este bloco uma vez. O arquivo será criado em **/home/davi/estoque/.env** com as três configurações usadas pelo projeto.

```bash
if [ ! -e .env ]; then
  (
    umask 077
    for nome in MYSQL_ROOT_PASSWORD MYSQL_PASSWORD DJANGO_SECRET_KEY; do
      printf '%s=%s\n' "$nome" "$(od -An -N32 -tx1 /dev/urandom | tr -d ' \n')"
    done > .env
  )
fi
sudo docker compose config --quiet
```

Se a validação terminar sem erro, execute:

```bash
sudo docker compose up -d --build
sudo docker compose ps -a
```

**Confira:** **estoque** e **wordpress** devem estar **Up**, e **mysql** deve estar **healthy**. Se algum serviço parar, use `sudo docker compose logs --tail 30 estoque`, substituindo estoque pelo nome do serviço com falha.

## 9. Windows · Abrir o estoque e o blog pelos nomes do grupo

Para o primeiro teste, use o arquivo **hosts**, opção aceita pelo enunciado. No Windows, procure **Bloco de Notas → Executar como administrador → Arquivo → Abrir**. Abra **C:\Windows\System32\drivers\etc\hosts** (se necessário, selecione **Todos os arquivos**). Acrescente a linha abaixo e salve no arquivo existente:

```text
192.168.13.10 estoque.local blog.estoque.local
```

| Abra no Windows | O que testar |
|---|---|
| http://estoque.local:8003 | Cadastre **Café**, quantidade **10**. Anote o ID. Aperte F5 e confira a mesma linha. |
| http://blog.estoque.local:9003 | Conclua o instalador do WordPress por esse endereço e abra a página pública. |
| DBeaver → Nova conexão → MySQL | Servidor **estoque.local**, porta **3303**, usuário **grupo03**, senha **MYSQL_PASSWORD** do .env. Observe os bancos estoque e wordpress. |

Para consultar a senha em particular, use `grep '^MYSQL_PASSWORD=' ~/estoque/.env` na janela SSH. No DBeaver, compare o cadastro com `SELECT id, nome, quantidade FROM estoque.produto ORDER BY id DESC;`.

## 10. Windows · Registrar o teste no Wireshark

1. Selecione a interface **VirtualBox Host-Only** que tem o endereço **192.168.13.1** e comece a captura antes de abrir o site.
2. Em **outra aba do PowerShell**, com prompt **PS**, execute `curl.exe -v http://estoque.local:8003/` e depois `curl.exe -v http://blog.estoque.local:9003/`. Pelo navegador, envie um produto fictício para capturar também o POST.
3. Pare a captura, filtre por `ip.addr == 192.168.13.10 && tcp.port == 8003` e selecione a conversa. Encontre **SYN → SYN/ACK → ACK**, a requisição e a resposta HTTP. Repita com a porta **9003**. Salve o arquivo em **.pcapng**.
4. **Para completar a defesa:** o arquivo hosts resolve os nomes dentro do Windows. Para registrar uma consulta DNS na rede, siga a seção de DNS local do [relatório do grupo](https://chatgpt.com/library?file_id=libfile_7357cbbd33448191a8944b63277d0b29&account_id=personal) e retire a linha do hosts adicionada no passo 9 antes de testar o DNS. O relatório também explica a captura interna das consultas ao MySQL. Em cada print da entrega, mostre nome do grupo ou hostname, data e hora.

## No dia seguinte · Ligar novamente

1. No **VirtualBox**, selecione **Servidor-Estoque → Iniciar** e aguarde o Debian carregar.
2. No **PowerShell do Windows**, execute `ssh davi@192.168.13.10`.
3. Na sessão **Debian**, rode `cd ~/estoque`, `sudo docker compose up -d` e `sudo docker compose ps`.
4. Abra **http://estoque.local:8003** no Windows. O clone, o .env e a instalação são feitos uma vez por disco virtual.

**Se você levar a VM pronta do seu PC:** importe o .ova no notebook em **Arquivo → Importar appliance**. Nesse caminho, o Debian, os arquivos e o Docker já acompanham o disco. Refaça a rede Host-only no Windows do notebook (passos 3–5), confira os serviços com os comandos de “No dia seguinte” e valide os passos 9–10.






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

# Conecta Campus MVP

Sistema web para **mural digital institucional**, desenvolvido com **Flask + SQLite + Bootstrap**, com painel administrativo, upload de mídias, criação de playlists e player web para exibição em TV Box, navegador ou dispositivo conectado à rede local.

O projeto foi pensado para o contexto do **Conecta Campus**, permitindo que avisos, imagens e vídeos sejam publicados em uma tela digital de forma simples, centralizada e atualizável.

---

## Funcionalidades

- Login administrativo.
- Painel web para gerenciamento do conteúdo.
- Upload de imagens e vídeos.
- Reutilização de mídias já cadastradas.
- Download de mídias salvas.
- Criação e organização de slides.
- Player web em tela cheia.
- Ajuste automático de imagens e vídeos na tela.
- Barra de tempo separada da imagem, sem sobreposição.
- Atualização automática do player.
- Rota padrão do player: `/player/conecta_campus`.
- Compatível com uso em TV Box via aplicativo Android Player.

---

## Tecnologias utilizadas

- Python
- Flask
- SQLite
- Bootstrap
- HTML, CSS e JavaScript
- Gunicorn para produção em Linux
- Waitress para produção em Windows

---

## Login padrão

```text
Usuário: admin
Senha: admin123
```

Após o primeiro acesso, recomenda-se alterar as credenciais no código ou no banco de dados, caso o sistema seja usado em ambiente real.

---

## Estrutura básica do projeto

```text
servidor_flask/
├── app.py
├── wsgi.py
├── requirements.txt
├── templates/
├── static/
├── uploads/
├── instance/
├── run_producao_linux.sh
├── run_producao_windows.bat
├── conecta-campus.service.example
└── nginx-conecta-campus.conf.example
```

A estrutura pode variar um pouco dependendo da versão do pacote, mas o arquivo principal do servidor é o `app.py`.

---

## Requisitos

Antes de instalar, tenha no computador:

- Python 3 instalado.
- Pip instalado.
- Acesso ao terminal.
- Navegador atualizado.
- TV Box ou dispositivo Android, caso use o aplicativo player.

No Linux/WSL, instale os pacotes básicos:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-full -y
```

---

# Instalação e execução

## 1. Clonar ou baixar o projeto

Se estiver usando GitHub:

```bash
git clone https://github.com/seu-usuario/conecta-campus.git
cd conecta-campus/servidor_flask
```

Se você baixou o projeto em ZIP, extraia o arquivo e entre na pasta `servidor_flask`.

Exemplo no WSL, usando um caminho do Windows:

```bash
cd /mnt/c/Users/Home/OneDrive/Documentos/projeto4/servidor_flask
```

---

## 2. Criar ambiente virtual

### Linux ou WSL

```bash
python3 -m venv venv --system-site-packages
source venv/bin/activate
```

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

---

## 3. Instalar dependências

Com o ambiente virtual ativado:

```bash
pip install -r requirements.txt
```

Se o `pip` do WSL mostrar erro de ambiente gerenciado, use:

```bash
./venv/bin/pip install -r requirements.txt
```

Se não existir `requirements.txt`, instale o básico:

```bash
pip install flask flask-cors gunicorn waitress
```

---

## 4. Rodar o servidor em modo desenvolvimento

### Linux ou WSL

```bash
./venv/bin/python app.py
```

ou:

```bash
python3 app.py
```

### Windows

```powershell
python app.py
```

O servidor deve iniciar na porta `5000`.

Exemplo de saída:

```text
Running on http://127.0.0.1:5000
Running on http://0.0.0.0:5000
```

---

# Acessar o sistema

## Painel administrativo

No navegador do computador:

```text
http://127.0.0.1:5000/login
```

Ou, usando o IP da rede:

```text
http://IP-DO-SERVIDOR:5000/login
```

Exemplo:

```text
http://192.168.18.11:5000/login
```

---

## Player do Conecta Campus

A rota atual do player é:

```text
http://IP-DO-SERVIDOR:5000/player/conecta_campus
```

Exemplo:

```text
http://192.168.18.11:5000/player/conecta_campus
```

Essa é a URL usada pelo aplicativo Android Player para exibir os slides.

---

# Uso com TV Box e aplicativo Android

O aplicativo Android Player deve estar instalado na TV Box ou dispositivo Android.

Para funcionar corretamente:

1. O servidor Flask precisa estar ligado.
2. A TV Box e o servidor precisam estar na mesma rede local.
3. A porta `5000` precisa estar liberada.
4. O player deve estar disponível em:

```text
http://IP-DO-SERVIDOR:5000/player/conecta_campus
```

A rede local pode ser Wi-Fi ou cabo de rede. O importante é que os dispositivos estejam conectados ao mesmo roteador.

---

## Observação importante para WSL

Se o servidor estiver rodando dentro do WSL, o IP `172.x.x.x` é interno do WSL e normalmente não funciona direto na TV Box.

Use o IP do Windows na rede local, por exemplo:

```text
192.168.18.11
```

Para descobrir o IP do Windows, abra o PowerShell e execute:

```powershell
ipconfig
```

Procure o endereço IPv4 do adaptador Wi-Fi ou Ethernet.

Se necessário, encaminhe a porta do Windows para o WSL no PowerShell como administrador:

```powershell
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=5000 connectaddress=IP-DO-WSL connectport=5000
```

Exemplo:

```powershell
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=5000 connectaddress=172.21.247.217 connectport=5000
```

Também libere a porta no firewall:

```powershell
netsh advfirewall firewall add rule name="Flask5000" dir=in action=allow protocol=TCP localport=5000
```

---

# Rodar em produção

## Linux com Gunicorn

Com o ambiente virtual ativado:

```bash
pip install -r requirements.txt
gunicorn -w 2 -b 0.0.0.0:5000 wsgi:app
```

Ou execute o script:

```bash
./run_producao_linux.sh
```

---

## Windows com Waitress

No PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
waitress-serve --host=0.0.0.0 --port=5000 wsgi:app
```

Ou execute:

```powershell
.\run_producao_windows.bat
```

---

# Iniciar automaticamente no Linux

O projeto inclui um exemplo de serviço systemd:

```text
conecta-campus.service.example
```

Copie para a pasta de serviços:

```bash
sudo cp conecta-campus.service.example /etc/systemd/system/conecta-campus.service
```

Depois edite o arquivo e ajuste:

- usuário;
- caminho do projeto;
- caminho do Python/venv.

Recarregue o systemd:

```bash
sudo systemctl daemon-reload
sudo systemctl enable conecta-campus
sudo systemctl start conecta-campus
```

Verifique o status:

```bash
sudo systemctl status conecta-campus
```

---

# Nginx

Também existe um exemplo de configuração:

```text
nginx-conecta-campus.conf.example
```

Ele pode ser usado para publicar o sistema com domínio, proxy reverso e HTTPS.

---

# Rotas principais

```text
/login
/dashboard
/midias
/playlists
/player/conecta_campus
```

A parte de gerenciamento avançado de telas e associação de telas foi removida deste MVP e fica prevista para uma próxima versão.

---

# Atualização do player

O player verifica atualizações automaticamente. Quando um slide ou mídia é alterado no painel, a TV Box atualiza o conteúdo sem precisar reinstalar o aplicativo.

Nesta versão, o foco é:

- atualização periódica rápida;
- compatibilidade com o aplicativo Android Player;
- funcionamento em rede local;
- exibição contínua dos slides.

---

# Solução de problemas

## O app fica com tela preta

Verifique:

1. O servidor Flask está rodando?
2. A TV Box está na mesma rede do servidor?
3. A porta `5000` está liberada?


Teste no navegador da TV ou celular:

```text
http://IP-DO-SERVIDOR:5000/player/conecta_campus
```

Se abrir no navegador, o aplicativo também deve conseguir carregar.

---

## Erro: No module named flask

Instale as dependências:

```bash
pip install flask flask-cors
```

ou:

```bash
./venv/bin/pip install flask flask-cors
```

---

## Erro: externally-managed-environment

No Linux, recrie o ambiente virtual:

```bash
rm -rf venv
python3 -m venv venv --system-site-packages
source venv/bin/activate
./venv/bin/pip install -r requirements.txt
```

---

```

---

# Próximo MVP

Funcionalidades planejadas para versões futuras:

- Cadastro avançado de telas.
- Associação de playlists por tela.
- Monitoramento online/offline das TVs.
- WebSocket para atualização instantânea.
- Cache offline das mídias no aplicativo.
- Relatórios de exibição.
- Controle remoto das telas.
- Modo kiosk avançado.

---

# Licença

Este projeto é um MVP acadêmico/institucional do **Conecta Campus**.

---

# Autor

Projeto desenvolvido para o **Conecta Campus**.

<div align="center">
  <img src="assets/banner.jpeg" alt="Banner Conecta Campus" width="100%">
</div>
<br>

# Conecta Campus

Plataforma de Digital Signage para comunicação institucional universitária, criada para exibir editais, avisos, eventos, comunicados e mídias em telas espalhadas pelo campus.

## Objetivo

Centralizar a publicação de informações acadêmicas em um painel web e distribuí-las automaticamente para players instalados em TV Boxes Android, computadores reaproveitados ou outros dispositivos conectados a monitores.

## Principais recursos

- Painel administrativo com login.
- Cadastro de usuários administrativos.
- Upload de imagens e vídeos.
- Biblioteca de mídias.
- Playlist com ordem e duração dos conteúdos.
- Publicação de playlist.
- Cadastro e controle de telas.
- Player web responsivo.
- Aplicativo Android em Flutter com WebView.
- Atualização automática da playlist no player.

## Tecnologias

- Python
- Flask
- SQLite
- HTML, CSS e JavaScript
- Flutter
- webview_flutter

## Estrutura

```text
ProjetoConectaCampus/
├── servidor_flask/
│   ├── app.py
│   ├── wsgi.py
│   ├── requirements.txt
│   ├── static/
│   ├── templates/
│   └── media/
└── android_player_builder/
    ├── main.dart
    └── conecta_campus_player_ok/
```

## Instalação no Windows

```powershell
cd servidor_flask
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Depois acesse o painel pelo navegador usando o endereço informado no terminal, seguido de `/login`.

## Instalação no Linux

```bash
cd servidor_flask
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Depois acesse o painel pelo navegador usando o endereço informado no terminal, seguido de `/login`.

## Primeiro acesso

Usuário inicial:

```text
usuário: admin
senha: admin123
```

Após o primeiro acesso, recomenda-se criar um novo usuário administrativo e alterar as credenciais padrão.

## Player

O player pode ser acessado no navegador por:

```text
/player/conecta_campus
```

O aplicativo Android carrega esse endereço dentro de uma WebView. Para usar outro servidor, atualize a constante `url` em `main.dart`.

Exemplo:

```dart
static const String url = 'http://ENDERECO_DO_SERVIDOR:5000/player/conecta_campus';
```

Quando houver domínio institucional, substitua o IP pelo domínio final.

## Funcionamento

1. O administrador acessa o painel.
2. Envia imagens ou vídeos.
3. Organiza a playlist.
4. Publica as alterações.
5. O player consulta a API do servidor.
6. A tela exibe os conteúdos automaticamente.

## Sustentabilidade

O projeto incentiva o reaproveitamento de TV Boxes Android, computadores antigos e monitores disponíveis, reduzindo descarte eletrônico e custos de implantação.

## Próximas evoluções

- Playlists por tela ou campus.
- Agendamento por data e horário.
- Relatórios de status das telas.
- Integração com QR Codes institucionais.
- Painel com permissões por setor.
- Uso com domínio e HTTPS.

# Autores

* Yuri Duarte Oliveira dos Santos
* Guilherme Henrique dos Santos Valente
* Luis Felype de Souza Macedo
* Alan Cunha Café

**Orientador:** José Vigno Moura Sousa
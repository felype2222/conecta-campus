import os
import sqlite3
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "painel.db")
MEDIA_DIR = os.path.join(BASE_DIR, "media")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "mp4", "webm"}
MAX_ITEMS = 5

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024
os.makedirs(MEDIA_DIR, exist_ok=True)

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT UNIQUE NOT NULL, senha_hash TEXT NOT NULL, criado_em TEXT NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS midias (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, arquivo TEXT NOT NULL, tipo TEXT NOT NULL, criado_em TEXT NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS playlist_itens (
        id INTEGER PRIMARY KEY AUTOINCREMENT, midia_id INTEGER NOT NULL, ordem INTEGER NOT NULL, duracao INTEGER NOT NULL DEFAULT 10)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS telas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT UNIQUE NOT NULL, nome TEXT NOT NULL, ativo INTEGER NOT NULL DEFAULT 1, ultimo_acesso TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS publicacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, publicado_em TEXT NOT NULL, usuario TEXT NOT NULL)""")
    if not cur.execute("SELECT id FROM usuarios WHERE usuario='admin'").fetchone():
        cur.execute("INSERT INTO usuarios(usuario,senha_hash,criado_em) VALUES(?,?,?)",
                    ("admin", generate_password_hash("admin123"), datetime.now().isoformat(timespec="seconds")))
    # Campi/núcleos iniciais do Conecta Campus
    campi_padrao = [
        ("conecta_campus", "Conecta Campus"),
        ("poeta_torquato_neto", "Campus Poeta Torquato Neto"),
        ("alexandre_alves", "Campus Prof. Alexandre Alves de Oliveira - Parnaíba"),
        ("antonio_giovanni", "Campus Prof. Antonio Giovanni Alves de Sousa - Piripiri"),
        ("herois_jenipapo", "Campus Heróis do Jenipapo - Campo Maior"),
        ("nucleo_barras", "Núcleos - Barras"),
        ("barros_araujo", "Campus Prof. Barros Araújo - Picos"),
        ("possidonio_queiroz", "Campus Possidônio Queiroz - Oeiras"),
        ("josefina_demes", "Campus Dra. Josefina Demes - Floriano"),
        ("ariston_dias", "Campus Prof. Ariston Dias Lima - São Raimundo Nonato"),
    ]

    # Remove os nomes antigos de exemplo, caso ainda existam em um banco de versão anterior.
    for codigo_antigo in ("recepcao01", "elevador01", "corredor01", "sala01"):
        cur.execute("DELETE FROM telas WHERE codigo=?", (codigo_antigo,))

    for codigo, nome in campi_padrao:
        cur.execute("INSERT OR IGNORE INTO telas(codigo,nome,ativo) VALUES(?,?,?)",(codigo,nome,1))
    conn.commit(); conn.close()

def allowed(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

def media_type(filename):
    return "video" if filename.rsplit(".",1)[1].lower() in {"mp4","webm"} else "imagem"

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def get_stats():
    conn=db()
    stats={
        "slides": conn.execute("SELECT COUNT(*) c FROM playlist_itens").fetchone()["c"],
        "midias": conn.execute("SELECT COUNT(*) c FROM midias").fetchone()["c"],
        "telas": conn.execute("SELECT COUNT(*) c FROM telas").fetchone()["c"],
        "online": conn.execute("SELECT COUNT(*) c FROM telas WHERE ultimo_acesso IS NOT NULL").fetchone()["c"],
    }
    conn.close(); return stats

@app.route("/")
def home(): return redirect(url_for("admin"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        usuario=request.form.get("usuario","").strip()
        senha=request.form.get("senha","")
        conn=db(); user=conn.execute("SELECT * FROM usuarios WHERE usuario=?",(usuario,)).fetchone(); conn.close()
        if user and check_password_hash(user["senha_hash"], senha):
            session["user_id"]=user["id"]; session["usuario"]=user["usuario"]
            return redirect(url_for("admin"))
        flash("Usuário ou senha inválidos.")
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        usuario=request.form.get("usuario","").strip()
        senha=request.form.get("senha","")
        if len(usuario)<3 or len(senha)<6:
            flash("Usuário precisa ter 3 caracteres e senha no mínimo 6.")
            return render_template("register.html")
        try:
            conn=db()
            conn.execute("INSERT INTO usuarios(usuario,senha_hash,criado_em) VALUES(?,?,?)",
                         (usuario, generate_password_hash(senha), datetime.now().isoformat(timespec="seconds")))
            conn.commit(); conn.close()
            flash("Usuário criado. Faça login.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Este usuário já existe.")
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("login"))

@app.route("/admin")
@login_required
def admin():
    return render_template("admin.html", **load_admin_context(), page="dashboard", stats=get_stats())

def load_admin_context():
    conn=db()
    itens=conn.execute("""SELECT pi.id,pi.ordem,pi.duracao,m.id midia_id,m.nome,m.arquivo,m.tipo
        FROM playlist_itens pi JOIN midias m ON m.id=pi.midia_id ORDER BY pi.ordem ASC, pi.id ASC""").fetchall()
    telas=conn.execute("SELECT * FROM telas ORDER BY nome").fetchall()
    midias=conn.execute("SELECT * FROM midias ORDER BY criado_em DESC").fetchall()
    pubs=conn.execute("SELECT * FROM publicacoes ORDER BY id DESC LIMIT 5").fetchall()
    conn.close()
    return dict(itens=itens,telas=telas,midias=midias,pubs=pubs,max_items=MAX_ITEMS)

@app.route("/admin/<page>")
@login_required
def admin_page(page):
    if page not in {"playlists","midias","agendamentos","relatorios","configuracoes"}:
        return redirect(url_for("admin"))
    return render_template("admin.html", **load_admin_context(), page=page, stats=get_stats())

@app.route("/admin/telas/add", methods=["POST"])
@login_required
def add_tela():
    codigo=secure_filename(request.form.get("codigo","").strip().lower()).replace("_","")
    nome=request.form.get("nome","").strip()
    if codigo and nome:
        conn=db(); conn.execute("INSERT OR IGNORE INTO telas(codigo,nome,ativo) VALUES(?,?,1)",(codigo,nome)); conn.commit(); conn.close()
        flash("Tela cadastrada.")
    return redirect(url_for("admin_page", page="telas"))

@app.route("/admin/upload", methods=["POST"])
@login_required
def upload():
    conn=db()
    count=conn.execute("SELECT COUNT(*) c FROM playlist_itens").fetchone()["c"]
    add_to_playlist=request.form.get("add_to_playlist","on")=="on"
    if add_to_playlist and count>=MAX_ITEMS:
        conn.close(); flash("A playlist já possui o limite de 5 itens."); return redirect(url_for("admin"))
    file=request.files.get("arquivo")
    duracao=max(3,int(request.form.get("duracao",10) or 10))
    if not file or file.filename=="" or not allowed(file.filename):
        conn.close(); flash("Envie uma imagem ou vídeo válido."); return redirect(url_for("admin"))
    original=secure_filename(file.filename)
    filename=f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{original}"
    file.save(os.path.join(MEDIA_DIR, filename))
    tipo=media_type(filename)
    cur=conn.cursor()
    cur.execute("INSERT INTO midias(nome,arquivo,tipo,criado_em) VALUES(?,?,?,?)",
                (original, filename, tipo, datetime.now().isoformat(timespec="seconds")))
    midia_id=cur.lastrowid
    if add_to_playlist:
        cur.execute("INSERT INTO playlist_itens(midia_id,ordem,duracao) VALUES(?,?,?)",(midia_id,count+1,duracao))
    conn.commit(); conn.close()
    flash("Mídia enviada com sucesso.")
    return redirect(request.referrer or url_for("admin"))

@app.route("/admin/playlist/add-existing", methods=["POST"])
@login_required
def playlist_add_existing():
    midia_id=int(request.form.get("midia_id"))
    duracao=max(3,int(request.form.get("duracao",10) or 10))
    conn=db(); count=conn.execute("SELECT COUNT(*) c FROM playlist_itens").fetchone()["c"]
    if count<MAX_ITEMS:
        conn.execute("INSERT INTO playlist_itens(midia_id,ordem,duracao) VALUES(?,?,?)",(midia_id,count+1,duracao))
        conn.commit(); flash("Mídia adicionada à playlist.")
    else:
        flash("Limite de 5 itens atingido.")
    conn.close(); return redirect(url_for("admin_page", page="playlists"))

@app.route("/admin/item/<int:item_id>/update", methods=["POST"])
@login_required
def update_item(item_id):
    duracao=max(3,int(request.form.get("duracao",10) or 10)); ordem=max(1,int(request.form.get("ordem",1) or 1))
    conn=db(); conn.execute("UPDATE playlist_itens SET duracao=?, ordem=? WHERE id=?",(duracao,ordem,item_id)); conn.commit(); conn.close()
    flash("Item atualizado."); return redirect(request.referrer or url_for("admin"))

@app.route("/admin/item/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_item(item_id):
    conn=db(); conn.execute("DELETE FROM playlist_itens WHERE id=?",(item_id,)); conn.commit(); conn.close()
    flash("Item removido."); return redirect(request.referrer or url_for("admin"))


@app.route("/admin/midia/<int:midia_id>/delete", methods=["POST"])
@login_required
def delete_midia(midia_id):
    conn=db()
    midia=conn.execute("SELECT * FROM midias WHERE id=?", (midia_id,)).fetchone()
    if midia:
        conn.execute("DELETE FROM playlist_itens WHERE midia_id=?", (midia_id,))
        conn.execute("DELETE FROM midias WHERE id=?", (midia_id,))
        conn.commit()
        try:
            os.remove(os.path.join(MEDIA_DIR, midia["arquivo"]))
        except OSError:
            pass
        flash("Mídia removida da biblioteca e da playlist.")
    conn.close()
    return redirect(request.referrer or url_for("admin_page", page="midias"))

@app.route("/admin/tela/<int:tela_id>/toggle", methods=["POST"])
@login_required
def toggle_tela(tela_id):
    ativo=1 if request.form.get("ativo")=="on" else 0
    conn=db(); conn.execute("UPDATE telas SET ativo=? WHERE id=?",(ativo,tela_id)); conn.commit(); conn.close()
    return redirect(request.referrer or url_for("admin"))

@app.route("/admin/publish", methods=["POST"])
@login_required
def publish():
    conn=db(); conn.execute("INSERT INTO publicacoes(publicado_em,usuario) VALUES(?,?)",
                            (datetime.now().strftime("%d/%m/%Y %H:%M"), session.get("usuario","admin")))
    conn.commit(); conn.close()
    flash("Playlist publicada. O aplicativo/player atualizará automaticamente em até 5 segundos.")
    return redirect(url_for("admin"))

@app.route("/player")
def player_padrao():
    return redirect(url_for("player", codigo="conecta_campus"))

@app.route("/player/<codigo>")
def player(codigo):
    conn=db(); conn.execute("UPDATE telas SET ultimo_acesso=? WHERE codigo=?",(datetime.now().isoformat(timespec="seconds"),codigo)); conn.commit(); conn.close()
    return render_template("player.html", codigo=codigo)

@app.route("/api/player/<codigo>")
def api_player(codigo):
    conn=db()
    tela=conn.execute("SELECT * FROM telas WHERE codigo=?",(codigo,)).fetchone()
    if not tela or not tela["ativo"]:
        conn.close(); return jsonify({"ativo":False,"slides":[]})
    itens=conn.execute("""SELECT pi.ordem,pi.duracao,m.nome,m.arquivo,m.tipo FROM playlist_itens pi
        JOIN midias m ON m.id=pi.midia_id ORDER BY pi.ordem ASC, pi.id ASC""").fetchall()
    conn.execute("UPDATE telas SET ultimo_acesso=? WHERE codigo=?",(datetime.now().isoformat(timespec="seconds"),codigo)); conn.commit(); conn.close()
    return jsonify({"ativo":True,"tela":codigo,"playlist":"Avisos Gerais",
        "slides":[{"tipo":i["tipo"],"nome":i["nome"],"url":url_for("media",filename=i["arquivo"]),"duracao":i["duracao"]} for i in itens]})

@app.route("/media/<path:filename>")
def media(filename): return send_from_directory(MEDIA_DIR, filename)

@app.route("/media/<path:filename>/download")
@login_required
def media_download(filename):
    return send_from_directory(MEDIA_DIR, filename, as_attachment=True)

init_db()

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

import os
import sqlite3
from datetime import datetime, timedelta

from flask import Flask, g, redirect, render_template, request, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("REGISTRO_DB", os.path.join(BASE_DIR, "registro.db"))

app = Flask(__name__)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS articoli (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            categoria TEXT NOT NULL DEFAULT 'generale',
            unita TEXT NOT NULL DEFAULT 'pz',
            soglia_minima REAL NOT NULL DEFAULT 0,
            creato_il TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        );
        CREATE TABLE IF NOT EXISTS movimenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            articolo_id INTEGER NOT NULL REFERENCES articoli(id) ON DELETE CASCADE,
            quantita REAL NOT NULL,
            tipo TEXT NOT NULL CHECK (tipo IN ('carico', 'scarico')),
            note TEXT DEFAULT '',
            data TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        );
        """
    )
    db.commit()
    db.close()


def giacenza(db, articolo_id):
    row = db.execute(
        """
        SELECT COALESCE(SUM(CASE WHEN tipo = 'carico' THEN quantita ELSE -quantita END), 0) AS qta
        FROM movimenti WHERE articolo_id = ?
        """,
        (articolo_id,),
    ).fetchone()
    return row["qta"]


def statistiche_articolo(db, articolo_id):
    """Ritorna giacenza, velocità di consumo (unità/giorno) e stima giorni rimanenti."""
    movimenti = db.execute(
        "SELECT quantita, tipo, data FROM movimenti WHERE articolo_id = ? ORDER BY data",
        (articolo_id,),
    ).fetchall()
    giac = sum(
        (m["quantita"] if m["tipo"] == "carico" else -m["quantita"]) for m in movimenti
    )

    velocita = 0.0
    giorni_rimanenti = None
    scarichi = [m for m in movimenti if m["tipo"] == "scarico"]
    if len(scarichi) >= 2:
        prima = datetime.fromisoformat(scarichi[0]["data"])
        ultima = datetime.fromisoformat(scarichi[-1]["data"])
        giorni = (ultima - prima).total_seconds() / 86400
        if giorni > 0:
            totale = sum(m["quantita"] for m in scarichi)
            velocita = totale / giorni
            if velocita > 0 and giac > 0:
                giorni_rimanenti = giac / velocita

    return giac, velocita, giorni_rimanenti


def lista_articoli(db):
    articoli = db.execute("SELECT * FROM articoli ORDER BY nome").fetchall()
    risultato = []
    for a in articoli:
        giac, velocita, giorni = statistiche_articolo(db, a["id"])
        risultato.append(
            {
                "id": a["id"],
                "nome": a["nome"],
                "categoria": a["categoria"],
                "unita": a["unita"],
                "soglia_minima": a["soglia_minima"],
                "giacenza": giac,
                "velocita": velocita,
                "giorni_rimanenti": giorni,
                "sotto_soglia": giac <= a["soglia_minima"],
            }
        )
    return risultato


@app.route("/")
def index():
    db = get_db()
    articoli = lista_articoli(db)
    return render_template("index.html", articoli=articoli)


@app.route("/articoli/nuovo", methods=["POST"])
def articolo_nuovo():
    db = get_db()
    nome = request.form.get("nome", "").strip()
    if not nome:
        return redirect(url_for("index"))
    db.execute(
        "INSERT INTO articoli (nome, categoria, unita, soglia_minima) VALUES (?, ?, ?, ?)",
        (
            nome,
            request.form.get("categoria", "generale").strip() or "generale",
            request.form.get("unita", "pz").strip() or "pz",
            float(request.form.get("soglia_minima") or 0),
        ),
    )
    db.commit()
    return redirect(url_for("index"))


@app.route("/articoli/<int:articolo_id>/elimina", methods=["POST"])
def articolo_elimina(articolo_id):
    db = get_db()
    db.execute("DELETE FROM articoli WHERE id = ?", (articolo_id,))
    db.commit()
    return redirect(url_for("index"))


@app.route("/articoli/<int:articolo_id>/movimento", methods=["POST"])
def movimento(articolo_id):
    db = get_db()
    tipo = request.form.get("tipo")
    if tipo not in ("carico", "scarico"):
        return redirect(url_for("index"))
    try:
        quantita = float(request.form.get("quantita"))
    except (TypeError, ValueError):
        quantita = 0
    if quantita <= 0:
        return redirect(url_for("index"))
    db.execute(
        "INSERT INTO movimenti (articolo_id, quantita, tipo, note) VALUES (?, ?, ?, ?)",
        (articolo_id, quantita, tipo, request.form.get("note", "").strip()),
    )
    db.commit()
    return redirect(url_for("index"))


@app.route("/articoli/<int:articolo_id>")
def dettaglio(articolo_id):
    db = get_db()
    articolo = db.execute("SELECT * FROM articoli WHERE id = ?", (articolo_id,)).fetchone()
    if articolo is None:
        return redirect(url_for("index"))
    giac, velocita, giorni = statistiche_articolo(db, articolo_id)
    movimenti = db.execute(
        "SELECT * FROM movimenti WHERE articolo_id = ? ORDER BY data DESC",
        (articolo_id,),
    ).fetchall()
    return render_template(
        "dettaglio.html",
        articolo=articolo,
        giacenza=giac,
        velocita=velocita,
        giorni_rimanenti=giorni,
        movimenti=movimenti,
    )


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)

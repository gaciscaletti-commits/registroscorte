# Registro Scorte — Centro Recupero Animali

Semplice webapp locale per tenere traccia delle scorte (cibo, farmaci, materiali,
pulizia) di un centro di recupero animali, con calcolo automatico della velocità
di consumo e alert quando una scorta scende sotto la soglia minima.

## Requisiti

- Python 3.9+
- Flask (`pip install flask`)

## Avvio

```bash
pip install -r requirements.txt
python app.py
```

Poi apri <http://127.0.0.1:5000> nel browser.

Il database SQLite (`registro.db`) viene creato automaticamente al primo avvio.

## Funzionalità

- **Articoli**: nome, categoria, unità di misura (pz, kg, l...) e soglia minima.
- **Movimenti**: carichi e scarichi con note e data, storico completo per articolo.
- **Velocità di consumo**: calcolata dal primo all'ultimo scarico registrato
  (unità/giorno), con stima dei giorni di autonomia rimanenti.
- **Alert**: evidenzia gli articoli con giacenza pari o sotto la soglia minima.

## Note

L'app ascolta solo su `127.0.0.1`: è pensata per girare in locale sul server,
esponibile poi tramite un proxy interno se serve accesso in rete locale.

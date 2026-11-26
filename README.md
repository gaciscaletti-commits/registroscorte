# Registro Scorte

Checklist scorte per il centro di recupero fauna selvatica, pensata per mobile.

- Ogni articolo ha quantità attuale, soglia d'ordine e max stock (default: 5x la soglia).
- Se la quantità è inferiore alla soglia d'ordine, l'articolo viene segnalato **DA ORDINARE**.
- Il pulsante "Rifornito" porta l'articolo al max stock.
- "Lista spesa" mostra cosa comprare e quanto (max stock − quantità attuale), copiabile negli appunti.
- I dati sono salvati nel browser (localStorage). Per condividerli tra più dispositivi serve sincronizzare il browser o esportare il file JSON.

## Uso

Host statico: abilitare GitHub Pages (Settings → Pages → Branch: main) e aprire l'URL generato, oppure aprire `index.html` direttamente.

## Nota quantità frazionarie

Soglie tipo "1/4 di barile" e "1/2 mensola" vanno inserite come 0,25 e 0,5.

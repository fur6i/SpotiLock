# SpotiLock

<p align="center">
  <img src="assets/spotilock-logo.png" alt="SpotiLock logo" width="128">
</p>

**Italiano** · [English](README.md)

Un piccolo programma per Windows che mantiene il **volume interno di Spotify**
al livello scelto. Usa l'API ufficiale, senza spostare il cursore, attivare la
finestra o modificare Spotify. I comandi funzionano anche con la finestra ridotta
a icona, purché il dispositivo sia disponibile per Spotify.

## Requisiti

- Windows 10 o 11 a 64 bit. L'eseguibile non richiede Python installato.
- Spotify Premium, Internet e Spotify aperto sul PC.
- Un'app personale nel [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).

## Avvio

1. Scarica **SpotifyVolumeLock.exe** e tienilo in una cartella dove puoi scrivere file.
2. Apri Spotify e riproduci un brano su questo PC per renderlo disponibile.
3. Apri **SpotifyVolumeLock.exe**. Digita **1** per Italiano o **2** per English e premi **Invio**. Invio senza numero usa la lingua precedente.
4. Al primo avvio parte automaticamente il collegamento dell'account. Dopo la configurazione si apre il pannello nella stessa finestra.
5. Gli avvii successivi riutilizzano automaticamente Client ID, account e PC.

C'è un solo eseguibile. Python e dipendenze sono inclusi: non servono installazione o file batch. Premi **R** nel pannello per ricollegare l'account o cambiare PC.

### Collegamento iniziale

Crea un'app nel Developer Dashboard, seleziona **Web API** e registra
esattamente questo Redirect URI:

```text
http://127.0.0.1:8765/callback
```

Copia il **Client ID** nel terminale e premi **Invio**. Non serve il Client Secret.
Autorizza il collegamento nel browser e torna al terminale. Il Client ID viene
ricordato subito, anche se la procedura si interrompe.

**Il PC viene selezionato automaticamente quando il suo nome in Spotify
corrisponde al nome del computer Windows.** Negli altri casi compare un elenco
numerato. **Digita il numero accanto al tuo PC e premi Invio sulla tastiera:
non devi fare clic sul numero.** Per esempio, se vedi `1. Il mio PC`, digita
`1` e premi **Invio**. Invio senza numero aggiorna l'elenco; `Q` annulla.

Dopo la configurazione il pannello di controllo si apre subito. Gli avvii
successivi con **SpotifyVolumeLock.exe** riutilizzano account e dispositivo senza chiedere
nuovamente il Client ID. Il tasto **R** permette di ricollegare l'account
o scegliere un altro PC.

## Comandi

| Tasto | Azione |
|---|---|
| **F** | Scegli volume fisso: digita 0–100 e premi Invio. |
| **V** | Cambia il volume desiderato mantenendo la modalità attuale. |
| **+ / −** | Aumenta / diminuisce di 5 punti percentuali. |
| **A** | Attiva la modalità interattiva. |
| **Esc** | Annulla la digitazione. |
| **R** | Ricollega l'account / sceglie un PC nella stessa finestra. |
| **Q** | Esce dal programma. |

In modalità fissa il volume torna al valore scelto dopo un cambiamento.
La modalità interattiva accetta cambi dopo un tuo input con Spotify in primo
piano e il puntatore sopra la finestra. I comandi del terminale funzionano
in entrambe le modalità, indipendentemente dalla visibilità della finestra.

La scelta della lingua compare prima della configurazione e del pannello.
Istruzioni, pagina di ritorno nel browser, comandi, stati ed errori del programma
seguono la lingua scelta. I messaggi esterni di Python e pip seguono le impostazioni
di quei programmi.

## Tempi e limiti

Chiudi Spotify sul telefono per evitare possibili conflitti con il volume del PC.
Questo avviso compare anche nel pannello di controllo.

Il controllo legge il volume ogni **3 secondi** e verifica che Spotify abbia
applicato il valore richiesto. Un cambiamento esterno può durare qualche secondo
prima della correzione. Internet e i limiti dell'API possono aggiungere attese;
il programma rispetta i tempi di ripetizione indicati da Spotify.

Il riconoscimento dei cambi manuali è approssimativo: l'API non comunica chi abbia
modificato il volume. Un cambio automatico contemporaneo al tuo input in Spotify
può essere acquisito. **F** offre il comportamento più prevedibile.

Spotify deve restare disponibile tra i dispositivi Connect. Se scompare, aprilo
e avvia un brano qui. Il programma non avvia o trasferisce automaticamente la
riproduzione. Se il comando non viene confermato entro circa 8–9 secondi, i tentativi
si fermano: **V** o **+ / −** permettono di riprovare.

## File locali e GitHub

La cartella distribuita non contiene dati dell'account. Il programma crea questi
file locali accanto all'eseguibile, esclusi da `.gitignore`:

| File | Contenuto |
|---|---|
| `preferences.json` | Ultima lingua scelta. |
| `client.json` | Client ID salvato prima dell'autorizzazione. |
| `config.json` | Client ID e dispositivo scelto. |
| `accesso.dat` | Credenziali cifrate con Windows DPAPI. |

Le credenziali sono legate al tuo account Windows. Conserva questi file quando
aggiorni il programma; ripeti il collegamento se cambi PC o account Windows.
Per scollegare definitivamente il programma, revoca l'accesso dalle impostazioni
del tuo account Spotify.

Per GitHub carica codice e documentazione. Se usi il caricamento tramite sito,
escludi manualmente i file locali: l'interfaccia web non applica `.gitignore`.
Lo ZIP fornito contiene sorgenti, documentazione ed eseguibile, senza dati personali.
Per pubblicarlo segui [la guida GitHub](GITHUB.md).

## Riga di comando

```text
SpotifyVolumeLock.exe --lang it --volume 70 --fisso
SpotifyVolumeLock.exe --lang en --volume 70 --fixed
SpotifyVolumeLock.exe --lang it --configura
SpotifyVolumeLock.exe --lang it --client-id NUOVO_CLIENT_ID
```

Senza `--lang` compare la scelta della lingua. Le opzioni principali hanno alias
italiani e inglesi. `--intervallo` / `--interval` cambia la frequenza delle letture;
il minimo è 2 secondi.

## Creare l'eseguibile (solo per sviluppatori)

Su Windows, con Python 3.10 o successivo:

```text
python -m pip install -r requirements-build.txt
python build.py
```

Il risultato è `dist/SpotifyVolumeLock.exe`, da pubblicare come allegato di una Release GitHub. Il repository contiene i sorgenti; l'eseguibile include tutte le dipendenze necessarie. I dati personali non vengono inclusi nella compilazione.

## Sviluppo

```text
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

I test usano risposte simulate e non richiedono un account. La prova reale richiede
il proprio account collegato e il dispositivo selezionato. Il collegamento usa
OAuth Authorization Code con PKCE e non salva un Client Secret.

[Documentazione del controllo volume Spotify](https://developer.spotify.com/documentation/web-api/reference/set-volume-for-users-playback)

Il progetto è indipendente da Spotify.

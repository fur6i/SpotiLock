# Debug report / Diagnosi

## English

`debug_report.py` is an optional diagnostic tool for the source project.
It does not change Spotify's volume and is not part of the existing executable.
Place it in the repository root, beside `launcher.py`.

With Python 3.10 or later, run:

```text
python debug_report.py --lang en
```

The offline check needs only Python's standard library. It writes
`diagnosi_spotify.json` beside the script with file availability, dependency checks
and configuration status. It never copies configuration contents or decrypts tokens.

To also read the selected device's current volume and capabilities:

```text
python debug_report.py --lang en --online
```

The online check requires Windows, the existing source modules and account files
beside the script, plus Internet access. It uses the saved account without opening
an authorization browser. It may refresh and save the local authorization token.
It does not send a volume command, transfer playback or change the selected device.
If the selected device disappears, the report records that condition.

Reports omit tokens, Client ID, device IDs, device names and raw exception messages.
The existing `.gitignore` already excludes `diagnosi_spotify.json`.

## Italiano

`debug_report.py` è uno strumento facoltativo per la diagnosi del progetto sorgente.
Non modifica il volume di Spotify e non è incluso nell'eseguibile già pubblicato.
Mettilo nella radice della repository, accanto a `launcher.py`.

Con Python 3.10 o successivo:

```text
python debug_report.py --lang it
```

La diagnosi offline richiede solo Python e crea `diagnosi_spotify.json` accanto
allo script. Controlla presenza dei file, dipendenze e configurazione senza
copiare il contenuto delle impostazioni o decifrare i token.

Per leggere anche volume e capacità del dispositivo selezionato:

```text
python debug_report.py --lang it --online
```

Il controllo online richiede Windows, i moduli sorgente e i file dell'account
accanto allo script, oltre a Internet. Usa il collegamento esistente senza aprire
il browser; può aggiornare e salvare il token locale. Non invia comandi di volume,
non trasferisce la riproduzione e non cambia il dispositivo selezionato.

La diagnosi esclude token, Client ID, ID e nomi dei dispositivi e messaggi grezzi
delle eccezioni. `diagnosi_spotify.json` è già escluso dal `.gitignore` esistente.

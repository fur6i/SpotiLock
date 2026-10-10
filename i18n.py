"""Italian/English messages and persistent startup language selection."""
import json
from pathlib import Path
from app_paths import data_root

ROOT = data_root()
LANGUAGE = "it"
ENGLISH = {
    "Avviso: chiudi Spotify sul telefono per evitare possibili conflitti.": "Notice: close Spotify on your phone to avoid possible conflicts.",
    "Ricollega account / scegli PC": "Reconnect account / select PC",
    "Premi R per ricollegare l'account qui, oppure Invio per chiudere: ": "Press R to reconnect your account here, or Enter to close: ",
    "Collegamento mancante: riapri SpotifyVolumeLock.exe per configurare l'account.": "Authorization missing: reopen SpotifyVolumeLock.exe to set up your account.",
    "Accesso scaduto: riavvia il programma con --setup per ricollegare l'account.": "Authorization expired: restart the program with --setup to reconnect your account.",
    "PC non disponibile o ambiguo: apri Spotify oppure riavvia con --setup.": "PC unavailable or ambiguous: open Spotify or restart with --setup.",
    "Collegamento annullato o scaduto. Riapri SpotifyVolumeLock.exe per riprovare.": "Authorization cancelled or timed out. Reopen SpotifyVolumeLock.exe to retry.",
    "Riapri SpotifyVolumeLock.exe per riprovare. Per ricollegare l'account usa --setup.": "Reopen SpotifyVolumeLock.exe to retry. Use --setup to reconnect your account.",
    "SECONDI": "SECONDS",
    "Modifica annullata.": "Change cancelled.",
    "Inserisci un numero da 0 a 100.": "Enter a number from 0 to 100.",
    "Volume aggiornato.": "Target volume updated.",
    "Puoi cambiare il volume anche dentro Spotify.": "You can also change the volume inside Spotify.",
    "Prima seleziona un volume con V oppure apri Spotify.": "First choose a volume with V or open Spotify.",
    "In attesa di Spotify": "Waiting for Spotify",
    "Spotify collegato": "Spotify connected",
    "\nIl tuo volume, sotto controllo.": "\nYour volume, under control.",
    "\nVOLUME DA MANTENERE": "\nTARGET VOLUME",
    "Modalità": "Mode",
    "Fissa": "Fixed",
    "Interattiva": "Interactive",
    "Volume in Spotify": "Spotify volume",
    "non applicato": "not applied",
    "Stato": "Status",
    "Mantiene il valore scelto anche quando usi Spotify.": "Keeps your target volume while you use Spotify.",
    "Accetta i tuoi cambi con Spotify attivo e il mouse sopra.": "Accepts changes with Spotify focused and the pointer over it.",
    "Input rilevato in Spotify · modifica del volume consentita.": "Input detected in Spotify · volume changes allowed.",
    "Scegli volume fisso": "Choose fixed volume",
    "Cambia volume scelto": "Change target volume",
    "Aumenta / diminuisci di 5 punti": "Increase / decrease by 5 points",
    "Modalità interattiva": "Interactive mode",
    "Esci": "Quit",
    "Cambia volume": "Change volume",
    " · Invio vuoto mantiene {0:g}%": " · Empty Enter keeps {0:g}%",
    "\n0–100 · Invio conferma · Esc annulla{0}": "\n0–100 · Enter confirms · Esc cancels{0}",
    "Premi un comando per iniziare.": "Press a command to start.",
    "Collega il tuo account e seleziona questo PC.": "Connect your account and select this PC.",
    "Solo volume interno Spotify": "Spotify internal volume only",
    "Attività recente": "Recent activity",
    "Limite richieste Spotify: attendo prima di riprovare.": "Spotify request limit reached: waiting before retrying.",
    "Accesso scaduto: esegui Configura.bat per ricollegare l'account.": "Authorization expired: run Setup.bat to reconnect your account.",
    "Accesso negato: verifica Premium e l'accesso all'app nel Developer Dashboard.": "Access denied: check Premium and app access in the Developer Dashboard.",
    "PC non disponibile: avvia un brano su Spotify in questo PC.": "PC unavailable: play a track in Spotify on this PC.",
    "Configurazione non valida: controlla Client ID e indirizzo di ritorno.": "Invalid configuration: check your Client ID and redirect URI.",
    "Spotify ha risposto con errore {0}.": "Spotify returned error {0}.",
    "Connessione a Spotify assente. Riprovo automaticamente.": "No connection to Spotify. Retrying automatically.",
    "Collegamento mancante: esegui Configura.bat.": "Authorization missing: run Setup.bat.",
    "PC non disponibile o ambiguo: apri Spotify oppure usa Configura.bat.": "PC unavailable or ambiguous: open Spotify or run Setup.bat.",
    "Questo dispositivo non consente il controllo del volume tramite Spotify.": "This device does not support volume control through Spotify.",
    "Volume fuori intervallo": "Volume out of range",
    "Richiesta non valida.": "Invalid request.",
    "Puoi chiudere questa scheda e tornare al terminale.": "You can close this tab and return to the terminal.",
    "Apro il browser per collegare Spotify. Se non si apre, copia questo indirizzo:\n": "Opening your browser to connect Spotify. If it does not open, copy this address:\n",
    "Collegamento annullato o scaduto. Riprova con Configura.bat.": "Authorization cancelled or timed out. Retry with Setup.bat.",
    "SPOTIFY VOLUME LOCK · Collegamento ufficiale\n": "SPOTIFY VOLUME LOCK · Official connection\n",
    "Uso il Client ID già salvato.\n": "Using your saved Client ID.\n",
    "1. Crea un'app su https://developer.spotify.com/dashboard": "1. Create an app at https://developer.spotify.com/dashboard",
    "2. Inserisci questo Redirect URI: ": "2. Enter this Redirect URI: ",
    "3. Seleziona Web API e copia il Client ID (non serve Client Secret).\n": "3. Select Web API and copy the Client ID (no Client Secret needed).\n",
    "Client ID non valido: copia i 32 caratteri dalle impostazioni dell'app.": "Invalid Client ID: copy the 32 characters from your app settings.",
    "Questo PC riconosciuto: {0}.": "This PC detected: {0}.",
    "{0}. {1} · volume {2}%": "{0}. {1} · volume {2}%",
    "Collegamento riuscito. Ora scegli il computer da controllare.": "Connected successfully. Now choose the computer to control.",
    "DIGITA il numero a sinistra del nome del tuo PC, poi premi INVIO.": "TYPE the number to the left of your PC name, then press ENTER.",
    "Esempio: se vedi «1. Il mio PC», digita 1 sulla tastiera e premi Invio. Non serve fare clic.": "Example: if you see '1. My PC', type 1 on your keyboard and press Enter. No clicking is needed.",
    "Numero del PC → ": "PC number → ",
    "Invio senza numero aggiorna l'elenco · Q annulla.": "Enter without a number refreshes the list · Q cancels.",
    "Configurazione annullata.": "Setup cancelled.",
    "Scelta non valida: inserisci il numero mostrato a sinistra del nome del PC.": "Invalid choice: enter the number shown to the left of your PC name.",
    "Apri Spotify e avvia un brano su questo PC se non compare nell'elenco.": "Open Spotify and play a track on this PC if it is not listed.",
    "Collegamento completato. Apro il pannello di controllo…": "Setup complete. Opening the control panel…",
    "Collegamento ufficiale a Spotify": "Connecting to Spotify",
    "Invio del volume richiesto…": "Sending the requested volume…",
    "Volume confermato · ": "Volume confirmed · ",
    "In attesa della conferma di Spotify": "Waiting for Spotify to confirm",
    "Volume non applicato: riprova con V o + / −": "Volume not applied: retry with V or + / −",
    "Spotify non ha confermato il volume. Non ripeto il comando in continuazione.": "Spotify did not confirm the volume. Repeated retries have been stopped.",
    "Volume scelto in Spotify acquisito": "Volume selected in Spotify accepted",
    "Comando inviato · verifico il volume": "Command sent · checking volume",
    "Errore del collegamento: ": "Connection error: ",
    "Scegli un numero da 0 a 100": "Choose a number from 0 to 100",
    "Sostituisce il Client ID salvato e ricollega l'account": "Replaces the saved Client ID and reconnects your account",
    "L'intervallo deve essere di almeno 2 secondi": "The interval must be at least 2 seconds",
    "Controllo volume terminato.": "Volume control stopped.",
    "Per collegare o riselezionare il PC apri Configura.bat; per le dipendenze usa Installa.bat.": "Run Setup.bat to connect or reselect your PC; use Install.bat to install dependencies.",
    "Controlla il volume interno di Spotify senza muovere il cursore.": "Control Spotify's internal volume without moving the pointer.",
    "Ricollega l'account e scegli il PC": "Reconnect your account and select the PC",
    "Volume iniziale, da 0 a 100": "Initial volume, from 0 to 100",
    "Mantieni un volume fisso": "Keep a fixed volume",
    "Intervallo di controllo in secondi (minimo 2)": "Check interval in seconds (minimum 2)",
    "Installazione delle dipendenze…": "Installing dependencies…",
    "Installazione completata. Ora apri Start.bat.": "Installation complete. Now open Start.bat.",
    "Installazione non riuscita. Controlla i messaggi qui sopra.": "Installation failed. Check the messages above.",
    "Serve Windows per controllare Spotify con questo programma.": "This program requires Windows to control Spotify.",
    "Errore: ": "Error: ",
    "Premi Invio per chiudere…": "Press Enter to close…",
}

# argparse uses English message keys; keep its help/errors localized too.
ITALIAN_CLI = {
    'usage: ': 'uso: ',
    'options': 'opzioni',
    'positional arguments': 'argomenti posizionali',
    'show this help message and exit': 'mostra questo messaggio ed esce',
    '%(prog)s: error: %(message)s\n': '%(prog)s: errore: %(message)s\n',
    'unrecognized arguments: %s': 'argomenti non riconosciuti: %s',
    'invalid choice: %(value)r (choose from %(choices)s)': 'scelta non valida: %(value)r (scegli tra %(choices)s)',
    'invalid %(type)s value: %(value)r': 'valore %(type)s non valido: %(value)r',
    'expected one argument': 'è richiesto un argomento',
    'the following arguments are required: %s': 'sono richiesti questi argomenti: %s',
    'argument %(argument_name)s: %(message)s': 'argomento %(argument_name)s: %(message)s',
}


def tr(message):
    return ENGLISH.get(message, message) if LANGUAGE == "en" else ITALIAN_CLI.get(message, message)


def set_language(language):
    global LANGUAGE
    if language not in ("it", "en"):
        raise ValueError("Language must be it or en")
    LANGUAGE = language


def choose_language():
    global LANGUAGE
    try:
        saved = json.loads((ROOT / "preferences.json").read_text(encoding="utf-8")).get("language", "it")
    except (OSError, ValueError):
        saved = "it"
    if saved not in ("it", "en"):
        saved = "it"
    print("SPOTIFY VOLUME LOCK\n")
    print("1. Italiano\n2. English")
    default = "1" if saved == "it" else "2"
    while True:
        answer = input(f"Lingua / Language [Invio / Enter = {default}]: ").strip().casefold()
        if not answer:
            answer = default
        if answer in ("1", "it", "italiano", "2", "en", "english"):
            LANGUAGE = "it" if answer in ("1", "it", "italiano") else "en"
            (ROOT / "preferences.json").write_text(json.dumps({"language": LANGUAGE}, indent=2), encoding="utf-8")
            return LANGUAGE
        print("Digita 1 o 2 e premi Invio. / Type 1 or 2 and press Enter.")

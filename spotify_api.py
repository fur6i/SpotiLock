"""Spotify Web API, PKCE e credenziali cifrate con Windows DPAPI."""
import base64
import ctypes
import hashlib
import json
import os
import secrets
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, parse_qs
from urllib.request import Request, urlopen

from app_paths import data_root
from i18n import tr

ROOT = data_root()
REDIRECT = 'http://127.0.0.1:8765/callback'
SCOPES = 'user-read-playback-state user-modify-playback-state'


class ApiError(RuntimeError):

    def __init__(self, message, retry_after=10):
        super().__init__(message)
        self.retry_after = retry_after

def protect(data, decrypt=False):
    from ctypes import wintypes

    class Blob(ctypes.Structure):
        _fields_ = [('size', wintypes.DWORD), ('data', ctypes.POINTER(ctypes.c_ubyte))]
    buffer = (ctypes.c_ubyte * len(data)).from_buffer_copy(data)
    source, result = (Blob(len(data), buffer), Blob())
    crypt = ctypes.WinDLL('crypt32', use_last_error=True)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    function = crypt.CryptUnprotectData if decrypt else crypt.CryptProtectData
    function.argtypes = [
        ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob),
    ]
    function.restype = wintypes.BOOL
    if not function(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(result)):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return ctypes.string_at(result.data, result.size)
    finally:
        kernel.LocalFree(result.data)

def http(method, url, form=None, token=None):
    headers = {'Accept': 'application/json'}
    data = None
    if form is not None:
        data = urlencode(form).encode()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    if token:
        headers['Authorization'] = 'Bearer ' + token
    try:
        with urlopen(Request(url, data=data, headers=headers, method=method), timeout=8) as reply:
            body = reply.read()
            return json.loads(body) if body else {}
    except HTTPError as exc:
        if exc.code == 429:
            try:
                delay = max(5, float(exc.headers.get('Retry-After', '60')))
            except ValueError:
                delay = 60
            raise ApiError(tr('Limite richieste Spotify: attendo prima di riprovare.'), delay) from None
        messages = {
            401: tr("Accesso scaduto: riavvia il programma con --setup per ricollegare l'account."),
            403: tr("Accesso negato: verifica Premium e l'accesso all'app nel Developer Dashboard."),
            404: tr('PC non disponibile: avvia un brano su Spotify in questo PC.'),
            400: tr('Configurazione non valida: controlla Client ID e indirizzo di ritorno.'),
        }
        error = ApiError(
            messages.get(exc.code, tr('Spotify ha risposto con errore {0}.').format(exc.code))
        )
        error.status = exc.code
        raise error from None
    except (URLError, TimeoutError, OSError):
        raise ApiError(tr('Connessione a Spotify assente. Riprovo automaticamente.')) from None

class SpotifyAPI:

    def __init__(self, config):
        self.config = config
        try:
            self.token = json.loads(protect((ROOT / 'accesso.dat').read_bytes(), decrypt=True))
        except (OSError, ValueError):
            raise ApiError(tr("Collegamento mancante: riapri SpotifyVolumeLock.exe per configurare l'account.")) from None

    def save_token(self, reply):
        reply.setdefault('refresh_token', self.token.get('refresh_token'))
        reply['expires_at'] = time.time() + reply.get('expires_in', 3600)
        self.token = reply
        (ROOT / 'accesso.dat').write_bytes(protect(json.dumps(reply).encode()))

    def refresh(self):
        reply = http('POST', 'https://accounts.spotify.com/api/token', {
            'grant_type': 'refresh_token',
            'refresh_token': self.token['refresh_token'],
            'client_id': self.config['client_id'],
        })
        self.save_token(reply)

    def call(self, method, path):
        if time.time() >= self.token.get('expires_at', 0) - 60:
            self.refresh()
        try:
            return http(method, 'https://api.spotify.com/v1/' + path, token=self.token['access_token'])
        except ApiError as exc:
            if getattr(exc, 'status', None) != 401:
                raise
            self.refresh()
            return http(method, 'https://api.spotify.com/v1/' + path, token=self.token['access_token'])

    def devices(self):
        return self.call('GET', 'me/player/devices').get('devices', [])

    def device(self):
        devices = self.devices()
        candidates = [d for d in devices if d.get('id') == self.config['device_id']]
        if not candidates:
            # L'ID può cambiare: recuperiamo solo lo stesso PC, senza ambiguità.
            candidates = [
                d for d in devices
                if d.get('name') == self.config['device_name']
                and d.get('type', '').casefold() == 'computer'
            ]
        if len(candidates) != 1:
            raise ApiError(tr('PC non disponibile o ambiguo: apri Spotify oppure riavvia con --setup.'))
        device = candidates[0]
        if (
            not device.get('id')
            or device.get('is_restricted')
            or device.get('supports_volume') is False
            or device.get('volume_percent') is None
        ):
            raise ApiError(tr('Questo dispositivo non consente il controllo del volume tramite Spotify.'))
        return device

    def set_volume(self, device_id, value):
        if not 0 <= value <= 100:
            raise ValueError(tr('Volume fuori intervallo'))
        self.call('PUT', 'me/player/volume?' + urlencode({
            'device_id': device_id,
            'volume_percent': round(value),
        }))

def authorize(client_id):
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
    state = secrets.token_urlsafe(32)
    result = {}

    class Callback(BaseHTTPRequestHandler):

        def log_message(self, *args):
            pass  # Evita di stampare il codice di autorizzazione nei log HTTP.

        def do_GET(self):
            parsed = urlsplit(self.path)
            query = parse_qs(parsed.query)
            if parsed.path != '/callback' or query.get('state') != [state]:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(tr('Richiesta non valida.').encode())
                return
            result.update(query)
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(tr('Puoi chiudere questa scheda e tornare al terminale.').encode())
    with HTTPServer(('127.0.0.1', 8765), Callback) as server:
        server.timeout = 0.5
        url = 'https://accounts.spotify.com/authorize?' + urlencode({
            'client_id': client_id,
            'response_type': 'code',
            'redirect_uri': REDIRECT,
            'scope': SCOPES,
            'state': state,
            'code_challenge_method': 'S256',
            'code_challenge': challenge,
        })
        print(tr('Apro il browser per collegare Spotify. Se non si apre, copia questo indirizzo:\n') + url)
        webbrowser.open(url)
        deadline = time.monotonic() + 300
        while not result and time.monotonic() < deadline:
            server.handle_request()
    if 'code' not in result:
        raise ApiError(tr('Collegamento annullato o scaduto. Riapri SpotifyVolumeLock.exe per riprovare.'))
    return http('POST', 'https://accounts.spotify.com/api/token', {
        'grant_type': 'authorization_code',
        'code': result['code'][0],
        'redirect_uri': REDIRECT,
        'client_id': client_id,
        'code_verifier': verifier,
    })

def read_config():
    try:
        return json.loads((ROOT / 'config.json').read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}

def saved_client_id():
    try:
        return json.loads((ROOT / 'client.json').read_text(encoding='utf-8'))['client_id']
    except (OSError, ValueError, KeyError):
        return read_config().get('client_id')

def configure(client_id=None):
    print(tr('SPOTIFY VOLUME LOCK · Collegamento ufficiale\n'))
    client_id = client_id or saved_client_id()
    if client_id:
        print(tr('Uso il Client ID già salvato.\n'))
    else:
        print(tr("1. Crea un'app su https://developer.spotify.com/dashboard"))
        print(tr('2. Inserisci questo Redirect URI: ') + REDIRECT)
        print(tr('3. Seleziona Web API e copia il Client ID (non serve Client Secret).\n'))
        client_id = input('Client ID: ').strip()
    if len(client_id) != 32 or any((c not in '0123456789abcdefABCDEF' for c in client_id)):
        raise ApiError(tr("Client ID non valido: copia i 32 caratteri dalle impostazioni dell'app."))
    # Salvalo prima del browser, anche se l'utente interrompe il collegamento.
    (ROOT / 'client.json').write_text(
        json.dumps({'client_id': client_id}, indent=2), encoding='utf-8'
    )
    reply = authorize(client_id)
    api = SpotifyAPI.__new__(SpotifyAPI)
    api.config = {'client_id': client_id}
    api.token = dict(reply, expires_at=time.time() + reply.get('expires_in', 3600))
    while True:
        devices = [
            d for d in api.devices()
            if d.get('type', '').casefold() == 'computer'
            and d.get('id')
            and not d.get('is_restricted')
            and d.get('supports_volume') is not False
            and d.get('volume_percent') is not None
        ]
        local_name = os.environ.get('COMPUTERNAME', '').casefold()
        local_devices = [
            d for d in devices
            if local_name and d.get('name', '').casefold() == local_name
        ]
        if len(local_devices) == 1:
            device = local_devices[0]
            print(tr('Questo PC riconosciuto: {0}.').format(device['name']))
            break
        print(tr('Collegamento riuscito. Ora scegli il computer da controllare.'))
        for i, device in enumerate(devices, 1):
            print(tr('{0}. {1} · volume {2}%').format(i, device['name'], device['volume_percent']))
        print(tr('DIGITA il numero a sinistra del nome del tuo PC, poi premi INVIO.'))
        print(tr('Esempio: se vedi «1. Il mio PC», digita 1 sulla tastiera e premi Invio. Non serve fare clic.'))
        print(tr("Invio senza numero aggiorna l'elenco · Q annulla."))
        answer = input(tr('Numero del PC → ')).strip()
        if answer.casefold() == 'q':
            raise ApiError(tr('Configurazione annullata.'))
        if answer.isdigit() and 1 <= int(answer) <= len(devices):
            device = devices[int(answer) - 1]
            break
        if answer:
            print(tr('Scelta non valida: inserisci il numero mostrato a sinistra del nome del PC.'))
        else:
            print(tr("Apri Spotify e avvia un brano su questo PC se non compare nell'elenco."))
    api.config.update(device_id=device['id'], device_name=device['name'])
    api.save_token(reply)
    (ROOT / 'config.json').write_text(json.dumps(api.config, indent=2), encoding='utf-8')
    print(tr('Collegamento completato. Apro il pannello di controllo…'))

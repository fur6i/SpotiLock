"""Controllo del volume interno tramite Spotify Web API; nessun clic sintetico."""
import argparse
import math
import threading
import time

from i18n import choose_language, set_language, tr
from spotify_api import ROOT, ApiError, SpotifyAPI, configure, read_config


class Controller:
    """Stato condiviso: serializza richieste e ignora letture precedenti ai comandi."""

    def __init__(self, api, target=None, fixed=False, interval=3):
        self.api, self.interval = api, interval
        self.lock = threading.Lock()
        self.wake, self.stop = threading.Event(), threading.Event()
        self.target, self.fixed = target, fixed
        self.current, self.connected = None, False
        self.status = tr('Collegamento ufficiale a Spotify')
        self.version = 0
        self.explicit = target is not None
        self.user_input_at = 0
        self.eligible = False
        self.pending = None
        self.blocked = False
        self.cooldown = 0
        self.events = []

    def command(self, action):
        with self.lock:
            if action[0] == 'volume':
                self.target, self.fixed = action[1:]
                self.target = round(self.target)
                self.explicit = True
                self.version += 1
                self.pending = None
                self.blocked = False
                self.status = tr('Invio del volume richiesto…')
            elif action[0] == 'mode':
                self.fixed = action[1]
                self.version += 1
                self.user_input_at = 0
        self.wake.set()

    def input(self, allowed, eligible):
        with self.lock:
            self.eligible = eligible
            if allowed:
                self.user_input_at = time.monotonic()

    def snapshot(self):
        with self.lock:
            events, self.events = (self.events, [])
            return ((self.target, self.current, self.fixed, self.connected, self.eligible, self.status), events)

    def tick(self):
        started = time.monotonic()
        with self.lock:
            version = self.version
        device = self.api.device()
        current = device['volume_percent']
        with self.lock:
            self.current, self.connected = (current, True)
            # Un comando digitato durante la richiesta deve prevalere sulla lettura.
            if version != self.version:
                return
            if self.target is None:
                self.target = current
            if abs(current - self.target) < 0.5:
                self.pending = None
                self.explicit = False
                self.blocked = False
                self.user_input_at = 0
                self.status = tr('Volume confermato · ') + device['name']
                return
            if self.pending is not None:
                requested, sent_at = self.pending
                if started - sent_at < max(8, self.interval * 2):
                    self.status = tr('In attesa della conferma di Spotify')
                    return
                self.pending = None
                self.blocked = True
                self.explicit = False
                self.status = tr('Volume non applicato: riprova con V o + / −')
                self.events.append(tr('Spotify non ha confermato il volume. Non ripeto il comando in continuazione.'))
            if self.blocked:
                return
            if (
                not self.explicit
                and not self.fixed
                and self.eligible
                and self.user_input_at > started - self.interval - 1
            ):
                self.target = current
                self.user_input_at = 0
                self.status = tr('Volume scelto in Spotify acquisito')
                return
            target = self.target
            self.status = tr('Invio del volume richiesto…')
        if self.stop.is_set():
            return
        self.api.set_volume(device['id'], target)
        with self.lock:
            if self.version == version:
                self.pending = (target, time.monotonic())
                self.explicit = False
                self.status = tr('Comando inviato · verifico il volume')

    def run(self):
        while not self.stop.is_set():
            self.wake.clear()
            now = time.monotonic()
            if now >= self.cooldown:
                try:
                    self.tick()
                except ApiError as exc:
                    self.cooldown = time.monotonic() + exc.retry_after
                    with self.lock:
                        if self.status != str(exc):
                            self.events.append(str(exc))
                        self.status = str(exc)
                        self.connected = False
                except Exception as exc:
                    with self.lock:
                        self.status = tr('Errore del collegamento: ') + type(exc).__name__
                        self.connected = False
                    self.cooldown = time.monotonic() + 10
            wait = max(self.interval, self.cooldown - time.monotonic())
            self.wake.wait(wait)
            # I comandi possono svegliare il thread, ma non saltare le attese API.
            if self.cooldown > time.monotonic() and not self.stop.is_set():
                self.stop.wait(min(self.interval, self.cooldown - time.monotonic()))


def volume(value):
    result = float(value.replace(',', '.'))
    if not math.isfinite(result) or not 0 <= result <= 100:
        raise argparse.ArgumentTypeError(tr('Scegli un numero da 0 a 100'))
    return round(result)

def main():
    language_parser = argparse.ArgumentParser(add_help=False)
    language_parser.add_argument('--lang', choices=('it', 'en'))
    language_args, _ = language_parser.parse_known_args()
    if language_args.lang:
        set_language(language_args.lang)
    else:
        choose_language()
    argparse._ = tr
    parser = argparse.ArgumentParser(
        description=tr('Controlla il volume interno di Spotify senza muovere il cursore.')
    )
    parser.add_argument('--lang', choices=('it', 'en'), help='Italiano / English')
    parser.add_argument(
        '--configura', '--setup', action='store_true',
        help=tr("Ricollega l'account e scegli il PC"),
    )
    parser.add_argument(
        '--client-id',
        help=tr("Sostituisce il Client ID salvato e ricollega l'account"),
    )
    parser.add_argument('--volume', type=volume, help=tr('Volume iniziale, da 0 a 100'))
    parser.add_argument('--fisso', '--fixed', action='store_true', help=tr('Mantieni un volume fisso'))
    parser.add_argument(
        '--intervallo', '--interval', type=float, default=3, metavar=tr('SECONDI'),
        help=tr('Intervallo di controllo in secondi (minimo 2)'),
    )
    args = parser.parse_args()
    if not math.isfinite(args.intervallo) or args.intervallo < 2:
        parser.error(tr("L'intervallo deve essere di almeno 2 secondi"))
    try:
        config = read_config()
        if (
            args.configura
            or args.client_id
            or not all(config.get(key) for key in ('client_id', 'device_id', 'device_name'))
            or not (ROOT / 'accesso.dat').exists()
        ):
            configure(args.client_id)
            config = read_config()
        api = SpotifyAPI(config)
        from input_gate import InputGate
        from terminal_ui import TerminalUI
        gate, ui = InputGate(), TerminalUI()
        controller = Controller(api, args.volume, args.fisso, args.intervallo)
        worker = threading.Thread(target=controller.run, daemon=True)
        ui.start(args.volume, args.fisso)
        worker.start()
        reconnect = False
        try:
            running = True
            while running:
                state, events = controller.snapshot()
                for message in events:
                    ui.log(message)
                for action in ui.poll(state[0], state[2]):
                    if action[0] == 'setup':
                        reconnect = True
                        running = False
                        break
                    if action[0] == 'quit':
                        running = False
                        break
                    controller.command(action)
                allowed = gate.allowed()
                _, foreground, hovered, spotify = gate.snapshot()
                controller.input(allowed, bool(spotify and foreground and (foreground == hovered)))
                ui.update(*state)
                time.sleep(0.05)
        finally:
            controller.stop.set()
            controller.wake.set()
            worker.join(timeout=1)
            ui.stop()
            if not reconnect:
                ui.finish(tr('Controllo volume terminato.'))
        if reconnect:
            return 2
    except KeyboardInterrupt:
        pass
    except (ApiError, OSError, ValueError, KeyError, ImportError) as exc:
        print(str(exc))
        print(tr("Riapri SpotifyVolumeLock.exe per riprovare. Per ricollegare l'account usa --setup."))
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

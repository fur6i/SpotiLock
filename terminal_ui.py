"""Interfaccia terminale: input non bloccante, il controllo continua durante la digitazione."""
from collections import deque
import math
import time

from i18n import tr

class ControlMenu:

    def __init__(self):
        self.editing = False
        self.buffer = ''
        self.edit_fixed = False
        self.message = ''
        self.extended_key = False

    def handle(self, key, target, fixed):
        if self.extended_key:
            self.extended_key = False
            return None
        if key in ('\x00', 'à'):
            self.extended_key = True
            return None
        if key == '\x03' or key.casefold() == 'q':
            return ('quit',)
        if self.editing:
            if key == '\x1b':
                self.editing = False
                self.message = tr('Modifica annullata.')
            elif key == '\x08':
                self.buffer = self.buffer[:-1]
            elif key == '\r':
                try:
                    value = float(self.buffer.replace(',', '.')) if self.buffer else target
                    if value is None or not math.isfinite(value) or (not 0 <= value <= 100):
                        raise ValueError
                except ValueError:
                    self.message = tr('Inserisci un numero da 0 a 100.')
                    return None
                self.editing = False
                self.message = tr('Volume aggiornato.')
                return ('volume', value, self.edit_fixed)
            elif key in '0123456789.,' and len(self.buffer) < 8:
                self.buffer += key
                self.message = ''
            return None
        key = key.casefold()
        if key in ('v', 'f'):
            self.editing = True
            self.buffer = ''
            self.edit_fixed = True if key == 'f' else fixed
            self.message = ''
        elif key == 'a':
            self.message = tr('Puoi cambiare il volume anche dentro Spotify.')
            return ('mode', False)
        elif key == 'r':
            return ('setup',)
        elif key in ('+', '=', '-'):
            if target is None:
                self.message = tr('Prima seleziona un volume con V oppure apri Spotify.')
                return None
            value = max(0, min(100, target + (5 if key in ('+', '=') else -5)))
            self.message = tr('Volume aggiornato.')
            return ('volume', value, fixed)
        return None

class TerminalUI:

    def __init__(self, console=None, keyboard=None):
        from rich.console import Console
        if keyboard is None:
            import msvcrt
            keyboard = msvcrt
        self.keyboard = keyboard
        self.console = console or Console()
        self.menu = ControlMenu()
        self.events = deque(maxlen=3)
        self.live = None
        self.status = tr('In attesa di Spotify')
        self.connected = False
        self.target = None
        self.current = None
        self.fixed = False
        self.allowed = False

    def start(self, target, fixed):
        from rich.live import Live
        self.target, self.fixed = target, fixed
        self.live = Live(
            self.render(), console=self.console, screen=True,
            auto_refresh=False, vertical_overflow='crop',
        )
        self.live.start(refresh=True)

    def poll(self, target, fixed):
        actions = []
        for _ in range(32):
            if not self.keyboard.kbhit():
                break
            action = self.menu.handle(self.keyboard.getwch(), target, fixed)
            if action is not None:
                actions.append(action)
                if action[0] == 'volume':
                    target, fixed = action[1:]
                elif action[0] == 'mode':
                    fixed = action[1]
                elif action[0] == 'quit':
                    break
        return actions

    def log(self, message):
        self.events.append((time.strftime('%H:%M:%S'), str(message)))

    def update(self, target, current, fixed, connected, allowed, status=None):
        self.target, self.current, self.fixed = target, current, fixed
        self.connected, self.allowed = connected, allowed
        self.status = status or (tr('Spotify collegato') if connected else tr('In attesa di Spotify'))
        if self.live:
            self.live.update(self.render(), refresh=True)

    def render(self):
        from rich.console import Group
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text
        green, muted = '#1DB954', '#9BA3AE'
        header = Text('SPOTIFY  /  VOLUME LOCK', style=f'bold {green}')
        header.append(tr('\nIl tuo volume, sotto controllo.'), style=muted)
        header.append('\n' + tr('Avviso: chiudi Spotify sul telefono per evitare possibili conflitti.'), style='yellow')
        volume = Text('—' if self.target is None else f'{self.target:g}%', style='bold white', justify='center')
        count = 0 if self.target is None else round(self.target * 28 / 100)
        bar = Text('─' * count, style=f'bold {green}', justify='center')
        bar.append('─' * (28 - count), style='#39414D')
        bar.append(tr('\nVOLUME DA MANTENERE'), style=muted)
        details = Table.grid(padding=(0, 2), expand=True)
        details.add_column(style=muted)
        details.add_column(justify='right')
        details.add_row(tr('Modalità'), Text(tr('Fissa') if self.fixed else tr('Interattiva'), style=f'bold {green}'))
        details.add_row(tr('Volume in Spotify'), Text('—' if self.current is None else f'{self.current:.1f}%'))
        warning = tr('non applicato') in self.status.casefold()
        details.add_row(tr('Stato'), Text(self.status, style=green if self.connected and (not warning) else 'yellow'))
        description = tr('Mantiene il valore scelto anche quando usi Spotify.') if self.fixed else tr('Accetta i tuoi cambi con Spotify attivo e il mouse sopra.')
        if self.allowed and (not self.fixed):
            description = tr('Input rilevato in Spotify · modifica del volume consentita.')
        commands = Table.grid(padding=(0, 2), expand=True)
        commands.add_column(style=f'bold {green}', width=7)
        commands.add_column()
        for key, label in (
            ('F', tr('Scegli volume fisso')),
            ('V', tr('Cambia volume scelto')),
            ('+ / −', tr('Aumenta / diminuisci di 5 punti')),
            ('A', tr('Modalità interattiva')),
            ('R', tr('Ricollega account / scegli PC')),
            ('Q', tr('Esci')),
        ):
            commands.add_row(key, label)
        if self.menu.editing:
            title = tr('Scegli volume fisso') if self.menu.edit_fixed else tr('Cambia volume')
            default = '' if self.target is None else tr(' · Invio vuoto mantiene {0:g}%').format(self.target)
            prompt = Text(f'{title} → {self.menu.buffer}▏', style=f'bold {green}')
            prompt.append(tr('\n0–100 · Invio conferma · Esc annulla{0}').format(default), style=muted)
        else:
            prompt = Text(self.menu.message or tr('Premi un comando per iniziare.'), style=muted)
        if self.menu.editing and self.menu.message:
            prompt.append(f'\n{self.menu.message}', style='yellow')
        events = Text()
        for index, (stamp, message) in enumerate(self.events):
            if index:
                events.append('\n')
            events.append(f'{stamp}  ', style=muted)
            events.append(message)
        if not self.events:
            events.append(tr('Collega il tuo account e seleziona questo PC.'), style=muted)
        body = Group(
            header, Text(''), volume, bar, Text(''), details,
            Text(description, style=muted), Text(''), commands, Text(''), prompt,
        )
        panels = [Panel(
            body, border_style=green, padding=(1, 2),
            subtitle=Text(tr('Solo volume interno Spotify'), style=muted),
        )]
        if self.console.height >= 28:
            panels.append(Panel(events, title=tr('Attività recente'), border_style='#39414D', padding=(0, 2)))
        return Group(*panels)

    def stop(self):
        if self.live:
            self.live.stop()
            self.live = None

    def finish(self, message, error=False):
        self.console.print(message, style='red' if error else '#1DB954', markup=False)

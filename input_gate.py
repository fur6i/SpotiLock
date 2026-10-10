"""Riconosce l'input dell'utente con Spotify attivo e il puntatore sulla finestra."""

import time


class InputGate:
    """Autorizza brevemente un cambio dopo input con Spotify attivo e sotto il mouse."""

    def __init__(self, snapshot=None, clock=time.monotonic):
        self.snapshot = snapshot or WindowsInput().snapshot
        self.clock = clock
        self.last_tick = self.snapshot()[0]
        self.input_window = None
        self.deadline = 0.0
        self.ignore_until = 0.0

    def allowed(self, expected_window=None):
        tick, foreground, hovered, is_spotify = self.snapshot()
        now = self.clock()
        if now < self.ignore_until:
            self.last_tick = tick
            self.input_window = None
            return False
        eligible = bool(foreground and hovered == foreground and is_spotify
                        and (expected_window is None or foreground == expected_window))
        if tick is None:
            self.input_window = None
            return False
        if tick != self.last_tick:
            self.last_tick = tick
            self.input_window = foreground if eligible else None
            self.deadline = now + 0.3 if eligible else 0.0
        if not eligible:
            self.input_window = None
        return eligible and self.input_window == foreground and now < self.deadline

    def suppress(self):
        """Non scambiare il clic del programma per un cambio fatto dall'utente."""
        self.last_tick = self.snapshot()[0]
        self.input_window = None
        self.deadline = 0.0
        self.ignore_until = self.clock() + 0.3


class WindowsInput:
    """Legge finestra attiva, finestra sotto il mouse e timestamp dell'ultimo input."""

    def __init__(self):
        import ctypes
        from ctypes import wintypes
        import psutil
        self.ctypes, self.wintypes, self.psutil = ctypes, wintypes, psutil

        class LastInputInfo(ctypes.Structure):
            _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]

        self.info_type = LastInputInfo
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        signatures = {
            "GetLastInputInfo": ([ctypes.POINTER(LastInputInfo)], wintypes.BOOL),
            "GetForegroundWindow": ([], wintypes.HWND),
            "GetCursorPos": ([ctypes.POINTER(wintypes.POINT)], wintypes.BOOL),
            "WindowFromPoint": ([wintypes.POINT], wintypes.HWND),
            "GetAncestor": ([wintypes.HWND, wintypes.UINT], wintypes.HWND),
            "GetWindowThreadProcessId":
                ([wintypes.HWND, ctypes.POINTER(wintypes.DWORD)], wintypes.DWORD),
        }
        for name, (arguments, result) in signatures.items():
            function = getattr(self.user32, name)
            function.argtypes, function.restype = arguments, result

    def snapshot(self):
        c, w, api = self.ctypes, self.wintypes, self.user32
        info = self.info_type()
        info.cbSize = c.sizeof(info)
        if not api.GetLastInputInfo(c.byref(info)):
            return None, None, None, False
        foreground = api.GetForegroundWindow()
        point = w.POINT()
        if not foreground or not api.GetCursorPos(c.byref(point)):
            return info.dwTime, None, None, False
        foreground = api.GetAncestor(foreground, 2)  # GA_ROOT: finestra principale.
        hovered = api.WindowFromPoint(point)
        hovered = api.GetAncestor(hovered, 2) if hovered else None
        pid = w.DWORD()
        api.GetWindowThreadProcessId(foreground, c.byref(pid))
        try:
            is_spotify = bool(pid.value and
                              self.psutil.Process(pid.value).name().casefold() == "spotify.exe")
        except (self.psutil.Error, OSError):
            is_spotify = False
        return info.dwTime, foreground, hovered, is_spotify


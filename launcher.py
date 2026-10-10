"""Standard-library launcher: select language before installation or setup."""
import os
import sys
from i18n import choose_language, tr


def main():
    language = choose_language()
    if os.name != "nt":
        print(tr("Serve Windows per controllare Spotify con questo programma."))
        return 1
    arguments = [argument for argument in sys.argv[1:] if argument != "--setup"]
    if "--setup" in sys.argv:
        arguments.append("--configura")
    from spotify_volume_lock import main as run_app
    while True:
        sys.argv = ["spotify_volume_lock.py", *arguments, "--lang", language]
        result = run_app() or 0
        if result == 0:
            return 0
        if result != 2:
            answer = input(tr("Premi R per ricollegare l'account qui, oppure Invio per chiudere: ")).strip()
            if answer.casefold() != 'r':
                return result
        arguments = [argument for argument in arguments if argument not in ('--configura', '--setup')]
        arguments.append('--configura')


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, EOFError):
        raise SystemExit(0)
    except OSError as exc:
        print(tr("Errore: ") + str(exc))
        input(tr("Premi Invio per chiudere…"))
        raise SystemExit(1)

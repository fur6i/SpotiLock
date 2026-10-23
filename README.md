# SpotiLock

<p align="center">
  <img src="assets/spotilock-logo.png" alt="SpotiLock logo" width="128">
</p>

[Italiano](README.it.md) · **English**

A small Windows terminal app that keeps Spotify's **internal player volume** at
your chosen level. It uses the official Spotify Web API, without moving the
pointer, focusing Spotify, or modifying its installation. Commands also work
when Spotify's window is minimized, provided the device is available to Spotify.

## Requirements

- Windows 10 or 11 (64 bit). No Python installation required for the executable.
- Spotify Premium, an Internet connection, and Spotify running on your PC.
- A personal app in the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).

## Quick start

1. Download **SpotiLock.exe** and keep it in a writable folder.
2. Open Spotify on this PC and play a track to make it available.
3. Double-click **SpotiLock.exe**. Type **1** for Italiano or **2** for English and press **Enter**. Enter without a number keeps the previous language.
4. On the first run, account setup starts automatically. Afterwards the control panel opens in the same window.
5. Future launches reuse your saved Client ID, account and PC automatically.

There is a single executable. Python and dependencies are bundled; no installer or batch files are needed. Press **R** in the panel to reconnect or choose another PC.

### One-time Spotify connection

Create an app in the Developer Dashboard, select **Web API**, and register
this exact redirect URI:

```text
http://127.0.0.1:8765/callback
```

Copy the **Client ID** into the terminal and press **Enter**. A Client Secret is
not required. Approve the connection in your browser, then return to the terminal.
The Client ID is saved immediately, even if setup is interrupted.

**Device selection is automatic when Spotify's device name matches your Windows
PC name.** Otherwise, the program shows numbered computers. **Type the number
next to your own PC and press Enter on your keyboard. Do not click the number.**
For example, for `1. My PC`, type `1` and press **Enter**. Press Enter with no
number to refresh the list, or type `Q` to cancel.

After setup, the control panel opens immediately. Future runs of **SpotifyVolumeLock.exe**
reuse the saved account and device without asking for the Client ID again.
Press **R** in the panel to reconnect or choose another PC.

## Controls

| Key | Action |
|---|---|
| **F** | Choose a fixed volume: type 0–100 and press Enter. |
| **V** | Change the target volume while keeping the current mode. |
| **+ / −** | Increase / decrease the target by 5 percentage points. |
| **A** | Enable interactive mode. |
| **Esc** | Cancel a value being entered. |
| **R** | Reconnect the account / select a PC, in the same window. |
| **Q** | Quit. |

Fixed mode restores the target when Spotify's volume changes. Interactive mode
accepts changes after user input while Spotify is foreground and the pointer is
over its window. Console commands work in either mode regardless of window visibility.

The language selector appears before setup and the control panel. Setup prompts,
the browser callback, controls, status messages and application errors use your
chosen language. Messages produced by Python or pip itself follow those tools' settings.

## Timing and limitations

Close Spotify on your phone to avoid possible conflicts with the PC volume.
This notice also appears in the control panel.

The app reads the volume every **3 seconds** and checks that Spotify actually
applied each command. Changes made elsewhere may take a few seconds to be
corrected. Spotify's API limits and Internet availability can add delays;
the program respects API retry times.

Interactive detection is approximate: the API does not identify who changed the
volume. An automatic change coinciding with your input in Spotify can be accepted.
Choose **F** for a predictable fixed target.

Spotify must remain available as a Connect device. If it disappears, open it and
play a track on this PC. The program does not automatically start or transfer
playback. If a command is not confirmed within roughly 8–9 seconds, repeated
attempts stop; use **V** or **+ / −** to retry.

## Command line

```text
SpotiLock.exe --lang en --volume 70 --fixed
SpotiLock.exe --lang it --volume 70 --fisso
SpotiLock.exe --lang en --setup
SpotiLock.exe --lang en --client-id YOUR_NEW_CLIENT_ID
```

Omit `--lang` to show the language selector. Italian and English option aliases
are supported. `--interval` / `--intervallo` changes the polling interval;
values below 2 seconds are rejected.

## Development

```text
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Tests use simulated Spotify responses and do not require an account. Live
verification requires your own authorized account and selected device.
Account setup uses OAuth Authorization Code with PKCE; no Client Secret is stored.

[Spotify volume endpoint documentation](https://developer.spotify.com/documentation/web-api/reference/set-volume-for-users-playback)

This project is independent of Spotify.

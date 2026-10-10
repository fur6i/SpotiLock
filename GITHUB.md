# Pubblicare su GitHub / Publish on GitHub

## Italiano

1. Estrai FINAL-RELEASE.zip. Per usare il programma apri soltanto
   **SpotifyVolumeLock.exe**: scegli Italiano o English e segui le istruzioni.
2. Su GitHub crea un repository, per esempio `spotify-volume-lock`.
3. Apri **Add file → Upload files** e carica sorgenti, documentazione,
   `.gitignore`, `.gitattributes` e cartella `tests` nella radice del repository.
   Conferma con **Commit changes**. Non caricare l'eseguibile o lo ZIP nel codice.
4. Apri **Releases → Draft a new release**, crea il tag `v1.0.0`,
   aggiungi **SpotifyVolumeLock.exe** e **FINAL-RELEASE.zip** come allegati
   e premi **Publish release**.

L'archivio distribuito non contiene dati dell'account. Dopo aver usato il programma,
non caricare `client.json`, `config.json`, `preferences.json` o `accesso.dat`:
il caricamento dal sito non applica automaticamente `.gitignore`.

Codex non ha un account GitHub personale da invitare come collaboratore.
Per continuare a lavorare insieme, scarica o clona il repository e apri la sua
cartella come progetto nell'app Codex. In alternativa, crea un ambiente cloud
in Codex, collega GitHub e seleziona il repository.

## English

1. Extract FINAL-RELEASE.zip. To use the app, open only **SpotifyVolumeLock.exe**,
   choose Italiano or English, and follow the instructions.
2. Create a GitHub repository, for example `spotify-volume-lock`.
3. Use **Add file → Upload files** to upload the source files, documentation,
   `.gitignore`, `.gitattributes`, and `tests` folder into the repository root.
   Select **Commit changes**. Keep the executable and ZIP out of the source tree.
4. Open **Releases → Draft a new release**, create the `v1.0.0` tag,
   attach **SpotifyVolumeLock.exe** and **FINAL-RELEASE.zip**,
   then select **Publish release**.

The distributed archive contains no account data. After running the app,
do not upload `client.json`, `config.json`, `preferences.json`, or `accesso.dat`:
web uploads do not automatically apply `.gitignore`.

Codex has no personal GitHub account to invite as a collaborator.
Download or clone the repository and open its folder as a project in the Codex
app to keep working together. Alternatively, create a Codex cloud environment,
connect GitHub, and select the repository.

## Guide ufficiali / Official guides

- [Create a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)
- [Upload files](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)
- [Publish a release](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
- [Codex app](https://learn.chatgpt.com/docs/app)
- [Codex cloud](https://learn.chatgpt.com/docs/cloud)

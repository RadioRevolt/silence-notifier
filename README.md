# silence-notifier
Varsle teknisk om stillhet på streamen

## Oppsett

1. Klon kodelageret: `git clone ...`
2. Kopier `rtmbot.conf.template` og kall den `rtmbot.conf`
3. Lag en ny fil kalt `settings.yaml`
4. Rediger `rtmbot.conf`, spesifikt legg inn Slack-nøkkel
5. Rediger `settings.yaml`, og redefiner `channel` og `rr_api`. Redefiner også
   andre innstillinger du føler for å endra fra `settings_default.yaml`.
6. Lag et virtualenv: `virtualenv -p python3 venv` eller noe liknende
7. Tre inn i det virtuelle miljøet: `. venv/bin/activate`
8. Installer nødvendige pakker: `pip install -r requirements.txt`
9. Kopier `silence-notifier.service` inn i `/etc/systemd/system` og rediger
   filstien i den så den er riktig.
10. Kjør `sudo visudo /etc/visudo.d/silence-notifier.sudoers` og legg inn 
    innholdet fra fila `silence-notifier.sudoers` her i kodelageret.

## Kjøring

Skriptet kjøres med SystemD:

```sh
sudo /bin/systemctl start silence-notifier
```

og stoppes også med SystemD:

```sh
sudo /bin/systemctl stop silence-notifier
```

Disse kommandoene setter du til å kjøres i `transition`-funksjoner i fallback i
LiquidSoap. Du må bruke den absolutte filstien som ovenfor for at sudo-reglene
skal gjelde (siden hvem som helst kan lage et skript som heter systemctl).

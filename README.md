# Space Pillow · Piano social

Contenuti, registro e strumenti del piano editoriale Instagram di Space Pillow.
I file in `media/` sono pubblicati con GitHub Pages: Metricool li scarica da qui quando importa il CSV.

## Cosa c'è

| Cartella | Contenuto |
|---|---|
| `index.html` | Il piano da sfogliare: calendario, rubriche, anteprime di grafiche e reel. |
| `media/<NN>_<data>_<formato>_<tema>/` | Le grafiche (JPG 1080×1350 o 1080×1080) e i reel (MP4 1080×1920 + copertina) di ogni contenuto. |
| `data/registro.json` | Il registro di tutti i contenuti pubblicati o programmati: ID, data, rubrica, serie, tema, titolo, caption, foto usate. |
| `data/ciclo2_temi.json` | I 78 temi già riservati per il ciclo 2 (1 giugno – 27 novembre 2027) e il materiale da chiedere a HOPI. |
| `metricool/` | Il CSV pronto da importare in Metricool. |
| `tools/verifica.py` | Il controllo anti-doppioni. |
| `tools/esporta_metricool.py` | Genera il CSV per Metricool dal registro. |

## Le regole del piano

- **Ritmo:** 3 contenuti a settimana, martedì, giovedì e sabato. Un ciclo dura 26 settimane, cioè 78 contenuti.
  - Ciclo 1: dal 1 dicembre 2026 al 29 maggio 2027.
  - Ciclo 2: dal 1 giugno al 27 novembre 2027.
  - Ciclo 3: dal 30 novembre 2027.
- **Rubriche:** 7 fisse. Ogni mese ognuna esce due volte, tranne «Artigiani del riposo» che esce una volta: 13 contenuti al mese.
- **Testi:** quelli su prodotto, taglie, scatola, rituale, recensioni e azienda sono le frasi del sito, alla lettera. I testi nuovi sono solo domande, inviti, auguri e riferimenti a ricorrenze.
- **ID:** ogni contenuto ha un ID (`SP-C<ciclo>-<numero>`) e una chiave tema unica. Un tema usato non torna più. Se un argomento ritorna, ha una chiave nuova e un angolo diverso, ad esempio `tappa2-torcia` e poi `tappa2-autunno`.

## Come si prepara il ciclo 2 senza doppioni

1. Partire da `data/ciclo2_temi.json`: 78 date, ciascuna con rubrica, formato, serie e tema già assegnati.
2. Scrivere i contenuti nuovi in un file `nuovi.json`, con gli stessi campi del registro.
3. Lanciare il controllo:
   ```
   python3 tools/verifica.py --nuovi nuovi.json --temi data/ciclo2_temi.json
   ```
   Lo script blocca in questi casi:
   - ID, temi, titoli o date doppi;
   - caption troppo simili a una già usata (le frasi del sito non contano);
   - caption oltre i 2200 caratteri;
   - giorni diversi da martedì, giovedì e sabato.

   Segnala inoltre come avviso:
   - la stessa foto principale usata entro 28 giorni;
   - tre formati uguali di fila;
   - rubriche sbilanciate nel mese.
4. Quando è tutto a posto, aggiungere i nuovi contenuti a `data/registro.json` e caricare i media in `media/`.
5. Rigenerare il CSV:
   ```
   python3 tools/esporta_metricool.py --base https://UTENTE.github.io/REPO/
   ```

## Importare in Metricool

- Al momento dell'importazione, scegliere il formato data `YYYY-MM-DD` e il formato ora `HH:MM:SS`.
- Il CSV crea i contenuti come bozze. I reel fatti di sole foto sono muti: prima di approvarli si aggiunge la musica nell'app.
- Per pubblicare anche su Facebook: `--reti instagram,facebook`. Per programmarli direttamente, senza bozze: `--bozze no`.

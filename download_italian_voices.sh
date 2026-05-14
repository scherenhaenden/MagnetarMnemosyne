#!/usr/bin/env bash
set -euo pipefail

ASSETS_DIR="/Users/edwardflores/Projects/Development/MagnetarMnemosyne/assets/reference-voices-italian"
mkdir -p "$ASSETS_DIR"
cd "$ASSETS_DIR"

echo "Descargando voces/referencias italianas desde Internet Archive / LibriVox..."

download_archive_audio_as_wav() {
  local item="$1"
  local label="$2"
  local start="$3"
  local duration="${4:-15}"

  echo ""
  echo "=================================================="
  echo "Item:  $item"
  echo "Label: $label"
  echo "Start: $start"
  echo "=================================================="

  local xml="${item}_files.xml"
  local source_name="${label}_source"
  local wav_name="${label}_ref.wav"

  curl -L "https://archive.org/download/${item}/${item}_files.xml" -o "$xml"

  local file
  file="$(python3 - "$xml" <<'PY'
import sys
import xml.etree.ElementTree as ET

xml_path = sys.argv[1]
root = ET.parse(xml_path).getroot()

preferred = []
fallback = []

for file_el in root.findall("file"):
    name = file_el.attrib.get("name", "")
    lower = name.lower()

    if lower.endswith((".mp3", ".ogg", ".m4a")):
        fallback.append(name)

        if "128kb" in lower:
            preferred.append(name)
        elif lower.endswith(".mp3"):
            preferred.append(name)

candidates = preferred or fallback

if not candidates:
    raise SystemExit("No audio file found in files XML")

print(candidates[0])
PY
)"

  local ext="${file##*.}"
  local encoded_file
  encoded_file="$(python3 - "$file" <<'PY'
import sys, urllib.parse
print(urllib.parse.quote(sys.argv[1]))
PY
)"

  echo "Archivo elegido: $file"

  curl -L "https://archive.org/download/${item}/${encoded_file}" -o "${source_name}.${ext}"

  ffmpeg -y -i "${source_name}.${ext}" \
    -ss "$start" -t "$duration" \
    -ar 24000 -ac 1 \
    "$wav_name"

  echo "Generado: $wav_name"
}

# ==========================================================
# CENTRO / TOSCANA 01
# Dante Alighieri - La Divina Commedia
# Página: https://archive.org/details/divina_commedia_librivox
# Nota: referencia italiana clásica/toscana por autor y obra.
# ==========================================================

download_archive_audio_as_wav \
  "divina_commedia_librivox" \
  "it_centro_toscana_dante_01" \
  "00:01:00" \
  "15"


# ==========================================================
# CENTRO / TOSCANA 02
# Giovanni Boccaccio - Decameron, Giornata Prima
# Página: https://archive.org/details/decameron1_2406_librivox
# Nota: referencia florentina/toscana por autor y obra.
# ==========================================================

download_archive_audio_as_wav \
  "decameron1_2406_librivox" \
  "it_centro_toscana_boccaccio_02" \
  "00:01:00" \
  "15"


# ==========================================================
# NORTE / LOMBARDÍA 01
# Alessandro Manzoni - Gl'Inni sacri
# Página: https://archive.org/details/glinni_sacri_1701_librivox
# Nota: referencia norte/lombarda por autor.
# ==========================================================

download_archive_audio_as_wav \
  "glinni_sacri_1701_librivox" \
  "it_nord_lombardia_manzoni_01" \
  "00:00:35" \
  "15"


# ==========================================================
# NORTE / PIEMONTE-LIGURIA 02
# Edmondo De Amicis - Cuore
# Página: https://archive.org/details/cuore_fg_librivox
# Nota: referencia norte por autor y contexto de la obra.
# ==========================================================

download_archive_audio_as_wav \
  "cuore_fg_librivox" \
  "it_nord_deamicis_cuore_02" \
  "00:01:00" \
  "15"


# ==========================================================
# SUR / NÁPOLES 01
# Salvatore Di Giacomo - Mattinate Napoletane
# Página: https://archive.org/details/mattinate_napoletane_dl_librivox
# Nota: referencia napolitana por autor/tema. Buena para "sur".
# ==========================================================

download_archive_audio_as_wav \
  "mattinate_napoletane_dl_librivox" \
  "it_sud_napoli_digiacomo_01" \
  "00:00:45" \
  "15"


# ==========================================================
# SUR / NÁPOLES 02
# Salvatore Di Giacomo - Mattinate Napoletane
# Página: https://archive.org/details/mattinate_napoletane_dl_librivox
# Nota: segundo fragmento del mismo material napolitano.
# ==========================================================

download_archive_audio_as_wav \
  "mattinate_napoletane_dl_librivox" \
  "it_sud_napoli_digiacomo_02" \
  "00:03:00" \
  "15"


# ==========================================================
# SICILIA 01
# Giovanni Verga - Mastro Don Gesualdo
# Página: https://archive.org/details/mastro_don_gesualdo_1104_librivox
# Nota: referencia siciliana por autor y ambientación.
# ==========================================================

download_archive_audio_as_wav \
  "mastro_don_gesualdo_1104_librivox" \
  "it_sicilia_verga_mastro_01" \
  "00:00:45" \
  "15"


# ==========================================================
# SICILIA 02
# Luigi Pirandello - Il Fu Mattia Pascal
# Página: https://archive.org/details/mattia_pascal_1012_librivox
# Nota: referencia siciliana por autor.
# ==========================================================

download_archive_audio_as_wav \
  "mattia_pascal_1012_librivox" \
  "it_sicilia_pirandello_mattia_02" \
  "00:00:45" \
  "15"


# ==========================================================
# CERDEÑA 01
# Grazia Deledda - Canne al vento
# Página: https://archive.org/details/canne_al_vento_1609_librivox
# Nota: referencia sarda por autora y contenido.
# ==========================================================

download_archive_audio_as_wav \
  "canne_al_vento_1609_librivox" \
  "it_sardegna_deledda_canne_01" \
  "00:00:45" \
  "15"


# ==========================================================
# CERDEÑA 02
# Grazia Deledda - Canne al vento
# Página: https://archive.org/details/canne_al_vento_1609_librivox
# Nota: segundo fragmento sardo del mismo audiolibro.
# ==========================================================

download_archive_audio_as_wav \
  "canne_al_vento_1609_librivox" \
  "it_sardegna_deledda_canne_02" \
  "00:03:00" \
  "15"


echo ""
echo "Rutas absolutas:"
python3 - <<'PY'
import os, glob
for f in sorted(glob.glob("*_ref.wav")):
    print(os.path.abspath(f))
PY

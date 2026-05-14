#!/usr/bin/env bash
set -euo pipefail

ASSETS_DIR="/Users/edwardflores/Projects/Development/MagnetarMnemosyne/assets/reference-voices-england"
mkdir -p "$ASSETS_DIR"
cd "$ASSETS_DIR"

echo "Descargando voces/referencias de inglés de Inglaterra desde Internet Archive / LibriVox..."

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

download_archive_audio_as_wav "memoirsofsherlockholmesv3_1502_librivox" "en_england_london_sherlock_memoirs_01" "00:00:45" "15"
download_archive_audio_as_wav "oliver_twist_6_1707_librivox" "en_england_london_oliver_twist_02" "00:00:45" "15"
download_archive_audio_as_wav "pride_prejudice_krs_librivox" "en_england_south_austen_pride_01" "00:00:45" "15"
download_archive_audio_as_wav "prideandprejudice_1005_librivox" "en_england_south_austen_pride_02" "00:00:45" "15"
download_archive_audio_as_wav "wuthering_heights_rg_librivox" "en_england_yorkshire_wuthering_01" "00:00:45" "15"
download_archive_audio_as_wav "secret_garden_version2_librivox" "en_england_yorkshire_secret_garden_02" "00:00:45" "15"
download_archive_audio_as_wav "shirley_1006_librivox" "en_england_yorkshire_shirley_03" "00:00:45" "15"
download_archive_audio_as_wav "middlemarch_0810_librivox" "en_england_midlands_middlemarch_01" "00:00:45" "15"
download_archive_audio_as_wav "middlemarch_version2_1310_librivox" "en_england_midlands_middlemarch_02" "00:00:45" "15"
download_archive_audio_as_wav "adventuressherlockholmes_v4_1501_librivox" "en_england_general_sherlock_adventures_01" "00:00:45" "15"
download_archive_audio_as_wav "returnsherlockholmes_v3_1507_librivox" "en_england_general_sherlock_return_02" "00:00:45" "15"

echo ""
echo "Rutas absolutas:"
python3 - <<'PY'
import os, glob
for f in sorted(glob.glob("*_ref.wav")):
    print(os.path.abspath(f))
PY

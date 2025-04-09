# Thanks to atlas academy for this script!
# All credits to atlas
# Github: github.com/atlasacademy
# Website: atlasacademy.io
# Api: api.atlasacademy.io
# Apps: apps.atlasacademy.io

import re
import json5
import httpx

PLAY_STORE_URL = {
    "NA": "https://play.google.com/store/apps/details?id=com.aniplex.fategrandorder.en",
    "JP": "https://play.google.com/store/apps/details?id=com.aniplex.fategrandorder",
    "KR": "https://play.google.com/store/apps/details?id=com.netmarble.fgok",
    "TW": "https://play.google.com/store/apps/details?id=com.xiaomeng.fategrandorder",
}

VERSION_REGEX = re.compile(r"^\d+\.\d+\.\d+$")

def get_play_store_ver(region: str) -> str:
    url = PLAY_STORE_URL[region]
    response = httpx.get(url, follow_redirects=True)

    # Tentativa 1: regex simples no texto da página
    version_match = re.search(r'Current Version.*?>([\d.]+)<', response.text)
    if version_match and VERSION_REGEX.match(version_match.group(1)):
        return version_match.group(1)

    # Tentativa 2: AF_initDataCallback do Google
    for match in re.finditer(r"AF_initDataCallback\((.*?)\);", response.text):
        try:
            data = json5.loads(match.group(1))
            if (
                "data" in data
                and isinstance(data["data"], list)
            ):
                # Busca por strings com versão
                flat_data = str(data["data"])
                version_candidates = re.findall(r"\d+\.\d+\.\d+", flat_data)
                for v in version_candidates:
                    if VERSION_REGEX.match(v):
                        return v
        except:
            continue

    return None

def get_version(region: str) -> str:
    play_store_version = get_play_store_ver(region)
    print(f"[DEBUG] Versão detectada na Play Store para região {region}: {play_store_version}")

    if play_store_version and VERSION_REGEX.match(play_store_version):
        return play_store_version
    else:
        raise ValueError("Não foi possível obter a versão mais recente da Play Store.")

# Thanks to atlas academy for this script!
# All credits to atlas
# Github: github.com/atlasacademy
# Website: atlasacademy.io
# Api: api.atlasacademy.io
# Apps: apps.atlasacademy.io

import re
import time

import json5
import httpx
import lxml.html

PLAY_STORE_URL = {
    "NA": "https://play.google.com/store/apps/details?id=com.aniplex.fategrandorder.en",
    "JP": "https://play.google.com/store/apps/details?id=com.aniplex.fategrandorder",
    "KR": "https://play.google.com/store/apps/details?id=com.netmarble.fgok",
    "TW": "https://play.google.com/store/apps/details?id=com.xiaomeng.fategrandorder",
}

PLAY_STORE_XPATH_1 = "/html/body/div[1]/div[4]/c-wiz/div/div[2]/div/div/main/c-wiz[4]/div[1]/div[2]/div/div[4]/span/div/span"
PLAY_STORE_XPATH_2 = "/html/body/div[1]/div[4]/c-wiz/div/div[2]/div/div/main/c-wiz[3]/div[1]/div[2]/div/div[4]/span/div/span"
PLAY_STORE_XPATH_3 = '//div[div[text()="Current Version"]]/span/div/span/text()'
VERSION_REGEX = re.compile(r"^\d+\.\d+\.\d+$")

def get_play_store_ver(region: str):
    import re

    url = PLAY_STORE_URL[region]
    response = httpx.get(url, follow_redirects=True)

    # Tente pegar via regex diretamente
    version_match = re.search(r'Current Version.*?>([\d.]+)<', response.text)
    if version_match and VERSION_REGEX.match(version_match.group(1)):
        return version_match.group(1)

    # Procura por "AF_initDataCallback" com versão válida
    for match in re.finditer(r"AF_initDataCallback\((.*?)\);", response.text):
        try:
            data = json5.loads(match.group(1))
            if (
                "data" in data
                and isinstance(data["data"], list)
            ):
                # Tenta vários níveis
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

import json
import binascii
import requests
import version
import main
import CatAndMouseGame

requests.urllib3.disable_warnings()
session = requests.Session()
session.verify = False

# ===== Game's parameters =====
app_ver_ = ''
data_ver_ = 0
date_ver_ = 0
ver_code_ = ''
asset_bundle_folder_ = ''
data_server_folder_crc_ = 0
server_addr_ = 'https://game.fate-go.jp'
github_token_ = ''
github_name_ = ''
user_agent_ = 'Dalvik/2.1.0 (Linux; U; Android 11; Pixel 5 Build/RD1A.201105.003.A1)'

# ==== User Info ====
def set_latest_assets():
    global app_ver_, data_ver_, date_ver_, asset_bundle_folder_, data_server_folder_crc_, ver_code_, server_addr_

    region = main.fate_region

    # Set Game Server Depends of region
    if region == "NA":
        server_addr_ = "https://game.fate-go.us"

    # Get Latest Version of the data!
    version_str = version.get_version(region)

    if not version_str:
        raise ValueError("Versão retornada de 'version.get_version()' é inválida ou vazia.")

    print(f"[INFO] Versão do app usada: {version_str}")
    url = f'{server_addr_}/gamedata/top?appVer={version_str}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        raw_json = response.json()

        response_section = raw_json.get("response", [{}])[0]
        if "success" not in response_section:
            raise KeyError("Chave 'success' não encontrada na resposta.")

        response_data = response_section["success"]

        app_ver_ = version_str
        data_ver_ = response_data.get('dataVer')
        date_ver_ = response_data.get('dateVer')
        ver_code_ = main.get_latest_verCode()

        if not data_ver_ or not date_ver_:
            raise ValueError("Dados incompletos recebidos do servidor.")

        # Use Asset Bundle Extractor to get Folder Name
        assetbundle = CatAndMouseGame.getAssetBundle(response_data['assetbundle'])
        get_folder_data(assetbundle)

    except Exception as e:
        print(f"[ERRO] Falha ao obter os dados mais recentes: {e}")
        print(f"[DEBUG] URL acessada: {url}")
        print(f"[DEBUG] Resposta do servidor:\n{response.text}")
        raise

def get_folder_data(assetbundle):
    global asset_bundle_folder_, data_server_folder_crc_

    asset_bundle_folder_ = assetbundle['folderName']
    data_server_folder_crc_ = binascii.crc32(
        assetbundle['folderName'].encode('utf8'))

# ===== End =====


httpheader = {
    'Accept-Encoding': 'gzip, identity',
    'User-Agent': user_agent_,
    'Content-Type': 'application/x-www-form-urlencoded',
    'Connection': 'Keep-Alive, TE',
    'TE': 'identity',
}


def NewSession():
    return requests.Session()


def PostReq(s, url, data):
    res = s.post(url, data=data, headers=httpheader, verify=False).json()
    res_code = res['response'][0]['resCode']

    if res_code != '00':
        detail = res['response'][0]['fail']['detail']
        message = f'[ErrorCode: {res_code}]\n{detail}'
        raise Exception(message)

    return res

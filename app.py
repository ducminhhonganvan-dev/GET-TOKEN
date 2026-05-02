#RIZER MISS YOU❤️❤️

import sys
sys.path.append("/")

from flask import Flask, jsonify, request, make_response
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import binascii
from protobuf import my_pb2, output_pb2, FreeFire_pb2, AccountPersonalShow_pb2
from google.protobuf import json_format
import json

import os
import warnings
from urllib3.exceptions import InsecureRequestWarning

warnings.filterwarnings("ignore", category=InsecureRequestWarning)

AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'

USERAGENT = "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)"
UNITY_VERSION = "2022.3.47f1"

app = Flask(__name__)


def get_player_level(token: str, server_url: str, account_id: int) -> int:
    """Get player level from GetPlayerPersonalShow API"""
    try:
        # Build protobuf request: account_id + show_type
        proto_bytes = b'\x08' + bytes([account_id]) + b'\x10\x07'

        # Encrypt with AES
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        from Crypto.Util.Padding import pad
        encrypted = cipher.encrypt(pad(proto_bytes, 16))

        headers = {
            'User-Agent': USERAGENT,
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/octet-stream",
            'Authorization': f"Bearer {token}",
            'X-Unity-Version': UNITY_VERSION,
            'X-GA': "v1 1",
            'ReleaseVersion': "OB53"
        }

        # Try multiple server URLs
        urls = [
            f"{server_url}/GetPlayerPersonalShow",
            "https://clientbp.ggpolarbear.com/GetPlayerPersonalShow",
            "https://clientbp.ggwhitehawk.com/GetPlayerPersonalShow"
        ]

        for url in urls:
            try:
                resp = requests.post(url, data=encrypted, headers=headers, verify=False, timeout=5)
                if resp.status_code == 200:
                    res_msg = AccountPersonalShow_pb2.AccountPersonalShowInfo()
                    res_msg.ParseFromString(resp.content)
                    res_dict = json.loads(json_format.MessageToJson(res_msg))
                    basic_info = res_dict.get('basic_info', {})
                    level = int(basic_info.get('level', 0))
                    return level
            except:
                continue

        return 0
    except:
        return 0

def get_token(password, uid):
    url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"

    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = f"uid={uid}&password={password}&response_type=token&client_type=2&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3&client_id=100067"

    r = requests.post(url, headers=headers, data=data)

    try:
        j = r.json()
    except:
        return {
            "error": "OAuth non JSON",
            "raw": r.text
        }

    token = (
        j.get("access_token")
        or j.get("token")
        or j.get("session_key")
        or j.get("jwt")
        or (j.get("data") or {}).get("token")
    )

    if token:
        j["access_token"] = token

    return {
        "access_token": j.get("access_token"),
        "open_id": j.get("open_id"),
        "uid": j.get("uid"),
        "raw": j
    }

def encrypt_message(key, iv, plaintext):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(plaintext, AES.block_size)
    return cipher.encrypt(padded_message)

def process_token(uid, password):

    token_data = get_token(password, uid)

    if not token_data or not token_data.get('access_token'):
        return {"error": "Failed to retrieve token from Garena"}

    oauth_raw = token_data.get("raw", token_data)
    access_token = token_data.get('access_token')
    open_id = token_data.get('open_id')

    # ---- LOGIN REQUEST (Simplified like summonjwt) ----
    login_req = FreeFire_pb2.LoginReq()
    login_req.open_id = open_id
    login_req.open_id_type = "4"
    login_req.login_token = access_token
    login_req.orign_platform_type = "4"

    serialized_data = login_req.SerializeToString()
    encrypted_data = encrypt_message(AES_KEY, AES_IV, serialized_data)

    url = "https://loginbp.ggpolarbear.com/MajorLogin"
    headers = {
        'User-Agent': USERAGENT,
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/octet-stream",
        'Expect': "100-continue",
        'X-GA': "v1 1",
        'X-Unity-Version': UNITY_VERSION,
        'ReleaseVersion': "OB53"
    }

    try:
        response = requests.post(url, data=encrypted_data, headers=headers, verify=False)

        if response.status_code == 200:
            login_res = FreeFire_pb2.LoginRes()
            login_res.ParseFromString(response.content)
            
            res_dict = json.loads(json_format.MessageToJson(login_res))

            token = res_dict.get("token", "N/A")
            server_url = res_dict.get("serverUrl", "N/A")
            region = res_dict.get("lockRegion", "N/A")

            # Extract account_id from JWT payload
            account_id = 0
            try:
                import base64
                jwt_parts = token.split('.')
                if len(jwt_parts) == 3:
                    payload_b64 = jwt_parts[1]
                    # Add padding if needed
                    padding = 4 - len(payload_b64) % 4
                    if padding != 4:
                        payload_b64 += '=' * padding
                    payload_json = base64.urlsafe_b64decode(payload_b64).decode('utf-8')
                    payload_data = json.loads(payload_json)
                    account_id = int(payload_data.get('account_id', 0))
            except:
                pass

            # Get player level
            level = 0
            if account_id > 0 and token != "N/A":
                level = get_player_level(token, server_url, account_id)

            return {
                "token": token,
                "oauth_raw": oauth_raw,
                "api": server_url,
                "region": region,
                "level": level,
                "status": "live"
            }
        else:
            return {"error": f"HTTP {response.status_code} - {response.reason}"}

    except Exception as e:
        return {"error": f"Request error: {e}"}

@app.route('/token', methods=['GET'])
def get_token_response():

    uid = request.args.get('uid')
    password = request.args.get('password')

    if not uid or not password:
        return jsonify({"error": "Missing parameters: uid and password are required"}), 400

    result = process_token(uid, password)

    if "error" in result:
        return jsonify(result), 500

    response = make_response(jsonify(result))
    response.headers["Content-Type"] = "application/json"
    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

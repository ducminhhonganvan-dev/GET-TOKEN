import requests
import json
import time

accounts = {
  "4541818971": "GUEST-8LG2P1BBZ-PASS",
  "4541818970": "GUEST-5V0PFBUSN-PASS",
  "4541819082": "GUEST-JZBL1XVTB-PASS",
  "4541785535": "GUEST-JJSRMQAGC-PASS",
  "4541785534": "GUEST-WHRFX3ENX-PASS",
  "4541785536": "GUEST-J0AAXPBGY-PASS",
  "4541818961": "GUEST-JRYCQBCCL-PASS",
  "4601109234": "GUEST-OOOCYMZHL-PASS",
  "4541786367": "GUEST-0NLQGYOY2-PASS",
  "4541785524": "GUEST-TUE2RWZCQ-PASS",
  "4579229453": "GUEST-ROH2ZFDZK-PASS",
  "4473885893": "NAJMI-SMSR3UHQE-CORE",
  "4529006667": "GUEST-1NQOMXLAI-PASS",
  "4484789117": "GUEST-FHET2ZDPW-PASS",
  "4687975445": "31579C40295D14B4DC1FAA8A17849390EEEC676F3AD7CD2C89BB65164A104083",
  "4686315275": "5798D7628F1B9A9E70B069973DD417622C3B630602157BC18B92DFF7697F669D",
  "4435237705": "B011DDE2081CFABDA08FCBAFE2E4795F04F5760632DD034382705C1B8F6DAC90",
  "4436651344": "1A7DD7FACA192D5F1F7C716C42939F08173B538C5C555F39CD6B7B7D5E3478C0",
  "4656478605": "chuong_QHAU_NO_DEV_2026",
  "4267953098": "GRINGO1737",
  "4267953116": "GRINGO2232",
  "4267953126": "GRINGO1238",
  "4669799007": "ACD6D40477A5847F748A1A52138EA3E14D3DE81D3749AF84D28B26C304497286",
  "4688668139": "252F46E75CD5A8B7F92BC67A84A949E19D566CC3338A4F75F2E3337F4EA53FE0",
  "4269877210": "GRINGO2137",
  "4269877242": "GRINGO1995",
  "4269955461": "GRINGO2201",
  "4269955477": "GRINGO1445",
  "4269955487": "GRINGO2376"
}

results = []
print(f"{'UID':<12} | {'Status':<10} | {'Region':<6} | {'Result'}")
print("-" * 60)

for uid, pwd in accounts.items():
    try:
        url = f"http://127.0.0.1:5000/token?uid={uid}&password={pwd}"
        resp = requests.get(url, timeout=15)
        data = resp.json()
        
        if resp.status_code == 200:
            status = "SUCCESS"
            region = data.get("region", "??")
            msg = "Token obtained"
        else:
            status = "FAILED"
            region = "--"
            msg = data.get("error", "Unknown error")
            
        print(f"{uid:<12} | {status:<10} | {region:<6} | {msg}")
        results.append({"uid": uid, "status": status, "region": region, "msg": msg})
    except Exception as e:
        print(f"{uid:<12} | ERROR      | --     | {str(e)}")

success_count = sum(1 for r in results if r["status"] == "SUCCESS")
print("-" * 60)
print(f"Total: {len(accounts)} | Success: {success_count} | Failed: {len(accounts) - success_count}")

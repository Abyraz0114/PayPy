import json
import pkce
import uuid
import datetime
import requests
import urllib.parse

from bs4 import BeautifulSoup

class PayPyException(Exception):
    pass

class PayPy(object):
    def __init__(self, access_token: str = None, device_uuid: str = str(uuid.uuid4()), client_uuid: str = str(uuid.uuid4()), proxy_info: str = None) -> None:
        if proxy_info == None:
            self.proxies = None
        else:
            self.proxies = {
                "http": proxy_info,
                "https": proxy_info
            }

        self.app_version = self.get_app_version()

        self.params = {
            "payPayLang": "ja"
        }

        self.headers = {
            "Host": "app4.paypay.ne.jp",
            "Client-Os-Type": "ANDROID",
            "Device-Acceleration-2": "NULL",
            "Device-Name": "SM-G973N",
            "Is-Emulator": "false",
            "Device-Rotation": "NULL",
            "Device-Manufacturer-Name": "samsung",
            "Client-Os-Version": "28.0.0",
            "Device-Brand-Name": "samsung",
            "Device-Orientation": "NULL",
            "Device-Uuid": device_uuid,
            "Device-Acceleration": "NULL",
            "Device-Rotation-2": "NULL",
            "Client-Os-Release-Version": "9",
            "Client-Type": "PAYPAYAPP",
            "Client-Uuid": client_uuid,
            "Device-Hardware-Name": "qcom",
            "Device-Orientation-2": "NULL",
            "Network-Status": "WIFI",
            "Client-Version": self.app_version,
            "Client-Mode": "NORMAL",
            "System-Locale": "ja",
            "Timezone": "Asia/Tokyo",
            "User-Agent": f"PaypayApp/{self.app_version} Android9",
            "Accept-Charset": "UTF-8",
            "Accept": "*/*",
            "Traceparent": "NULL",
            "Tracestate": "NULL",
            "Newrelic": "NULL",
            "Accept-Encoding": "gzip, deflate",
            "X-Newrelic-Id": "NULL"
        }

        if access_token != None:
            self.headers["Authorization"] = f"Bearer {access_token}"

        self.session = requests.Session()

    def get_app_version(self):
        response = requests.get('https://apps.apple.com/jp/app/paypay-ペイペイ/id1435783608')
        soup = BeautifulSoup(response.text, "html.parser")
        app = json.loads(list(json.loads(soup.find("script", attrs={"id": "shoebox-media-api-cache-apps"}).text).values())[0])
        version = app["d"][0]["attributes"]["platformAttributes"]["ios"]["versionHistory"][0]["versionDisplay"]
        return version
    
    def login_start(self, phone_number, password):
        self.verifier, self.challenge = pkce.generate_pkce_pair(code_verifier_length=43)

        response = self.session.post(
            "https://app4.paypay.ne.jp/bff/v2/oauth2/par",
            params=self.params,
            headers=self.headers,
            data={
                "clientId": "pay2-mobile-app-client",
                "clientAppVersion": self.app_version,
                "clientOsVersion": "32.0.0",
                "clientOsType": "ANDROID",
                "responseType": "code",
                "redirectUri": "paypay://oauth2/callback",
                "state": pkce.generate_code_verifier(length=43),
                "codeChallenge": self.challenge,
                "codeChallengeMethod": "S256",
                "scope": "REGULAR",
                "tokenVersion": "v2",
                "prompt": "create",
                "uiLocales": "ja"
            },
            proxies=self.proxies
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPyException(response["header"]["resultCode"], response["header"]["resultMessage"])
        request_uri = response["payload"]["requestUri"]

        self.session.get(
            "https://www.paypay.ne.jp/portal/api/v2/oauth2/authorize",
            params={
                "client_id": "pay2-mobile-app-client",
                "request_uri": request_uri
            },
            headers={
                "Host": "www.paypay.ne.jp",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": f"Mozilla/5.0 (Linux; Android 9; SM-G973N Build/PPR1.190810.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 jp.pay2.app.android/{self.app_version}",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "X-Requested-With": "jp.ne.paypay.android.app",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
                "Connection": "close"
            },
            proxies=self.proxies
        )

        response = self.session.post(
            "https://www.paypay.ne.jp/portal/api/v2/oauth2/sign-in/password",
            headers={
                "Host": "www.paypay.ne.jp",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Client-Os-Version": "28.0.0",
                "Client-Version": self.app_version,
                "User-Agent": f"Mozilla/5.0 (Linux; Android 9; SM-G973N Build/PPR1.190810.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 jp.pay2.app.android/{self.app_version}",
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "Client-App-Load-Start": "1694156981476",
                "Client-Os-Type": "ANDROID",
                "Client-Id": "pay2-mobile-app-client",
                "Client-Type": "PAYPAYAPP",
                "Origin": "https://www.paypay.ne.jp",
                "X-Requested-With": "jp.ne.paypay.android.app",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://www.paypay.ne.jp/portal/oauth2/sign-in?client_id=pay2-mobile-app-client&mode=landing",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
            },
            json={
                "username": phone_number,
                "password": password
            },
            proxies=self.proxies
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPyException(response["header"]["resultCode"], response["header"]["resultMessage"])
        
        response = self.session.post(
            "https://www.paypay.ne.jp/portal/api/v2/oauth2/extension/code-grant/start",
            headers={
                "Host": "www.paypay.ne.jp",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Client-Os-Version": "28.0.0",
                "Client-Version": self.app_version,
                "User-Agent": f"Mozilla/5.0 (Linux; Android 9; SM-G973N Build/PPR1.190810.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 jp.pay2.app.android/{self.app_version}",
                "Accept": "application/json, text/plain, */*",
                "Client-App-Load-Start": "1694156981476",
                "Client-Os-Type": "ANDROID",
                "Client-Id": "pay2-mobile-app-client",
                "Client-Type": "PAYPAYAPP",
                "Sentry-Trace": "NULL",
                "Baggage": "NULL",
                "Origin": "https://www.paypay.ne.jp",
                "X-Requested-With": "jp.ne.paypay.android.app",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://www.paypay.ne.jp/portal/oauth2/extension-code-grant?mode=navigation",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
            },
            proxies=self.proxies
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPyException(response["header"]["resultCode"], response["header"]["resultMessage"])
        self.ext_id = response["payload"]["extensionId"]

        response = self.session.post(
            "https://www.paypay.ne.jp/portal/api/v2/oauth2/extension/code-grant/otl/select",
            headers={
                "Host": "www.paypay.ne.jp",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Client-Os-Version": "28.0.0",
                "Client-Version": self.app_version,
                "User-Agent": f"Mozilla/5.0 (Linux; Android 9; SM-G973N Build/PPR1.190810.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 jp.pay2.app.android/{self.app_version}",
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "Client-App-Load-Start": "1694156981476",
                "Client-Os-Type": "ANDROID",
                "Client-Id": "pay2-mobile-app-client",
                "Client-Type": "PAYPAYAPP",
                "Origin": "https://www.paypay.ne.jp",
                "X-Requested-With": "jp.ne.paypay.android.app",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://www.paypay.ne.jp/portal/oauth2/verification-method?mode=navigation-2fa",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
            },
            json={
                "extensionId": self.ext_id,
                "signInMethod": "MOBILE"
            },
            proxies=self.proxies
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPyException(response["header"]["resultCode"], response["header"]["resultMessage"])
    
    def login_confirm(self, otp):
        response = self.session.post(
            "https://www.paypay.ne.jp/portal/api/v2/oauth2/extension/code-grant/otl/verify-otp",
            headers={
                "Host": "www.paypay.ne.jp",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Client-Os-Version": "28.0.0",
                "Client-Version": self.app_version,
                "User-Agent": f"Mozilla/5.0 (Linux; Android 9; SM-G973N Build/PPR1.190810.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 jp.pay2.app.android/{self.app_version}",
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "Client-App-Load-Start": "1694156981476",
                "Client-Os-Type": "ANDROID",
                "Client-Id": "pay2-mobile-app-client",
                "Client-Type": "PAYPAYAPP",
                "Origin": "https://www.paypay.ne.jp",
                "X-Requested-With": "jp.ne.paypay.android.app",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://www.paypay.ne.jp/portal/oauth2/otl-otp?mode=navigation-2fa",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
            },
            json={
                "extensionId": self.ext_id,
                "otp": otp
            },
            proxies=self.proxies
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPyException(response["header"]["resultCode"], response["header"]["resultMessage"])
        code = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(response["payload"]["redirectUrl"]).query))["code"]

        response = self.session.post(
            "https://app4.paypay.ne.jp/bff/v2/oauth2/token",
            params=self.params,
            headers=self.headers,
            data={
                "clientId": "pay2-mobile-app-client",
                "redirectUri": "paypay://oauth2/callback",
                "code": code,
                "codeVerifier": self.verifier
            },
            proxies=self.proxies
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPyException(response["header"]["resultCode"], response["header"]["resultMessage"])
        
        token = response["payload"]["accessToken"]
        self.headers["Authorization"] = f"Bearer {token}"

        return response

    def get_balance(self):
        if not "Authorization" in self.headers:
            raise PayPyException(None, "先にログインを行ってください")

        response = self.session.get(
            "https://app4.paypay.ne.jp/bff/v1/getBalanceInfo",
            params={
                "includePendingBonusLite": "false",
                "includePending": "true",
                "includePreAuth": "true",
                "noCache": "true",
                "includeKycInfo": "true",
                "payPayLang": "ja"
            },
            headers=self.headers,
            proxies=self.proxies
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPyException(response["header"]["resultCode"], response["header"]["resultMessage"])
        
        return response
    
    def get_history(self, size: int = 20):
        if not "Authorization" in self.headers:
            raise PayPyException(None, "先にログインを行ってください")
        response = self.session.get(
            f"https://app4.paypay.ne.jp/bff/v3/getPaymentHistory",
            params={
                "pageSize": str(size),
                "payPayLang": "ja"
            },
            headers=self.headers,
            proxies=self.proxies
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPyException(response["header"]["resultCode"], response["header"]["resultMessage"])
        
        return response
    
    def get_profile(self):
        if not "Authorization" in self.headers:
            raise PayPyException(None, "先にログインを行ってください")

        response = self.session.get(
            "https://app4.paypay.ne.jp/bff/v2/getProfileDisplayInfo",
            params={
                "includeExternalProfileSync": "true",
                "payPayLang": "ja"
            },
            headers=self.headers,
            proxies=self.proxies
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPyException(response["header"]["resultCode"], response["header"]["resultMessage"])
        
        return response
    
    def get_link(self, code: str):
        if not "Authorization" in self.headers:
            raise PayPyException(None, "先にログインを行ってください")
        
        response = requests.get(
            "https://app4.paypay.ne.jp/bff/v2/getP2PLinkInfo",
            params={
                "verificationCode": code,
                "payPayLang": "ja"
            },
            headers=self.headers,
            proxies=self.proxies
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPyException(response["header"]["resultCode"], response["header"]["resultMessage"])
        
        return response
    
    def create_link(self, amount: int = 1, password: str = None):
        if not "Authorization" in self.headers:
            raise PayPyException(None, "先にログインを行ってください")

        payload = {
            "requestId": str(uuid.uuid4()),
            "amount": amount,
            "theme": "default-sendmoney",
            "requestAt": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        if password != None:
            payload["passcode"] = password

        response = requests.post(
            "https://app4.paypay.ne.jp/bff/v2/executeP2PSendMoneyLink",
            params=self.params,
            headers=self.headers,
            json=payload,
            proxies=self.proxies
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPyException(response["header"]["resultCode"], response["header"]["resultMessage"])
        
        return response
    
    def accept_link(self, code: str, password: str = None):
        if not "Authorization" in self.headers:
            raise PayPyException(None, "先にログインを行ってください")
        
        response = requests.get(
            "https://app4.paypay.ne.jp/bff/v2/getP2PLinkInfo",
            params={
                "verificationCode": code,
                "payPayLang": "ja"
            },
            headers=self.headers,
            proxies=self.proxies
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPyException(response["header"]["resultCode"], response["header"]["resultMessage"])
        if response["payload"]["orderStatus"] != "PENDING":
            raise PayPyException(None, "リンクは既に受け取り済みであるか辞退済みです")
        elif response["payload"]["pendingP2PInfo"]["isSetPasscode"] and password == None:
            raise PayPyException(None, "パスワードが必要です")
        
        payload = {
            "verificationCode": code,
            "requestId": str(uuid.uuid4()),
            "requestAt": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "orderId": response["payload"]["message"]["data"]["orderId"],
            "senderChannelUrl": response["payload"]["message"]["chatRoomId"],
            "senderMessageId": response["payload"]["message"]["messageId"]
        }
        if response["payload"]["pendingP2PInfo"]["isSetPasscode"]:
            payload["passcode"] = password
        
        response = requests.post(
            "https://app4.paypay.ne.jp/bff/v2/acceptP2PSendMoneyLink",
            params=self.params,
            headers=self.headers,
            json=payload,
            proxies=self.proxies
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPyException(response["header"]["resultCode"], response["header"]["resultMessage"])
        
        return response
    
    def reject_link(self, code: str):
        if not "Authorization" in self.headers:
            raise PayPyException(None, "先にログインを行ってください")
        
        response = requests.get(
            "https://app4.paypay.ne.jp/bff/v2/getP2PLinkInfo",
            params={
                "verificationCode": code,
                "payPayLang": "ja"
            },
            headers=self.headers,
            proxies=self.proxies
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPyException(response["header"]["resultCode"], response["header"]["resultMessage"])
        if response["payload"]["orderStatus"] != "PENDING":
            raise PayPyException(None, "リンクは既に受け取り済みであるか辞退済みです")
        
        payload = {
            "verificationCode": code,
            "requestId": str(uuid.uuid4()),
            "requestAt": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "orderId": response["payload"]["message"]["data"]["orderId"],
            "senderChannelUrl": response["payload"]["message"]["chatRoomId"],
            "senderMessageId": response["payload"]["message"]["messageId"]
        }
        
        response = requests.post(
            "https://app4.paypay.ne.jp/bff/v2/rejectP2PSendMoneyLink",
            params=self.params,
            headers=self.headers,
            json=payload,
            proxies=self.proxies
        ).json()
        if response["header"]["resultCode"] != "S0000":
            raise PayPyException(response["header"]["resultCode"], response["header"]["resultMessage"])
        
        return response
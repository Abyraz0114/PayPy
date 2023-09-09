# PayPy
PayPayをPythonから操作します。<br>
(非公式PayPayライブラリ)

## 特徴
- 次のようなことを行うことが出来ます: 
	* PayPayログイン(電話番号とパスワード / トークン)
	* 残高の参照
	* 取引履歴の指定個数分の参照
	* 送金リンクの受け取り 
	* 送金リンクの作成
	* アカウント情報の確認
	
## 使い方
### ログイン
```python
from PayPy import PayPy

paypay = PayPy()

def login():
	try:
		paypay.login_start("PHONE NUMBER", "PASSWORD")
	except:
		print("Error")
		return
	otp = input("OTP: ")
	try:
		result = paypay.login_confirm(otp)
		token = result["payload"]["accessToken"]
		print(f"Token: {token}")
	except:
		print("Error")
		return
		
login()
```

### 各メゾット
```python
from PayPy import PayPy

paypay = PayPy("ACCESS TOKEN")

balance = paypay.get_balance() # 残高確認
history = paypay.get_history(20) # 取引履歴
profile = paypay.get_profile() # プロフィール確認
link_info = paypay.get_link("XXXXXXXXXXXXXXXX") # 受け取りリンク確認
accept_result = paypay.accept_link("XXXXXXXXXXXXXXXX", "PASSWORD") # リンク受け取り
reject_result = paypay.reject_link("XXXXXXXXXXXXXXXX") # リンク辞退
create_result = paypay.create_link(1, "PASSWORD") # リンク作成
```

## クレジット
- PayPayPy(https://github.com/SpecialAgency-Chat/paypaypy)

## 法的
これは、PayPayによって影響を受けたり、推奨されたり、認定されたりするものではありません。これは独立した非公式のAPIです。自己責任でご使用ください。
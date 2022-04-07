# How to set API keys

Login using the “Login” button in the top right
- Select the “Scheduler” button in the top right
- Select the “Set API keys” button
- Select the exchange for which you would like to configure
- Coinbase Pro requires three keys
  - API Key
  - API Secret
  - API Passphrase
- All other exchanges require only two keys
  - API Key
  - API Secret
- It’s important that your API keys are generated using the correct permissions following the principle of least privilege.  CryptoStacker only needs the ability to view and trade. CryptoStacker does not need the ability to deposit or withdraw.  Coinbase Pro calls these permissions “view” and “trade”. To see what these permissions are called on other exchanges please see “How to create API keys for each exchange” for detailed guides.  All exchange API keys which you enter into CryptoStacker should be created as view & trade only API keys.  CryptoStacker does not need deposit/withdrawal/transfer permissions.
- You can set a key expiration length so that CryptoStacker will automatically delete your API keys after a set interval.
- You can delete your API keys at anytime from the “Set API keys” pages

API Keys are passwords, they should be kept secret.

### How to create API keys on Coinbase Pro
- Login to Coinbase Pro | https://pro.coinbase.com/
- Browse to the API page | https://pro.coinbase.com/profile/api
- Select “+ New API Key”
- Create a key with “View” & “Trade” permissions (“Transfer” permission is not needed for CryptoStacker)
- You’ll need the “API key”, “API passphrase” & “API Secret” for CryptoStacker

API KEY:

![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/api-key-example.jpg)

API Secret:

![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/api-key-secret.jpg)

API Passphrase:

![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/api-key-passphrase-example.jpg)

### How to create API keys on Binance US
Login to Binance US | https://www.binance.us/
- Browse to the “API Management” page | https://www.binance.us/en/usercenter/settings/api-management
- Select “Create” after entering a label
- Create a key with “Can Read” & “Enable Spot Trading” permissions (“Enable Withdrawals” permission is not needed for CryptoStacker)
- IP access restrictions: Unrestricted
- You’ll need the “API key” & “Secret key” for CryptoStacker
- Binance US requires “Enable Spot Trading” to be re-enabled after 30 days please see their blog post for more details

### How to create API keys on Kraken
- Login to Kraken | https://www.kraken.com/
- Browse to the “API key management” page | https://www.kraken.com/u/security/api
- Select “Add Key”
- Enter a description of your choice and leave nonce window set to 0
- The “Key permissions” required are “Query Funds” & “Create & Modify Order” (CryptoStacker DOES NOT require “Deposit Funds” or “Withdraw Funds” key permissions)
- Select Generate Key
- You’ll need the “API key” & “Private key” for CryptoStacker
- Select Save

### How to create API keys on Gemini
Login to Gemini | https://www.gemini.com/
- Browse to the “API” page | https://exchange.gemini.com/settings/api
- Select “Create API key”
- It is recommended for security purposes to use the scope “primary”
- Create a key with “trading” API key setting, without require heartbeat (“Fund management” API key setting is not needed for CryptoStacker)
- You’ll need the “API key” & “API Secret” for CryptoStacker

### How to create API keys on FTX US
- Login to FTX US | https://ftx.us/
- Browse to the “API” page | https://ftx.us/settings/api
- Select “Create API Key”
- You’ll need the “API key” & “API Secret” for CryptoStacker
- Ensure that the permissions for this new key is set to “Trading” (“Withdrawals enabled” is not needed for CryptoStacker)

### How to create API keys on Bittrex
- Login to Bittrex | https://bittrex.com/
- Browse to the “API Keys” page | https://bittrex.com/Manage?view=api
- Select “Add new key…”
- Enable “READ INFO” & “TRADE” and select save
- You’ll need the “Key” & “Secret” for CryptoStacker

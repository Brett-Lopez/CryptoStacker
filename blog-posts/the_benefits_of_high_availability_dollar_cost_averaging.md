# The benefits of high availability dollar-cost averaging

A great way to DCA is to setup a recurring purchase on your favorite exchange. But what if your favorite exchange is down or you run out of funds on said exchange?  Enter CryptoStacker’s high availability features for dollar-cost averaging (DCA). 

CryptoStacker supports four high availability options.  Let's assume a DCA event occurs every 1000 minutes (16 hours & 40 minutes).
- Failover will begin with your Priority 1 exchange, and if for any reason the DCA event fails on that exchange (such as the exchange is down/offline or your balance is insufficient) then failover will move to your Priority 2 exchange.  This process will continue all the way to your Priority 6 exchange until a transaction is successful.  If no transactions are successful, CryptoStacker will wait until the next DCA event before attempting to purchase again (16 hours & 40 minutes).  If a successful transaction occurs, then no additional exchanges will attempt a purchase during the DCA event.
- Round Robin will cycle between each exchange you specify in the priority drop downs. Priority numbers determine the order which is repeated once the final exchange is reached.  Only one exchange will transact per DCA event.  Failover is built into the Round Robin high availability type to ensure a DCA event is never missed.
- Simultaneous will cause all exchanges you specify in the priority drop downs to purchase simultaneously during every DCA event.
- Single exchange will cause only the exchange set in Priority 1 to run during a DCA event.  If for some reason that exchange fails to DCA it will attempt again at the next DCA event.

Using Failover, Round Robin, and Simultaneous high availability features means that, even if your favorite exchange is down when your DCA event is scheduled to take place, you’ll still buy crypto on a different exchange.

We’re going to demonstrate some examples of the high availability features of CryptoStacker.

In this first example, we create a Bitcoin DCA schedule with the following settings:
- Purchase $10 every 1,000 minutes (16 hours, 40 minutes)
- High availability type: Failover
- Funding source: USD on exchange
- Exchange priority:
  - Kraken
  - Binance US
  - Coinbase Pro (free to all Coinbase users)
  - Gemini

![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/7.PNG)

In this example our API Key for Kraken has expired and we no longer have any USD funds on Binance US, lets check the logs to see how CryptoStacker handles this.

![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/2.PNG)

![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/3.PNG)

![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/8.PNG)

We can see from the snapshot above that CryptoStacker’s failover preformed the following actions:
- Kraken is online but the API key is expired, CryptoStacker recognized it to be invalid so a “failed” status was logged along with “API Key Invalid”, and moves on to the next exchange.
- Binance US is online but the USD balance on Binance US is below $10, so an “Insufficient Balance” status was logged and moves on to the next exchange.
- Coinbase Pro is online, has a valid API key and sufficient USD balance, so CryptoStacker is able to submit this cycle’s DCA event on Coinbase Pro and log a “Success” status.
- Gemini isn’t attempted because the purchase on Coinbase Pro was successful.

In this second example, we create a Bitcoin DCA schedule with the following settings:
- Purchase $10 every 1,000 minutes (16 hours, 40 minutes)
- High availability type: Round Robin
- Funding source: USD on exchange
- Exchange priority:
  - Coinbase Pro (free to all Coinbase users)
  - Binance US
  - Gemini
  - Bittrex

![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/9.png)

In this example all API keys are valid, Coinbase Pro has a $11 balance, Binance US, Gemini & Bittrex all have larger balances, lets check the logs to see how CryptoStacker handles this.

![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/round_robin.png)

We can see from the snapshot above that CryptoStacker’s round robin preformed the following actions:
- Coinbase Pro is online, has a valid API key and sufficient USD balance, so CryptoStacker is able to submit this cycle’s DCA event on Coinbase Pro and log a “Success” status.
- 16 hours & 40 minutes later: Binance US is online, has a valid API key and sufficient USD balance, so CryptoStacker is able to submit this cycle’s DCA event on Binance US and log a “Success” status.
- 16 hours & 40 minutes later: Gemini is online, has a valid API key and sufficient USD balance, so CryptoStacker is able to submit this cycle’s DCA event on Gemini and log a “Success” status.
- 16 hours & 40 minutes later: Bittrex is online, has a valid API key and sufficient USD balance, so CryptoStacker is able to submit this cycle’s DCA event on Bittrex and log a “Success” status.
- 16 hours & 40 minutes later: Coinbase Pro is online, has a valid API key BUT insufficient USD balance, so CryptoStacker logs a “Failed” status for “Insufficient Balance” then attempts the next exchange Binance US.  Binance US is online, has a valid API key and sufficient USD balance, so CryptoStacker is able to submit this cycle’s DCA event on Binance US and log a “Success” status.  This is an example of how failover is built into the round robin high availability type.
- 16 hours & 40 minutes later: Gemini is online, has a valid API key and sufficient USD balance, so CryptoStacker is able to submit this cycle’s DCA event on Gemini and log a “Success” status.
- 16 hours & 40 minutes later: Bittrex is online, has a valid API key and sufficient USD balance, so CryptoStacker is able to submit this cycle’s DCA event on Bittrex and log a “Success” status.
- ….this cycle will continue until the schedule is disabled.

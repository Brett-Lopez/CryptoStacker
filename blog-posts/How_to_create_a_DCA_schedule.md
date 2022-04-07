# How to create a DCA schedule 

Login using the “Login” button in the top right
- Select the “Scheduler” button in the top right
- Select the “DCA schedules” button
- Select the coin you wish to create a schedule for (BTC, ETH, LTC) and select “Set Schedule”
- Set the dollar amount and time interval for your DCA purchase
  - Eg: 10 dollars every 720 minutes
- Select the high availability type:
  - Failover will begin with your Priority 1 exchange and, if for any reason the DCA event fails on that exchange (such as the exchange is down/offline, your API key has expired or is no longer valid, your balance is insufficient), then failover will move to your Priority 2 exchange.  This process will continue all the way to your Priority 6 exchange until a transaction is successful.  If no transactions are successful, Cryptostacker will retry from the start at the next scheduled interval.  If a successful transaction occurs, then no additional exchanges will attempt a purchase.
  - Round Robin will cycle between each exchange you specify in the priority drop downs, priority numbers determine the order which is repeated once the final exchange is reached.  Only one exchange will transact per DCA event.  Failover is built into the Round Robin high availability type to ensure a DCA event is never missed.
  - Simultaneous will cause all exchanges you specify in the priority drop downs to purchase simultaneously at every DCA interval.
  - Single exchange will cause only the exchange set in Priority 1 to run during a DCA interval.  If for some reason that exchange fails to DCA, it will attempt again at the next DCA interval.
- Funding source: At the time of this writing, the only funding source is on exchange USD balance.  You must deposit USD on the exchanges of your choosing in order to purchase coins with CryptoStacker.
- Coinbase Pro is free, you simply browse to pro.coinbase.com and login with your usual Coinbase account.  You can easily transfer funds between Coinbase and Coinbase Pro or deposit directly to Coinbase Pro.

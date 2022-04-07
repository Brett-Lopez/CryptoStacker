# FAQ:

### Where do I find my API keys?
API keys will have to be created on each exchange that you would like to use with CryptoStacker.
Detailed information on this process for each exchange can be found here.

### How can I secure my API keys?
It’s important that your API keys are generated using the correct permissions following the principle of least privilege.  CryptoStacker only needs the ability to view and trade. CryptoStacker does not need the ability to deposit or withdraw.  Coinbase Pro calls these permissions “view”  and “trade”. To see what these permissions are called on other exchanges please see “How to create API keys for each exchange” for detailed guides.  All exchange API keys which you enter into CryptoStacker should be created as view and trade only API keys.  CryptoStacker does not need deposit/withdrawal/transfer permissions.  API keys are passwords and should be treated as such.

### How do I enter/set API keys?
API keys are set for each exchange on this page.  For a more detailed guide please read this page.

### How do I set a DCA schedule?
DCA schedules can be set here.  And you can read about how to configure DCA schedules here.


### How do I view past DCA events?
Past DCA events are viewed in the DCA logs here.

### How do I use the DCA calculator?
The DCA calculator is used to calculate the optimal high frequency DCA schedule.  You provide the dollar amount for each DCA event (eg: $10), the time period over which your DCA schedule will run in days (eg: 30 days), and the total dollar amount you wish to use over the DCA schedule period (eg: $600).  The calculator will return the DCA schedule to use with CryptoStacker, using the example numbers from above the output would be: Purchase $10.0 every 720 minutes

An example with a screenshot can be seen here.

### What is dollar-cost averaging (DCA)?
Dollar-cost averaging (DCA) is an investment strategy that involves spending a fixed amount of money on an asset at set intervals. You do this no matter what’s happening with the asset’s price. However, the amount of money and the intervals can vary based on your preferences and the amount of capital that you have to deploy.

### How do I change my time zone so DCA logs & schedules reflect the correct time zone?
You can change your timezone on the user settings page.

### How do I upgrade my subscription from the free tier 1 to tier 2 or 3?
Visit the pricing page and select the plan you wish to purchase.

### How do I upgrade my subscription from tier 2 to tier 3?
Visit the pricing page and select the plan you wish to purchase.

### How do I manage my subscription such as viewing past payments or checking my current subscription tier?
Visit the manage subscription page.

### How do I reset MFA?
Click the “RESET MFA” button the on user settings page.

### I didn't receive a verification email.  How do I request a new verification email?
Click the “Resend email verification” button on the user settings page. 
Please be sure to also check your spam folder.

### How do I delete my API keys?
Visit the set api keys page, select the applicable exchange and click the button at the bottom that says “DELETE <exchange> API KEY”.
More information about creating and deleting API keys can be found here.

### How can I request a feature?
If you’d like to request an additional feature we’d love to hear from you! Please use this page to submit a feature request.

### What happens if my USD balance on an exchange is below my purchase amount?
If your purchase amount is above your balance amount, CryptoStacker will either end the DCA event and try again at the next scheduled time or move on to your next exchange depending upon how you configured high availability.  You can read more about high availability configuration here.

### Why is the fiat size of Gemini, FTX US, Kraken & Bittrex purchases inconsistent?
This is due to limitations of each exchange's API. Each exchange has a unique API implementation.  If you require your DCA's to have a consistent fiat size then we recommend you use Coinbase Pro or Binance US which both support a consistent fiat size for every DCA event.

### Can I pay for CryptoStacker with a credit card?
At this time CryptoStacker only accepts payments in Bitcoin.  We support on-chain transactions or the lightning network.

### How do I contant support with a question or problem that isn't listed in the FAQ?
Please contact us using this page.

### How do I delete my account and all of my data?
Click the “Delete my account and all of my data” button on the user settings page.

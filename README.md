# trading-bot-new-coins
This is a fork of [binance-trading-bot-new-coins](https://github.com/CyberPunkMetalHead/binance-trading-bot-new-coins "binance-trading-bot-new-coins") - credit for this idea goes to him.

This trading bot detects new coins as soon as they are listed on various exchanges, and automatically places sell and buy orders.  Binance and FTX are currently supported. In addition, it comes with trailing stop loss, stop loss, take profit, and other features.

It comes with a live and test mode, so naturally, use it at your own risk.

##### TODO List:
- Swap to multi-threading?
- Notification service (Discord/Telegram)
- Additional tests
- Additional Exchanges*

#### I want to contribute:
I would love contributors! Please send a pull request, and I will review it.

\*If you plan to add support for additional exchanges, please review and follow the structure used for the FTX and Binance wrapper classes already implemented.

#### I found a bug/issue:
Please include any applicable stack traces and logs.  There are currently two log files: `errors.log` and `verbose_log.log`.  Please also attach any relevant information from these files.


#### Changelog:
- 2021-09-16: New baseline - I've done a poor job tracking changes thus far.

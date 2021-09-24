# Automatic New Cryptocurrency Trading Bot
This is a major re-write of [binance-trading-bot-new-coins](https://github.com/CyberPunkMetalHead/binance-trading-bot-new-coins "binance-trading-bot-new-coins") - credit for the idea goes to him.

This trading bot detects new coins as soon as they are listed on various exchanges, and automatically places sell and buy orders.  Binance and FTX are currently supported. In addition, it comes with trailing stop loss, stop loss, take profit, and other features.

It comes with a live and test mode, so naturally, use it at your own risk.

## How to Set Up Notifications:
### Discord:
You must have permissions to create a `webhoook` on your chosen Discord server. 

1. Right-click the server icon
2. Go to `Integrations`
3. Click `Create Webhook`
4. Choose an icon (optional), name, and channel
5. Copy the `Webhook URL` and paste into `config.yml` under `NOTIFICATION_OPTIONS -> DISCORD -> AUTH -> ENDPOINT`

### Telegram:
This is a bit more involved than Discord...
1. Go to https://t.me/botfather and add the BotFather Bot
2. Type `/newbot`
3. Choose a name for your bot
4. Choose a username for your bot
5. Carefully copy the `token`
6. Go to the chat you wish the bot to be in and add the bot.  Add Member, then \<your bot name\>
7. Type a message in that chat
8. Visit this url:  `https://api.telegram.org/bot<YourBOTToken>/getUpdates` where `<YourBOTTOKEN>` is your token from step 5.
9. You should see a JSON response which has the chat id displayed.  The negative number (keep the negative sign)
10. Copy the token to  `NOTIFICATION_OPTIONS -> TELEGRAM -> AUTH -> ENDPOINT`
11. Copy the chat id to `NOTIFICATION_OPTIONS -> TELEGRAM -> AUTH -> CHAT_ID`

#### I found a bug/issue:
Please include any applicable stack traces and logs.  There are currently two log files: `errors.log` and `verbose_log.log`.  Please also attach any relevant information from these files.

## TODO List:
- Swap to multi-threading?
- ~~Notification service (Discord/Telegram)~~
- Additional tests
- Additional Exchanges*

## I want to contribute:
I would love contributors! Please send a pull request, and I will review it.

*If you plan to add support for additional exchanges, please review and follow the structure used for the FTX and Binance wrapper classes already implemented.

## I found a bug/issue:
Please include any applicable stack traces and logs.  There are currently two log files: `errors.log` and `verbose_log.log`.  Please also attach any relevant information from these files.

## Changelog:
- 2021-09-24: 
  1. `Invalid Symbol` Binance error finally fixed! 
  2. Notifications for Discord and Telegram added
- 2021-09-16:
  1. New baseline - I've done a poor job tracking changes thus far.

## Donate:
Made a killing using this?  [Buy me a coffee!](https://venmo.com/u/Cdalton713)
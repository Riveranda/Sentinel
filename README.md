# Eve Kill Stream

Sentinel is a discord bot which streams kills from Zkillboard directly into a discord channel. 

## Early Development

Sentinel has now released v1.0.0. Hosted on Google Cloud, the bot is now available to be added to servers via the link below:

[Invite Sentinel](https://discord.com/api/oauth2/authorize?client_id=1026984295539163186&permissions=8&scope=bot)

## Commands
Discord's new slash commands are being utilized here!

```/setchannel``` : Set the channel you wish to recieve the killstream in with

```/stop``` : Stop the killstream

```/start``` : Start the killstream

```/status``` : Display the current status muted/unmuted

```/watch {system/region/constellation}``` : Add a filter for the desired system, region, or constellation. 

```/watchcorp {corp_id/name}``` : Add a filter for the desired corporation. You might need to provide the corporation id if it has not been previously seen in the killstream.

```/watchalliance {alliance_id/name}``` : Add a filter for the desired alliance. You might need to provide the alliance id if it has not been previously seen in the killstream. 

```/ignore {system/region/constellation}``` :  Remove the desired filter.

```/ignorealliance {alliance_id/name}```  : Remove the desired alliance filter.

```/ignorecorp {corp_id/name}``` : Remove the desired corporation filter.

```/watchall``` : Removes all filters and opens up the full killstream.


## License

This project is licensed under the [GPL-3.0] License - see the LICENSE file for details

## Acknowledgments

* [sqlalchemy](https://github.com/sqlalchemy/sqlalchemy)
* [discord.py](https://github.com/Rapptz/discord.py)
* [requests-client](https://pypi.org/project/requests-client/)

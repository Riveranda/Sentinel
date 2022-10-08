# Eve Alarm

Eve Alarm is a discord bot which streams kills from Zkillboard directly into a discord channel. 

## Early Development

Eve Alarm is still in early development and has not been deployed yet. An invite link will be added upon version 1.0's release.



## Commands
```!setchannel``` : Set the channel you wish to recieve the killstream in with

```!stop``` : Stop the killstream

```!start``` : Start the killstream

```!watch {system/region/constellation}``` : Add a filter for the desired system, region, or constellation. 

```!watch corp:{corp_id/name}``` : Add a filter for the desired corporation. You might need to provide the corporation id if it has not been previously seen in the killstream.

```!watch alliance:{alliance_id/name}``` : Add a filter for the desired alliance. You might need to provide the alliance id if it has not been previously seen in the killstream. 

```!ignore [param]``` : See !watch for options. Remove the desired filter.

```!watchall``` : Removes all filters and opens up the full killstream.

```!h or !help``` : Prints out this list of commands.


## License

This project is licensed under the [GPL-3.0] License - see the LICENSE file for details

## Acknowledgments

* [sqlalchemy](https://github.com/sqlalchemy/sqlalchemy)
* [discord.py](https://github.com/Rapptz/discord.py)
* [requests-client](https://pypi.org/project/requests-client/)

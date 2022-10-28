from dbutility import is_ally_recorded, is_corp_recorded, add_new_ally_by_id, add_new_corp_by_id, add_object_to_watch
from Schema import Alliances, Corporations
from discord import Interaction


async def validate_corp_ally_obj(interaction: Interaction, obj: str, table: object, session):
    is_recorded, is_unique = None, None

    if table is Alliances:
        is_recorded, is_unique = is_ally_recorded(obj, session)
    elif table is Corporations:
        is_recorded, is_unique = is_corp_recorded(obj, session)
    else:
        return False
    if not is_unique and is_recorded:
        await interaction.response.send_message(f"Oops! Duplicate name or ticker: {obj}. A {'Corporation' if table is Corporations else 'Alliance'} with an identical name/ticker was likely closed.\nPlease add by id!")
        return False
    if not is_recorded:
        if obj.isdigit():
            if table is Corporations and not add_new_corp_by_id(int(obj), session):
                await interaction.response.send_message(f"Invalid Corporation Id: {int(obj)}")
                return False
            elif table is Alliances and not add_new_ally_by_id(int(obj), session):
                await interaction.response.send_message(f"Invalid Alliance Id: {int(obj)}")
                return False
        else:
            await interaction.response.send_message(f"{'Corporation' if table is Corporations else 'Alliance'} not in database. Please try adding by id")
            return False
    return True


async def add_ally_objects(interaction: Interaction, obj: str, table: object, session):
    obj_name = "Corporation" if table is Corporations else "Alliance"
    added, already_watched, name, same_ally = add_object_to_watch(
        interaction, session, obj, table, friend=True)
    if already_watched and same_ally:
        await interaction.response.send_message(f"{obj_name}: {name} is already an ally!")
        return
    elif added:
        await interaction.response.send_message(f"{obj_name}: {name} added as an ally!")
        return
    await interaction.response.send_message(f"Unknown {obj_name}, try adding by id or check your spelling.")


async def add_corp_alliance_objects(interaction: Interaction, obj: str, table: object, session):
    obj_name = "Corporation" if table is Corporations else "Alliance"
    added, already_watched, name, _ = add_object_to_watch(
        interaction, session, obj, table)
    if already_watched:
        await interaction.response.send_message(f"{obj_name}: {name} is already being watched!")
        return
    elif added:
        await interaction.response.send_message(f"{obj_name}: {name} added to watch list!")
        return
    await interaction.response.send_message(f"Unknown {obj_name}, try adding by id or check your spelling.")

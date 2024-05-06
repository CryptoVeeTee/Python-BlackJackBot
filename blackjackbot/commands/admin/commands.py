# -*- coding: utf-8 -*-

import logging
import re

from telegram.constants import ParseMode

from blackjackbot.commands.admin import notify_admins
from blackjackbot.commands.util.decorators import admin_method
from blackjackbot.errors import NoActiveGameException
from blackjackbot.gamestore import GameStore
from blackjackbot.lang import reload_strings, Translator
from database import Database

logger = logging.getLogger(__name__)


@admin_method
async def ban_user_cmd(update, context):
    """Bans a user from using the bot"""
    usage_message = r"Please provide a valid userid\. Usage: `/ban <userid>`"

    # Try to get user_id from command
    if len(context.args) != 1:
        await update.effective_message.reply_text(usage_message, parse_mode=ParseMode.MARKDOWN_V2)
        return

    match = re.search(r"^\d+$", context.args[0])
    if not match:
        logger.error(f"The user_id did not match. Args: {context.args}")
        await update.effective_message.reply_text(usage_message, parse_mode=ParseMode.MARKDOWN_V2)
        return

    user_id = match.group(0)
    db = Database()
    db.ban_user(user_id=user_id)
    logger.info(f"Admin '{update.effective_user.id}' banned user '{user_id}'!")
    await notify_admins(f"Admin '{update.effective_user.id}' banned user '{user_id}'!", context)


@admin_method
async def unban_user_cmd(update, context):
    """Unbans a user from using the bot"""
    usage_message = r"Please provide a valid userid\. Usage: `/unban <userid>`"

    # Try to get user_id from command
    if len(context.args) != 1:
        await update.message.reply_text(usage_message, parse_mode=ParseMode.MARKDOWN_V2)
        return

    match = re.search(r"^\d+$", context.args[0])
    if not match:
        logger.error(f"The user_id did not match. Args: {context.args}")
        await update.effective_message.reply_text(usage_message, parse_mode=ParseMode.MARKDOWN_V2)
        return
    user_id = match.group(0)

    db = Database()
    db.unban_user(user_id=user_id)

    logger.info(f"Admin '{update.effective_user.id}' unbanned user '{user_id}'!")
    await notify_admins(f"Admin '{update.effective_user.id}' unbanned user '{user_id}'!", context)


@admin_method
async def kill_game_cmd(update, context):
    """Kills the game for a certain chat/group"""
    if len(context.args) == 0:
        await update.message.reply_text("Please provide a chat_id!")
        return

    chat_id = context.args[0]
    # Input validation for chat_id
    if not re.match(r"^-?[0-9]+$", chat_id):
        await update.message.reply_text("Sorry, the chat_id is invalid!")
        return

    chat_id = int(chat_id)

    try:
        _ = GameStore().get_game(chat_id=chat_id)
    except NoActiveGameException:
        await update.message.reply_text("Sorry, there is no running game in a chat with that ID!")
        return

    logger.info("Admin '{0}' removed game in chat '{1}'".format(update.effective_user.id, chat_id))
    GameStore().remove_game(chat_id=chat_id)
    await update.message.reply_text("Alright, I killed the running game in '{0}'!".format(chat_id))
    await context.bot.send_message(chat_id=chat_id, text="The creator of this bot stopped your current game of BlackJack.")


@admin_method
async def reload_languages_cmd(update, context):
    reload_strings()
    await update.message.reply_text("Reloaded languages & strings!")


@admin_method
async def answer_comment_cmd(update, context):
    # Answer to admins only in English, because we don't save admin languages yet
    text = update.effective_message.text
    reply_to_message = update.message.reply_to_message
    text = text.replace("/answer ", "")

    # Error handling
    if reply_to_message is None or update.message.reply_to_message.from_user.id != context.bot.id:
        await update.message.reply_text("⚠ You need to reply to the user's comment!")
        return
    if update.message.reply_to_message.text is None:
        await update.message.reply_text("⚠ You replied to a non text message!")
        return

    try:
        # Parse user data from the message
        user_info = reply_to_message.text.split("\n")[-1]
    except Exception as e:
        await update.message.reply_text("⚠ An unexpected error occurred!")
        logger.error("While parsing user data, the following exception occurred: {}".format(e))
        return

    user = user_info.split(" | ")

    if type(user) != list or len(user) != 6:
        await update.message.reply_text("⚠ Can't parse user data from the message you replied to! Please reply to a comment!")
        logger.warning("Can't parse user data from message: {}".format(reply_to_message.text))
        return

    chat_id = user[0]

    if not re.match(r"^-?\d+$", chat_id):
        await update.message.reply_text("⚠ Malformed chat_id!")
        logger.error("Malformed chat_id: {}".format(chat_id))
        return

    translator = Translator(chat_id)
    user_reply = translator("reply_from_maintainer").format(text)

    # The following errors can easily happen here:
    # Have no rights to send a message -> Missing permissions
    # Forbidden: bot was blocked by the user -> User blocked the bot
    await context.bot.send_message(chat_id=chat_id, text=user_reply)
    await update.message.reply_text(text="I sent your comment to the user!")

    await notify_admins("An admin replied to the comment by\n\n{}\n\nwith:\n\n{}".format(user_info, text), context)


@admin_method
async def users_cmd(update, context):
    """Returns the amount of players in the last 24 hours"""
    db = Database()
    players = db.get_recent_players()

    text = "Last 24 hours: {}".format(len(players))

    await update.message.reply_text(text=text)


@admin_method
async def bans_cmd(update, context):
    """Returns the amount of players in the last 24 hours"""
    db = Database()
    banned_users = db.get_banned_users()

    text = f"Banned user count: {len(banned_users)}"

    await update.message.reply_text(text=text)

@admin_method
async def get_userid_cmd(update, context):
    """Unbans a user from using the bot"""
    usage_message = r"Please provide a valid username\. Usage: `/get_userid <username>`"

    # Try to get username from command
    if len(context.args) != 1:
        await update.message.reply_text(usage_message, parse_mode=ParseMode.MARKDOWN_V2)
        return

    if context.args[0].startswith("@"):
        username = context.args[0][1:]
    else:
        username = context.args[0]

    match = re.search(r"^[a-zA-Z][a-zA-Z0-9_.]{4,31}$", username)
    if not match:
        logger.error(f"The username did not match. Args: {context.args}")
        await update.effective_message.reply_text(usage_message, parse_mode=ParseMode.MARKDOWN_V2)
        return
    username = match.group(0)

    db = Database()
    user_id = db.get_userid(username=username)

    text = f"User ID for {username}: {user_id}"

    await update.message.reply_text(text=text)
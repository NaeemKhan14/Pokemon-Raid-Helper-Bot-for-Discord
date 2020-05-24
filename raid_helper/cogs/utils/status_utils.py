import discord
from discord.ext import commands
from typing import Tuple

from .chess_utils import load_from_pgn, to_png, get_turn
from .user_utils import get_discord_user
from .game_utils import who_offered_action
from raid_helper import database, constants


def _get_status_mentions(
    white: discord.User, black: discord.User, game: database.Game
) -> Tuple[str, str]:
    if white is None:
        white_mention = game.white.username or game.white.discord_id
    else:
        white_mention = white.mention

    if black is None:
        black_mention = game.black.username or game.black.discord_id
    else:
        black_mention = black.mention

    return white_mention, black_mention


def get_vs_line(bot: commands.Bot, game: database.Game) -> str:
    white, black = get_discord_user(bot, game.white), get_discord_user(bot, game.black)
    white_mention, black_mention = _get_status_mentions(white, black, game)
    return f"{white_mention} (white) **VS.** {black_mention} (black)"


def get_game_status(bot: commands.Bot, game: database.Game) -> Tuple[str, discord.File]:
    if not game.white or not game.black:
        raise RuntimeError(
            f"Either white or black player is not present in game #{game.id}"
        )

    vs_line = get_vs_line(bot, game)
    status = f"__Game ID: {game.id}__\n{vs_line}\n"

    board = load_from_pgn(game.pgn)

    if game.winner is None and game.win_reason is None:
        turn = get_turn(board)
        turn_str = constants.turn_to_str(turn)
        status += f"*{turn_str.capitalize()}'s turn.*\n"

        if game.action_proposed in constants.OFFERABLE_ACTIONS.values():
            if not (game.white_accepted_action or game.black_accepted_action):
                raise RuntimeError(
                    "An action was offered but neither player accepted it"
                )

            action = constants.OFFERABLE_ACTIONS_REVERSE.get(game.action_proposed)
            if action is None:
                raise RuntimeError("Action is not present in OFFERABLE_ACTIONS_REVERSE")
            action_str = action.lower()

            action_side = who_offered_action(game)
            opposite_side = (
                constants.BLACK if action_side == constants.WHITE else constants.WHITE
            )

            action_side_str = constants.turn_to_str(action_side).capitalize()
            opposite_side_str = constants.turn_to_str(opposite_side)

            status += (
                f'**{action_side_str} offered a "{action_str}" action.** '
                f"If {opposite_side_str} wants to accept, they should type *{bot.command_prefix}accept {game.id}*\n"
            )

        status += f"\nThis game will expire on {str(game.expiration_date).split()[0]},\nresulting in {turn_str} losing, if they don't make a move.\n"

    elif game.winner is not None and game.win_reason is not None:
        result = constants.turn_to_str(game.winner).capitalize()
        result = (
            f"{result} wins - {game.win_reason}."
            if game.winner != constants.DRAW
            else game.win_reason + "."
        )

        status += f"\n**Game over!** {result}"
    else:
        raise RuntimeError(
            f"Either game.winner or game.win_reason is not present in game #{game.id}"
        )

    return status, to_png(board)

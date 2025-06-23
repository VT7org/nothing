from pyrogram.types import InlineKeyboardButton
import config
from SONALI import app

def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"], url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_CHAT),
        ],
    ]
    return buttons

def private_panel(_):
    # Owner profile button with fallback if username is not available
    if hasattr(config, "OWNER_USERNAME") and config.OWNER_USERNAME:
        owner_button = InlineKeyboardButton(
            text=_["S_B_5"], url=f"https://t.me/{config.OWNER_USERNAME}"
        )
    else:
        owner_button = InlineKeyboardButton(
            text=_["S_B_5"], url=config.SUPPORT_CHAT
        )

    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            owner_button,
            InlineKeyboardButton(text=_["S_B_7"], callback_data="gib_source"),
            InlineKeyboardButton(text=_["S_B_6"], url=config.SUPPORT_CHANNEL),
        ],
        [InlineKeyboardButton(text=_["S_B_4"], callback_data="settings_back_helper")],
    ]
    return buttons

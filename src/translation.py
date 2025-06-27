import gettext

from src.settings import SRC_FOLDER


def get_translator(lang):
    try:
        return gettext.translation(
            "messages", localedir=SRC_FOLDER / "locales", languages=[lang]
        )
    except FileNotFoundError:
        return gettext.NullTranslations()

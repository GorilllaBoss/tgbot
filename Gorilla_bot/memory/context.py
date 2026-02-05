from memory.raw import get_today_raw


def build_today_context() -> str:
    items = get_today_raw()

    if not items:
        return ""

    return (
        "Контекст текущего дня пользователя "
        "(учитывай при ответе, не повторяй дословно):\n"
        + "\n".join(items)
    )

from enum import Enum
from colorama import init, Fore, Back, Style



class ElementType(Enum):
    COLORLESS = "Colorless"
    GRASS = "Grass"
    FIRE = "Fire"
    WATER = "Water"
    LIGHTNING = "Lightning"
    FIGHTING = "Fighting"
    PSYCHIC = "Psychic"
    DARKNESS = "Darkness"
    METAL = "Metal"
    FAIRY = "Fairy"
    DRAGON = "Dragon"

class StatusCondition(Enum):
    POISON = "Poison"  # 10 damage/turn
    BURN = "Burn"     # 20 damage/turn + coin flip
    SLEEP = "Sleep"   # attack prevention + coin flip
    PARALYSIS = "Paralysis"  # one-turn attack/retreat prevention
    CONFUSION = "Confusion"  # attack coin flip

ELEMENT_COLORS = {
    ElementType.COLORLESS: Style.DIM + Fore.WHITE,
    ElementType.GRASS: Fore.GREEN,
    ElementType.FIRE: Fore.RED,
    ElementType.WATER: Fore.BLUE,
    ElementType.LIGHTNING: Fore.YELLOW,
    ElementType.FIGHTING: Fore.MAGENTA,
    ElementType.PSYCHIC: Fore.MAGENTA,
    ElementType.DARKNESS: Style.DIM + Fore.WHITE,
    ElementType.METAL: Style.DIM + Fore.WHITE,
    ElementType.FAIRY: Fore.MAGENTA,
    ElementType.DRAGON: Fore.RED
}

# Define color mappings for status conditions
STATUS_COLORS = {
    StatusCondition.POISON: Fore.GREEN,
    StatusCondition.BURN: Fore.RED,
    StatusCondition.SLEEP: Fore.BLUE,
    StatusCondition.PARALYSIS: Fore.YELLOW,
    StatusCondition.CONFUSION: Fore.MAGENTA
}

ELEMENT_SYMBOLS = {
    ElementType.COLORLESS: "⬜",   # White square
    ElementType.GRASS: "🍃",
    ElementType.FIRE: "🔥",
    ElementType.WATER: "💧",
    ElementType.LIGHTNING: "⚡",
    ElementType.FIGHTING: "🥊",
    ElementType.PSYCHIC: "🔮",
    ElementType.DARKNESS: "🌑",
    ElementType.METAL: "⚙️",
    ElementType.FAIRY: "✨",
    ElementType.DRAGON: "🐉"
}

import json
import os
from src.pokemon import Pokemon
from src.deck import Deck
from src.elementTypes import ElementType

CARDLIST_PATH = os.path.join(os.path.dirname(__file__), '../resources/CardList.json')

# Load and cache the card list once
with open(CARDLIST_PATH, encoding='utf-8') as f:
    CARD_LIST = json.load(f)

def get_pokemon_by_name(name):
    """Retrieve a Pokémon card dict by name from the loaded card list."""
    for card in CARD_LIST:
        if card.get('name', '').lower() == name.lower() and card.get('card_type', '').startswith('Pokémon'):
            return card
    return None

def get_pokemon_by_criteria(criteria_fn, limit=1):
    """Retrieve Pokémon cards matching a criteria function."""
    results = []
    for card in CARD_LIST:
        if card.get('card_type', '').startswith('Pokémon') and criteria_fn(card):
            results.append(card)
            if len(results) >= limit:
                break
    return results

def create_real_test_deck():
    """Create a test deck of 20 Pokémon cards with duplicate evolution chains for testing evolution."""
    # Hardcode two evolution chains: Charmander -> Charmeleon -> Charizard and Bulbasaur -> Ivysaur -> Venusaur
    chain1 = [
        get_pokemon_by_name('Charmander'),
        get_pokemon_by_name('Charmeleon'),
        get_pokemon_by_name('Charizard'),
    ]
    chain2 = [
        get_pokemon_by_name('Bulbasaur'),
        get_pokemon_by_name('Ivysaur'),
        get_pokemon_by_name('Venusaur'),
    ]
    # Add two copies of each card in both chains
    selected = []
    for card in chain1 + chain2:
        if card:
            selected.extend([card, card])
    # Fill to 20 cards with other basics if needed
    if len(selected) < 20:
        other_basics = get_pokemon_by_criteria(lambda c: c.get('evolution_type') == 'Basic' and c.get('name') not in [c['name'] for c in selected], 20 - len(selected))
        selected.extend(other_basics)
    # Build deck_cards with up to 2 copies per card
    name_counts = {}
    deck_cards = []
    for card in selected:
        name = card.get('name', 'Unknown')
        if name_counts.get(name, 0) < 2:
            deck_cards.append(Pokemon(card_data=card))
            name_counts[name] = name_counts.get(name, 0) + 1
        if len(deck_cards) >= 20:
            break
    # Use all element types found in the deck for energy
    energy_types = list({card.get('type') for card in selected if card.get('type')})
    if not energy_types:
        energy_types = [ElementType.FIRE, ElementType.GRASS]
    if energy_types:
        energy_types = [ElementType[type_str.upper()] for type_str in energy_types if type_str.upper() in ElementType.__members__]
    return Deck(deck_cards, energy_types)

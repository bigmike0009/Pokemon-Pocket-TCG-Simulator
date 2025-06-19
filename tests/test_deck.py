"""Test deck implementation."""
import pytest
from src.deck import Deck
from src.pokemon import Pokemon
from src.trainer import Item, Supporter, Tool

def create_mock_card(name: str, card_type: str = "Trainer - Item", evolution_type: str = None):
    """Helper to create mock cards for testing."""
    card_data = {
        'id': '1',
        'name': name,
        'card_type': card_type,
        'evolution_type': evolution_type
    }
    
    if 'Pokémon' in card_type:
        return Pokemon(card_data)
    elif 'Item' in card_type:
        return Item(card_data)
    elif 'Supporter' in card_type:
        return Supporter(card_data)
    else:
        return Tool(card_data)

def test_valid_deck():
    # Create a valid deck with 20 cards including 1 basic Pokemon
    cards = [
        create_mock_card("Pikachu", "Pokémon - Basic", "Basic"),  # 1 basic Pokemon
        *[create_mock_card("Potion") for _ in range(10)],  # 10 copies of different items
        *[create_mock_card("Pokeball") for _ in range(9)]  # 9 copies of different items
    ]
    deck = Deck(cards, ["Electric"])
    assert len(deck) == 20
    
def test_invalid_deck_size():
    # Test deck with wrong size
    cards = [create_mock_card("Potion") for _ in range(19)]  # Only 19 cards
    with pytest.raises(ValueError, match="Deck must contain exactly 20 cards"):
        Deck(cards, ["Fire"])
        
def test_too_many_copies():
    # Test deck with more than 2 copies of a card
    cards = [
        create_mock_card("Pikachu", "Pokémon - Basic", "Basic"),
        *[create_mock_card("Potion") for _ in range(19)]  # 19 copies of same card
    ]
    with pytest.raises(ValueError, match="Deck cannot contain more than 2 copies"):
        Deck(cards, ["Electric"])
        
def test_no_basic_pokemon():
    # Test deck with no basic Pokemon
    cards = [create_mock_card("Potion") for _ in range(20)]
    with pytest.raises(ValueError, match="Deck must contain at least 1 basic Pokemon"):
        Deck(cards, ["Psychic"])
        
def test_no_energy_types():
    # Test deck with no energy types declared
    cards = [
        create_mock_card("Pikachu", "Pokémon - Basic", "Basic"),
        *[create_mock_card("Potion") for _ in range(19)]
    ]
    with pytest.raises(ValueError, match="Deck must declare at least 1 energy type"):
        Deck(cards, [])

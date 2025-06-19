"""Test card implementations."""
import pytest
from src.cards import Card
from src.pokemon import Pokemon
from src.game_state import GameState

def test_pokemon_creation():
    card_data = {
        'id': '9',
        'name': 'Pikachu',
        'hp': '60',
        'card_type': 'Pokémon - Basic',
        'evolution_type': 'Basic',
        'weakness': 'Fighting',
        'retreat': '1',
        'ex': 'No'
    }
    
    pokemon = Pokemon(card_data)
    assert pokemon.name == 'Pikachu'
    assert pokemon.hp == 60
    assert pokemon.evolution_type == 'Basic'
    assert pokemon.weakness == 'Fighting'
    assert not pokemon.is_ex
    
def test_pokemon_damage():
    card_data = {
        'id': '9',
        'name': 'Pikachu',
        'hp': '60',
        'card_type': 'Pokémon - Basic',
        'evolution_type': 'Basic'
    }
    
    pokemon = Pokemon(card_data)
    assert not pokemon.is_knocked_out()
    
    pokemon.damage_counters = 60
    assert pokemon.is_knocked_out()

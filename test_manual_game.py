from src.cards import Card
from src.pokemon import Pokemon
from src.elementTypes import ElementType
from src.deck import Deck
from src.game import Game
from src.deck_factory import create_real_test_deck

# Create Deck objects
player1_deck = create_real_test_deck()
player2_deck = create_real_test_deck()

game = Game("Ash", player1_deck, "Gary", player2_deck, manual=True)

# Initialize next_energy for both players using their deck's energy_types
# This must be done after GameState and players are set up, but before the game starts
for idx, deck in enumerate([player1_deck, player2_deck]):
    game.state.initialize_player_energy(idx, deck.energy_types)

winner = game.run()
print(f"Winner: {winner}")

# The test decks now contain duplicate evolution chains (e.g., 2x Charmander, 2x Charmeleon, 2x Charizard, etc.) for evolution testing.
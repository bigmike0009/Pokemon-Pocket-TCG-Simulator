import random
from src.game import Game
from src.cards import Card
from src.pokemon import Pokemon

def create_test_deck():
    """Create a test deck with at least one basic Pokémon."""
    deck = []
    # Add a basic Pokémon
    deck.append(Pokemon(card_data={
        "name": "Basic Pokémon",
        "evolution_type": "Basic",
        "element_type": "Fire",
        "hp": 50,
        "attacks": [],
        "card_type": "Pokemon Fire"
    }))
    # Add other Pokémon cards to make up 20 cards
    for i in range(19):
        deck.append(Pokemon(card_data={
            "name": f"Card {i+1}",
            "evolution_type": "Basic",
            "element_type": "Water",
            "hp": 30,
            "attacks": [],
            "card_type": "Pokemon Water"
        }))
    return deck

def test_gameplay_setup(manual=True):
    """Test the initial gameplay setup."""
    # Create test decks for both players
    player1_deck = create_test_deck()
    player2_deck = create_test_deck()

    # Initialize the game with manual flag
    game = Game("Player 1", player1_deck, "Player 2", player2_deck, manual=manual)

    # Run the setup
    game.setup_game()

    # Check that both players have 5 cards in hand
    assert len(game.state.players[0].hand) == 5, "Player 1 should have 5 cards in hand."
    assert len(game.state.players[1].hand) == 5, "Player 2 should have 5 cards in hand."

    # Check that both players have at least one basic Pokémon in hand
    assert game.state.players[0].has_basic_pokemon(), "Player 1 should have a basic Pokémon in hand."
    assert game.state.players[1].has_basic_pokemon(), "Player 2 should have a basic Pokémon in hand."

    # Check that the decks are shuffled and reduced by 5 cards
    assert len(game.state.players[0].deck) == 15, "Player 1's deck should have 15 cards remaining."
    assert len(game.state.players[1].deck) == 15, "Player 2's deck should have 15 cards remaining."

    print("Gameplay setup test passed!")
    return game

def test_manual_game():
    """Test manual game setup and initial display."""
    game = test_gameplay_setup(manual=True)
    try:
        # Start the game and check if it displays the board
        game._display_game_board()
        print("Manual game test passed!")
    except Exception as e:
        print(f"Manual game test failed: {str(e)}")

def test_simulated_game():
    """Test simulated game setup and AI decision making."""
    game = test_gameplay_setup(manual=False)
    try:
        # Start the game and check if it handles AI decisions
        game._handle_main_phase()
        print("Simulated game test passed!")
    except Exception as e:
        print(f"Simulated game test failed: {str(e)}")

if __name__ == "__main__":
    print("Testing manual game setup...")
    test_manual_game()
    print("\nTesting simulated game setup...")
    test_simulated_game()

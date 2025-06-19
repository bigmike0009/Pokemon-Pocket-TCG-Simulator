"""Test the board visualization."""
import pytest
from src.board_view import BoardView
from src.game_state import GameState
from src.pokemon import Pokemon, ElementType, StatusCondition
from src.active_pokemon import ActivePokemon
from src.trainer import Tool, Item, Supporter
from src.game import Player
from src.cards import Card

class MockCard(Card):
    def __init__(self, data: dict):
        self.name = data.get('name', 'Unknown')
        self.card_type = data.get('card_type', 'Trainer - Item')
        self.ability = {'name': 'Effect', 'effect': data.get('effect', 'No effect')}

    def play(self, game_state: 'GameState') -> bool:
        return True

def test_board_visualization():
    """Test basic board visualization."""
    game_state = GameState()
    
    # Create players with decks and discard piles
    player1_deck = [MockCard({'name': f'Card{i}'}) for i in range(15)]
    player2_deck = [MockCard({'name': f'Card{i}'}) for i in range(12)]
    game_state.players = [
        Player("Player 1", player1_deck),
        Player("Player 2", player2_deck)
    ]
    
    # Add some cards to discard piles
    game_state.players[0].discard_pile = [MockCard({'name': f'Discard{i}'}) for i in range(3)]
    game_state.players[1].discard_pile = [MockCard({'name': f'Discard{i}'}) for i in range(5)]

    # Create a sample Pokemon
    pikachu_data = {
        'name': 'Pikachu',
        'hp': 60,
        'card_type': 'Pokémon - Basic Lightning',
        'evolution_type': 'Basic',
        'element_type': 'Lightning',
        'weakness': 'Fighting',
        'retreat': 1,
        'attacks': [
            {
                'name': 'Thunder Shock',
                'cost': ['Lightning'],
                'damage': '20',
                'effect': 'Flip a coin. If heads, the opponent\'s Pokémon is paralyzed.'
            }
        ],
        'ability': {
            'name': 'Static',
            'effect': 'When this Pokémon is attacked, the attacking Pokémon might become paralyzed.'
        }
    }
    
    charmander_data = {
        'name': 'Charmander',
        'hp': 70,
        'card_type': 'Pokémon - Basic Fire',
        'evolution_type': 'Basic',
        'element_type': 'Fire',
        'weakness': 'Water',
        'retreat': 1,
        'attacks': [
            {
                'name': 'Ember',
                'cost': ['Fire'],
                'damage': '30',
                'effect': None
            }
        ]
    }
    
    # Create Pokemon instances
    pikachu = ActivePokemon(Pokemon(pikachu_data), 1)
    charmander = ActivePokemon(Pokemon(charmander_data), 1)
    
    # Set up a test game state
    game_state.active_pokemon[0] = pikachu
    game_state.benched_pokemon[0].append(charmander)
    
    # Add energy to energy zones and set next energy
    game_state.energy_zones[0] = ElementType.LIGHTNING
    game_state.next_energy[0] = ElementType.FIRE
    game_state.energy_zones[1] = ElementType.WATER
    game_state.next_energy[1] = ElementType.GRASS
    
    # Create trainer cards with abilities/effects
    ultra_ball = Item({
        'name': 'Ultra Ball',
        'card_type': 'Trainer - Item',
        'ability': {
            'name': 'Pokemon Search',
            'effect': 'Discard 2 cards from your hand. Search your deck for a Basic Pokemon.'
        }
    })
    
    professors_research = Supporter({
        'name': 'Professor\'s Research',
        'card_type': 'Trainer - Supporter',
        'ability': {
            'name': 'Draw Power',
            'effect': 'Discard your hand and draw 7 cards.'
        }
    })
    
    muscle_band = Tool({
        'name': 'Muscle Band',
        'card_type': 'Trainer - Tool',
        'ability': {
            'name': 'Power Boost',
            'effect': 'The Pokémon this card is attached to does 20 more damage.'
        }
    })

    # Add cards to hands
    game_state.hands[0] = [
        Pokemon(pikachu_data),
        Pokemon(charmander_data),
        ultra_ball,
        professors_research,
        muscle_band
    ]
    game_state.hands[1] = [
        MockCard({'name': 'Card1'}),
        MockCard({'name': 'Card2'})
    ]
    
    # Set some scores
    game_state.scores[0] = 1
    game_state.scores[1] = 2
    
    # Create the board view and render
    board_view = BoardView()
    print("\nBasic board visualization with trainer cards:")
    board_view.render(game_state)
    board_view.render_turn_info(1, "Player 1")
    
    # Verify counts
    assert len(game_state.players[0].deck) == 15
    assert len(game_state.players[0].discard_pile) == 3
    assert len(game_state.players[1].deck) == 12
    assert len(game_state.players[1].discard_pile) == 5
    assert len(game_state.hands[0]) == 5  # Verify hand has all cards

def test_comprehensive_board():
    """Test board visualization with multiple complex scenarios."""
    game_state = GameState()
    
    # Create players with decks and discard piles
    player1_deck = [MockCard({'name': f'Card{i}'}) for i in range(10)]
    player2_deck = [MockCard({'name': f'Card{i}'}) for i in range(8)]
    game_state.players = [
        Player("Player 1", player1_deck),
        Player("Player 2", player2_deck)
    ]
    
    # Add some cards to discard piles
    for _ in range(7):
        game_state.players[0].discard_pile.append(MockCard({'name': 'Discarded Card'}))
    for _ in range(4):
        game_state.players[1].discard_pile.append(MockCard({'name': 'Discarded Card'}))

    # Create various Pokemon data
    charizard_ex_data = {
        'name': 'Charizard',
        'hp': 220,
        'card_type': 'Pokémon - Stage 2 Fire',
        'evolution_type': 'Stage 2',
        'element_type': 'Fire',
        'weakness': 'Water',
        'retreat': 2,
        'ex': 'Yes',
        'attacks': [
            {
                'name': 'Fire Spin',
                'cost': ['Fire', 'Fire'],
                'damage': '180',
                'effect': 'Discard 2 Energy attached to this Pokémon'
            }
        ],
        'ability': {
            'name': 'Burning Spirit',
            'effect': 'Your Fire Pokémon\'s attacks do 30 more damage.'
        }
    }
    
    mew_data = {
        'name': 'Mew',
        'hp': 70,
        'card_type': 'Pokémon - Basic Psychic',
        'evolution_type': 'Basic',
        'element_type': 'Psychic',
        'weakness': 'Darkness',
        'retreat': 1,
        'attacks': [
            {
                'name': 'Psywave',
                'cost': ['Psychic'],
                'damage': '30',
                'effect': None
            }
        ]
    }
    
    snorlax_data = {
        'name': 'Snorlax',
        'hp': 140,
        'card_type': 'Pokémon - Basic Colorless',
        'evolution_type': 'Basic',
        'element_type': 'Colorless',
        'weakness': 'Fighting',
        'retreat': 4,
        'attacks': [
            {
                'name': 'Body Slam',
                'cost': ['Colorless', 'Colorless', 'Colorless'],
                'damage': '90',
                'effect': 'Flip a coin. If heads, your opponent\'s Active Pokémon is now Paralyzed.'
            }
        ],
        'ability': {
            'name': 'Gourmet Time',
            'effect': 'Once during your turn, heal 30 damage from this Pokémon.'
        }
    }
    
    # Create Pokemon instances
    charizard_ex = ActivePokemon(Pokemon(charizard_ex_data), 1)
    mew = ActivePokemon(Pokemon(mew_data), 1)
    snorlax = ActivePokemon(Pokemon(snorlax_data), 1)
    
    # Set up player 1's board
    game_state.active_pokemon[0] = charizard_ex  # Place as active
    game_state.benched_pokemon[0].extend([mew])  # Place on bench
    
    # Set up opponent's Pokemon and bench
    game_state.active_pokemon[1] = snorlax  # Snorlax as active
    game_state.benched_pokemon[1].extend([
        ActivePokemon(Pokemon(mew_data), 1),
        ActivePokemon(Pokemon(charizard_ex_data), 1)
    ])  # Add Mew and Charizard to opponent's bench
    
    # Add status conditions
    game_state.active_pokemon[0].status = StatusCondition.BURN
    game_state.active_pokemon[1].status = StatusCondition.PARALYSIS
    
    # Create and attach tool cards
    muscle_band = Tool({'name': 'Muscle Band', 'card_type': 'Trainer - Tool', 'effect': 'Attacks do 20 more damage'})
    expert_belt = Tool({'name': 'Expert Belt', 'card_type': 'Trainer - Tool', 'effect': '+20 HP and attacks do 20 more damage'})
    
    # Attach tools to Pokémon
    game_state.attach_tool(muscle_band, game_state.active_pokemon[0])
    game_state.attach_tool(expert_belt, game_state.active_pokemon[1])
    
    # Set energies
    game_state.energy_zones[0] = ElementType.FIRE
    game_state.next_energy[0] = ElementType.PSYCHIC
    game_state.energy_zones[1] = ElementType.WATER
    game_state.next_energy[1] = ElementType.LIGHTNING
      # Add cards to hands
    # Add Trainer cards to hands
    game_state.hands[0] = [
        Tool({'name': 'Ultra Ball', 'card_type': 'Trainer - Item', 'effect': 'Discard 2 cards from your hand. Search your deck for a Basic Pokemon.'}),
        Tool({'name': 'Switch', 'card_type': 'Trainer - Item', 'effect': 'Switch your active Pokemon with one of your benched Pokemon.'}),
        Tool({'name': 'Energy Retrieval', 'card_type': 'Trainer - Item', 'effect': 'Put 2 basic Energy cards from your discard pile into your hand.'})
    ]
    game_state.hands[1] = [
        Tool({'name': 'Rare Candy', 'card_type': 'Trainer - Item', 'effect': 'Evolve 1 of your Basic Pokemon into a Stage 2.'}),
        Tool({'name': 'Professor\'s Research', 'card_type': 'Trainer - Supporter', 'effect': 'Discard your hand and draw 7 cards.'})
    ]
    
    # Set scores
    game_state.scores[0] = 2  # Player 1 close to winning
    game_state.scores[1] = 1  # Player 2
    
    # Create the board view and render
    board_view = BoardView()
    print("\nComprehensive board test visualization:")
    board_view.render(game_state)
    board_view.render_turn_info(15, "Player 2")  # Showing turn 15, Player 2's turn
    
    # Verify bench Pokemon counts
    assert len(game_state.benched_pokemon[0]) == 1  # Player has 1 benched Pokemon
    assert len(game_state.benched_pokemon[1]) == 2  # Opponent has 2 benched Pokemon

def test_hand_display():
    """Test that cards in hand are displayed with full details."""
    game_state = GameState()
    
    # Create players with empty decks
    player1_deck = []
    player2_deck = []
    game_state.players = [
        Player("Player 1", player1_deck),
        Player("Player 2", player2_deck)
    ]
    
    # Create a Pokemon and a Trainer card
    pikachu_data = {
        'name': 'Pikachu',
        'hp': 60,
        'card_type': 'Pokémon - Basic Lightning',
        'evolution_type': 'Basic',
        'element_type': 'Lightning',
        'weakness': 'Fighting',
        'retreat': 1,
        'attacks': [
            {
                'name': 'Thunder Shock',
                'cost': ['Lightning'],
                'damage': '20',
                'effect': 'Flip a coin. If heads, paralyze.'
            }
        ]
    }
    
    # Add cards to player's hand
    game_state.hands[0] = [
        Pokemon(pikachu_data),
        Tool({'name': 'Quick Ball', 'card_type': 'Trainer - Item', 'effect': 'Search your deck for a Basic Pokemon.'})
    ]    # Add cards to opponent's hand
    game_state.hands[1] = [
        Pokemon(pikachu_data),  # Add a Pikachu
        Tool({'name': 'Great Ball', 'card_type': 'Trainer - Item', 'effect': 'Look at 7 cards from your deck.'})  # Add a trainer card
    ]
    
    # Create the board view and render
    board_view = BoardView()
    print("\nHand display test visualization:")
    board_view.render(game_state)
      # Add assertions to verify the hand counts
    assert len(game_state.hands[0]) == 2
    assert len(game_state.hands[1]) == 2  # Updated to match the two cards we added to opponent's hand

def test_full_game_state():
    """Test board visualization with a complete game state including all elements."""
    game_state = GameState()
    
    # Create diverse deck contents
    player1_deck = [
        Pokemon({
            'name': 'Squirtle',
            'hp': 70,
            'card_type': 'Pokémon - Basic Water',
            'evolution_type': 'Basic',
            'element_type': 'Water',
            'weakness': 'Lightning',
            'retreat': 1,
            'attacks': [{'name': 'Bubble', 'cost': ['Water'], 'damage': '20', 'effect': None}]
        }),
        Tool({'name': 'Great Ball', 'card_type': 'Trainer - Item', 'effect': 'Look at 7 cards from the top of your deck. You may reveal a Pokemon you find there and put it into your hand.'}),
        Tool({'name': 'Energy Switch', 'card_type': 'Trainer - Item', 'effect': 'Move a basic Energy from 1 of your Pokemon to another.'})
    ]
    player2_deck = [
        Pokemon({
            'name': 'Vulpix',
            'hp': 60,
            'card_type': 'Pokémon - Basic Fire',
            'evolution_type': 'Basic',
            'element_type': 'Fire',
            'weakness': 'Water',
            'retreat': 1,
            'attacks': [{'name': 'Ember', 'cost': ['Fire'], 'damage': '30', 'effect': None}]
        }),
        Tool({'name': 'Potion', 'card_type': 'Trainer - Item', 'effect': 'Heal 30 damage from 1 of your Pokemon.'})
    ]
    
    game_state.players = [
        Player("Player 1", player1_deck),
        Player("Player 2", player2_deck)
    ]
    
    # Add cards to discard piles (mix of Pokemon and Trainers)
    game_state.players[0].discard_pile = [
        Pokemon({
            'name': 'Magikarp',
            'hp': 30,
            'card_type': 'Pokémon - Basic Water',
            'evolution_type': 'Basic',
            'element_type': 'Water',
            'weakness': 'Lightning',
            'retreat': 1,
            'attacks': [{'name': 'Splash', 'cost': [], 'damage': '0', 'effect': None}]
        }),
        Tool({'name': 'Pokemon Communication', 'card_type': 'Trainer - Item', 'effect': 'Reveal a Pokemon from your hand. Put it into your deck and search your deck for a Pokemon to put into your hand.'})
    ]
    game_state.players[1].discard_pile = [
        Tool({'name': 'Professor\'s Research', 'card_type': 'Trainer - Supporter', 'effect': 'Discard your hand and draw 7 cards.'})
    ]
    
    # Create active Pokemon with varying stats and conditions
    charizard_ex = ActivePokemon(Pokemon({
        'name': 'Charizard',
        'hp': 300,
        'card_type': 'Pokémon - Stage 2 Fire',
        'evolution_type': 'Stage 2',
        'element_type': 'Fire',
        'weakness': 'Water',
        'retreat': 3,
        'ex': 'Yes',
        'attacks': [
            {
                'name': 'Fire Spin',
                'cost': ['Fire', 'Fire', 'Colorless'],
                'damage': '220',
                'effect': 'Discard 2 Energy attached to this Pokémon'
            },
            {
                'name': 'Wing Attack',
                'cost': ['Colorless', 'Colorless'],
                'damage': '70',
                'effect': None
            }
        ],
        'ability': {
            'name': 'Dragon\'s Roar',
            'effect': 'Once during your turn, you may attach a Fire Energy card from your discard pile to this Pokemon.'
        }
    }), 1)
    
    mewtwo = ActivePokemon(Pokemon({
        'name': 'Mewtwo',
        'hp': 170,
        'card_type': 'Pokémon - Basic Psychic',
        'evolution_type': 'Basic',
        'element_type': 'Psychic',
        'weakness': 'Darkness',
        'retreat': 2,
        'attacks': [
            {
                'name': 'Psystrike',
                'cost': ['Psychic', 'Psychic', 'Colorless'],
                'damage': '130',
                'effect': 'This attack\'s damage isn\'t affected by Weakness or Resistance.'
            }
        ],
        'ability': {
            'name': 'Pressure',
            'effect': 'If this Pokemon is your Active Pokemon, your opponent\'s attacks cost 1 more Energy.'
        }
    }), 1)
      # Set up active Pokemon with damage and status
    charizard_ex.damage_counters = 120  # Taken 120 damage
    mewtwo.damage_counters = 80  # Taken 80 damage
    charizard_ex.status = StatusCondition.BURN
    mewtwo.status = StatusCondition.PARALYSIS
      # Add energy to active Pokemon
    charizard_ex.attached_energies[ElementType.FIRE] = 2
    charizard_ex.attached_energies[ElementType.COLORLESS] = 1
    mewtwo.attached_energies[ElementType.PSYCHIC] = 2
    
    # Create and attach tools
    muscle_band = Tool({'name': 'Muscle Band', 'card_type': 'Trainer - Tool', 'effect': 'The attacks of the Pokemon this card is attached to do 20 more damage to your opponent\'s Active Pokemon.'})
    air_balloon = Tool({'name': 'Air Balloon', 'card_type': 'Trainer - Tool', 'effect': 'The retreat cost of the Pokemon this card is attached to is 2 less.'})
    
    game_state.attach_tool(muscle_band, charizard_ex)
    game_state.attach_tool(air_balloon, mewtwo)
    
    # Set up benched Pokemon
    pikachu = ActivePokemon(Pokemon({
        'name': 'Pikachu',
        'hp': 60,
        'card_type': 'Pokémon - Basic Lightning',
        'evolution_type': 'Basic',
        'element_type': 'Lightning',
        'weakness': 'Fighting',
        'retreat': 1,
        'attacks': [{'name': 'Thunder Shock', 'cost': ['Lightning'], 'damage': '20', 'effect': 'Flip a coin. If heads, paralyze.'}]
    }), 1)
    
    snorlax = ActivePokemon(Pokemon({
        'name': 'Snorlax',
        'hp': 140,
        'card_type': 'Pokémon - Basic Colorless',
        'evolution_type': 'Basic',
        'element_type': 'Colorless',
        'weakness': 'Fighting',
        'retreat': 4,
        'attacks': [
            {
                'name': 'Body Slam',
                'cost': ['Colorless', 'Colorless', 'Colorless'],
                'damage': '90',
                'effect': 'Flip a coin. If heads, paralyze.'
            }
        ]
    }), 1)
      # Add Pokemon to bench with some damage
    game_state.benched_pokemon[0].extend([pikachu])  # Player's bench
    game_state.benched_pokemon[1].extend([snorlax])  # Opponent's bench
    pikachu.damage_counters = 20  # Taken 20 damage
    snorlax.damage_counters = 50  # Taken 50 damage
    
    # Add energy to benched Pokemon
    pikachu.attached_energies[ElementType.LIGHTNING] = 1
    
    # Set up active Pokemon
    game_state.active_pokemon[0] = charizard_ex
    game_state.active_pokemon[1] = mewtwo
    
    # Set up hands with mixed card types
    game_state.hands[0] = [
        Pokemon({
            'name': 'Charmander',
            'hp': 70,
            'card_type': 'Pokémon - Basic Fire',
            'evolution_type': 'Basic',
            'element_type': 'Fire',
            'weakness': 'Water',
            'retreat': 1,
            'attacks': [{'name': 'Scratch', 'cost': ['Colorless'], 'damage': '10', 'effect': None}]
        }),
        Pokemon({
            'name': 'Charmeleon',
            'hp': 90,
            'card_type': 'Pokémon - Stage 1 Fire',
            'evolution_type': 'Stage 1',
            'element_type': 'Fire',
            'weakness': 'Water',
            'retreat': 1,
            'attacks': [{'name': 'Flame Tail', 'cost': ['Fire', 'Colorless'], 'damage': '50', 'effect': None}]
        }),
        Tool({'name': 'Ultra Ball', 'card_type': 'Trainer - Item', 'effect': 'Discard 2 cards from your hand. Search your deck for a Pokemon and put it into your hand.'}),
        Tool({'name': 'Boss\'s Orders', 'card_type': 'Trainer - Supporter', 'effect': 'Switch your opponent\'s Active Pokemon with 1 of their Benched Pokemon.'})
    ]
    
    # Add opponent's hand with actual cards
    game_state.hands[1] = [
        Tool({'name': 'Switch', 'card_type': 'Trainer - Item', 'effect': 'Switch your active Pokemon with one of your benched Pokemon.'}),
        Tool({'name': 'Rare Candy', 'card_type': 'Trainer - Item', 'effect': 'Evolve 1 of your Basic Pokemon into a Stage 2.'}),
        Pokemon({
            'name': 'Magikarp',
            'hp': 30,
            'card_type': 'Pokémon - Basic Water',
            'evolution_type': 'Basic',
            'element_type': 'Water',
            'weakness': 'Lightning',
            'retreat': 1,
            'attacks': [{'name': 'Splash', 'cost': [], 'damage': '10', 'effect': None}]
        })
    ]
    
    # Set up energy zones
    game_state.energy_zones[0] = ElementType.FIRE
    game_state.next_energy[0] = ElementType.PSYCHIC
    game_state.energy_zones[1] = ElementType.WATER
    game_state.next_energy[1] = ElementType.LIGHTNING
    
    # Set scores
    game_state.scores[0] = 3
    game_state.scores[1] = 2
    game_state.active_hand_card[0] = 1
    
    # Create the board view and render
    board_view = BoardView()
    print("\nFull game state visualization:")
    board_view.render(game_state)
    board_view.render_turn_info(7, "Player 1")  # Turn 7, Player 1's turn    # Verify the game state

    assert len(game_state.hands[0]) == 4  # Player has 4 cards in hand
    assert len(game_state.hands[1]) == 3  # Opponent has 3 cards in hand
    assert len(game_state.benched_pokemon[0]) == 1  # Player has 1 benched Pokemon
    assert len(game_state.benched_pokemon[1]) == 1  # Opponent has 1 benched Pokemon
    assert game_state.active_pokemon[0].current_hp == 180  # Charizard EX has taken 120 damage
    assert game_state.active_pokemon[1].current_hp == 90  # Mewtwo has taken 80 damage
    
    # Verify energy counts
    charizard_energies = game_state.active_pokemon[0].attached_energies
    assert charizard_energies[ElementType.FIRE] == 2  # 2 Fire energy
    assert charizard_energies[ElementType.COLORLESS] == 1  # 1 Colorless energy
    # Verify Mewtwo's energy
    mewtwo_energies = game_state.active_pokemon[1].attached_energies
    assert mewtwo_energies[ElementType.PSYCHIC] == 2  # 2 Psychic energy

if __name__ == '__main__':
    # Run all visualization tests
    test_board_visualization()
    test_comprehensive_board()
    test_hand_display()
    test_full_game_state()

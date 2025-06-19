"""Game state management."""
from typing import List, Dict, Optional, Set, TYPE_CHECKING
from .pokemon import ElementType

from .pokemon import Pokemon
from .active_pokemon import ActivePokemon
from .trainer import Trainer, Item, Supporter, Tool

class GameState:
    def __init__(self):
        # Basic game state
        self.players = []
        self.current_player_idx = 0
        self.turn_number = 0
        self.supporter_played_this_turn = False
        
        # Board state
        self.active_pokemon: Dict[int, Optional['ActivePokemon']] = {0: None, 1: None}
        self.benched_pokemon: Dict[int, List['ActivePokemon']] = {0: [], 1: []}
        self.scores = {0: 0, 1: 0}
        
        # Energy tracking
        self.energy_zones = {0: None, 1: None}  # Current available energy for each player
        self.next_energy = {0: None, 1: None}  # Next energy to be added for each player
        
        # Hand tracking
        self.hands = {0: [], 1: []}  # List of cards in each player's hand
        self.active_hand_card = {0: 1, 1: 1}  # Currently selected card in each player's hand
    
        # Discard piles
        self.card_discard_piles = {0: [], 1: []}  # For discarded cards (Pokemon, Trainer, etc.)
        self.energy_discard_piles = {0: [], 1: []}  # For discarded energy (ElementType)
    
    @property
    def player_score(self) -> int:
        """Get current player's score."""
        return self.scores[0]
        
    @property
    def opponent_score(self) -> int:
        """Get opponent's score."""
        return self.scores[1]
        
    @property
    def player_energy_zone(self) -> Optional[ElementType]:
        """Get current player's available energy."""
        return self.energy_zones[0]
        
    @property
    def opponent_energy_zone(self) -> Optional[ElementType]:
        """Get opponent's available energy."""
        return self.energy_zones[1]
        
    @property
    def player_hand(self) -> List:
        """Get current player's hand."""
        return self.hands[0]
        
    @property
    def opponent_hand(self) -> List:
        """Get opponent's hand."""
        return self.hands[1]
        
    @property
    def player_active(self) -> Optional['ActivePokemon']:
        """Get current player's active Pokemon."""
        return self.active_pokemon[0]
        
    @property
    def opponent_active(self) -> Optional['ActivePokemon']:
        """Get opponent's active Pokemon."""
        return self.active_pokemon[1]
        
    @property
    def player_bench(self) -> List['ActivePokemon']:
        """Get current player's bench."""
        return self.benched_pokemon[0]
        
    @property
    def opponent_bench(self) -> List['ActivePokemon']:
        """Get opponent's bench."""
        return self.benched_pokemon[1]
        
    @property
    def player_card_discard(self):
        """Get current player's card discard pile."""
        return self.card_discard_piles[0]
        
    @property
    def opponent_card_discard(self):
        """Get opponent's card discard pile."""
        return self.card_discard_piles[1]
        
    @property
    def player_energy_discard(self):
        """Get current player's energy discard pile."""
        return self.energy_discard_piles[0]
        
    @property
    def opponent_energy_discard(self):
        """Get opponent's energy discard pile."""
        return self.energy_discard_piles[1]
        
    def place_basic_pokemon(self, pokemon: Pokemon, turn_played: int) -> bool:
        """Place a basic Pokemon either as active or on bench."""
        if pokemon.evolution_type != 'Basic':
            return False
            
        player = self.current_player_idx
        active_pokemon = ActivePokemon(pokemon, turn_played)
        
        # If no active Pokemon, must place as active
        if not self.active_pokemon[player]:
            self.active_pokemon[player] = active_pokemon
            return True
            
        # Otherwise try to place on bench
        if len(self.benched_pokemon[player]) < 3:
            self.benched_pokemon[player].append(active_pokemon)
            return True
            
        return False
        
    def evolve_pokemon(self, evolution_card: Pokemon, turn_played: int) -> bool:
        """Attempt to evolve a Pokemon on the field.
        
        Args:
            evolution_card: The evolution Pokemon card
            turn_played: The current turn number for evolution timing
        """
        player = self.current_player_idx
        target = None
        
        # Find a Pokemon that can evolve into this one
        all_pokemon = ([self.active_pokemon[player]] if self.active_pokemon[player] else []) + self.benched_pokemon[player]
        for pokemon in all_pokemon:
            if (pokemon and pokemon.card.name == evolution_card.evolution_type and 
                pokemon.can_evolve(turn_played)):
                target = pokemon
                break
                
        if not target:
            return False
            
        # Create new ActivePokemon with evolution card
        evolved = ActivePokemon(evolution_card, turn_played)
        
        # Transfer any attached cards/energy from previous stage
        evolved.attached_energies = target.attached_energies
        evolved.attached_tool = target.attached_tool
        
        # Replace the target Pokemon with evolved form
        if target == self.active_pokemon[player]:
            self.active_pokemon[player] = evolved
        else:
            idx = self.benched_pokemon[player].index(target)
            self.benched_pokemon[player][idx] = evolved
            
        return True
        
    def play_item(self, item: Item) -> bool:
        """Handle item card effects."""
        # Item effects will go here
        pass
        
    def play_supporter(self, supporter: Supporter) -> bool:
        """Handle supporter card effects."""
        if self.supporter_played_this_turn:
            return False
        # Supporter effects will go here
        self.supporter_played_this_turn = True
        return True
        
    def attach_tool(self, tool: Tool, target: ActivePokemon) -> bool:
        """Attach a tool card to a Pokemon."""
        if not target or target.attached_tool:
            return False
        return target.attach_tool(tool)
        
    def add_energy(self, target: ActivePokemon) -> bool:
        """Add energy from the energy zone to a Pokemon."""
        current_energy = self.energy_zones[self.current_player_idx]
        if not current_energy:
            return False
            
        # Attach the current energy
        target.attach_energy(current_energy)
        
        # Move next energy to current if available
        self.energy_zones[self.current_player_idx] = self.next_energy[self.current_player_idx]
        self.next_energy[self.current_player_idx] = None
        return True
        
    def end_turn(self):
        """Handle end of turn effects."""
        player = self.current_player_idx
        
        # Apply status effects
        if self.active_pokemon[player]:
            damage = self.active_pokemon[player].apply_status_effects()
            if damage > 0:
                self.apply_damage(self.active_pokemon[player], damage)
                
        for pokemon in self.benched_pokemon[player]:
            if pokemon:
                damage = pokemon.apply_status_effects()
                if damage > 0:
                    self.apply_damage(pokemon, damage)
        
        # Switch players
        self.current_player_idx = 1 - self.current_player_idx
        self.turn_number += 1
        
    def apply_damage(self, target, damage: int, owner_idx: int = None):
        """Apply damage to a Pokemon and check if it's knocked out. owner_idx specifies which player's field to remove from."""
        target.damage_counters += damage
        if target.is_knocked_out():
            # If owner_idx is not provided, default to opponent of current player (legacy)
            if owner_idx is None:
                owner_idx = 1 - self.current_player_idx
            # Increment score
            self.scores[owner_idx] += target.calculate_points()
            # Remove from field
            if target == self.active_pokemon[owner_idx]:
                self.active_pokemon[owner_idx] = None
                if not self.benched_pokemon[owner_idx]:
                    # If no benched Pokemon, player loses
                    if self.check_win_condition() is not None:
                        return
                if hasattr(self, 'faint_callback') and callable(self.faint_callback):
                    self.faint_callback(target, owner_idx)
            else:
                if target in self.benched_pokemon[owner_idx]:
                    self.benched_pokemon[owner_idx].remove(target)
            # Call faint handler if set
            
        
    def check_win_condition(self) -> Optional[int]:
        """Check if either player has won."""
        
        for idx, player in enumerate(self.players):
            if self.scores[idx] >= 3:
                return idx + 1
            active = self.active_pokemon[idx]
            bench = self.benched_pokemon[idx]
            if active is None and not bench:
                # This player has no Pokémon left, opponent wins
                opponent_idx = 1 - idx
                print(f"{player.name} has no Pokémon left! {self.players[opponent_idx].name} wins!")
                return opponent_idx + 1
            
        return None
    
    def set_active_hand_card(self, player_idx: int, card_idx: Optional[int]) -> None:
        """Set the active card in a player's hand.
        
        Args:
            player_idx: The player whose hand to modify (0 or 1)
            card_idx: The index of the card to make active, or None to clear
        """
        if card_idx is not None and card_idx < 0 or card_idx >= len(self.hands[player_idx]):
            self.active_hand_card[player_idx] = None
        else:
            self.active_hand_card[player_idx] = card_idx
            
    def sync_hands_with_players(self):
        """Update self.hands to match the actual player hand lists."""
        for idx, player in enumerate(self.players):
            self.hands[idx] = list(player.hand)
            
    def initialize_player_energy(self, player_idx: int, energy_types: List[ElementType]) -> None:
        """Initialize a player's energy zones with random energy types from their deck.
        
        Args:
            player_idx: The player index (0 or 1)
            energy_types: List of energy types available in the player's deck
        """
        # Start with next_energy filled, energy_zone will be filled on first turn
        import random
        self.next_energy[player_idx] = random.choice(energy_types)
        
    def draw_new_player_energy(self, player_idx: int, energy_types: List[ElementType]) -> None:
        """Update a player's energy zones at the beginning of their turn.
        
        This moves the "next" energy into the active energy zone and draws a new
        random energy for the "next" energy zone.
        
        Args:
            player_idx: The player index (0 or 1)
            energy_types: List of energy types available in the player's deck
        """
        # Move the next energy to the current energy zone
        self.energy_zones[player_idx] = self.next_energy[player_idx]
        
        # Draw a new random energy for the next energy zone
        import random
        self.next_energy[player_idx] = random.choice(energy_types)
        
    def discard_card(self, player_idx: int, card):
        """Move a card to the player's card discard pile."""
        self.card_discard_piles[player_idx].append(card)
        
    def discard_energy(self, player_idx: int, energy_type):
        """Move an energy to the player's energy discard pile."""
        self.energy_discard_piles[player_idx].append(energy_type)
        
    def set_active_pokemon(self, player_idx: int, pokemon: Pokemon):
        """Set the active Pokemon for a player during setup."""
        self.active_pokemon[player_idx] = ActivePokemon(pokemon, turn_played=0)

    def add_benched_pokemon(self, player_idx: int, pokemon: Pokemon):
        """Add a Pokemon to the player's bench during setup (max 3)."""
        if len(self.benched_pokemon[player_idx]) < 3:
            self.benched_pokemon[player_idx].append(ActivePokemon(pokemon, turn_played=0))
            
    def execute_attack(self, attacker: 'ActivePokemon', attack: dict, turn: int) -> None:
        """Execute an attack from the given ActivePokemon using the attack dict."""
        target_type = attack.get('target', 'opponent_active')
        damage = int(attack.get('damage', '0').replace('+', '').replace('-', ''))  # Basic parsing
        opponent_idx = 1 - self.current_player_idx
        targets = []
        
        # Determine targets
        if target_type == 'opponent_active':
            if self.active_pokemon[opponent_idx]:
                targets = [self.active_pokemon[opponent_idx]]
        elif target_type == 'opponent_bench':
            if self.benched_pokemon[opponent_idx]:
                # Pick one at random for now; can add menu for manual
                import random
                targets = [random.choice(self.benched_pokemon[opponent_idx])]
        elif target_type == 'random_opponent':
            all_targets = [p for p in ([self.active_pokemon[opponent_idx]] if self.active_pokemon[opponent_idx] else []) + self.benched_pokemon[opponent_idx]]
            if all_targets:
                import random
                targets = [random.choice(all_targets)]
        elif target_type == 'multi_random':
            all_targets = [p for p in ([self.active_pokemon[opponent_idx]] if self.active_pokemon[opponent_idx] else []) + self.benched_pokemon[opponent_idx]]
            import random
            n = min(2, len(all_targets))  # Example: hit 2 at random
            targets = random.sample(all_targets, n) if all_targets else []
        else:
            # Default to opponent active
            if self.active_pokemon[opponent_idx]:
                targets = [self.active_pokemon[opponent_idx]]
        
        # Apply damage to each target
        for target in targets:
            # Weakness check
            if target.weakness and attacker.element_type.name.upper() == str(target.weakness).upper():
                total_damage = damage + 20
            else:
                total_damage = damage
            self.apply_damage(target, total_damage)
        # TODO: handle attack effects, abilities, and status conditions

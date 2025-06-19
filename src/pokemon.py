"""Pokemon card implementation."""
from typing import Dict, Any, List, TYPE_CHECKING
from .cards import Card
from .elementTypes import ElementType, StatusCondition

if TYPE_CHECKING:
    from .game_state import GameState



class Pokemon(Card):
    def __init__(self, card_data: Dict[str, Any]):
        super().__init__(card_data)
        self.name = card_data.get('name', 'Unknown')
        self.hp = int(card_data.get('hp', 0))
        self.evolution_type = card_data.get('evolution_type', 'Basic')
        self.element_type = self._parse_element_type(card_data)
        self.weakness = card_data.get('weakness')
        self.retreat_cost = int(card_data.get('retreat', 0))
        self.is_ex = card_data.get('ex', 'No') == 'Yes'
        
        # Parse attacks
        self.attacks = self._parse_attacks(card_data.get('attacks', []))
        
        # Parse ability
        ability_data = card_data.get('ability', {})
        self.ability = {
            'name': ability_data.get('name') if ability_data else 'No ability',
            'effect': ability_data.get('effect') if ability_data else 'N/A'
        }
        
    def play(self, game_state: 'GameState', current_turn: int) -> bool:
        """Play this Pokemon card according to game rules."""
        # Check if it's a basic Pokemon or if evolution requirements are met
        if self.evolution_type == 'Basic':
            return game_state.place_basic_pokemon(self, current_turn)
        return game_state.evolve_pokemon(self, current_turn)
    
    def calculate_points(self) -> int:
        """Calculate points value when knocked out."""
        return 2 if self.is_ex else 1
        
    def _parse_element_type(self, card_data: Dict[str, Any]) -> ElementType:
        """Parse the element type from card data."""
        # Extract type from card_type field, e.g., "Pokémon - Basic Fire" -> "Fire"
        type_str = card_data.get('type', '').split()[-1]
        try:
            return ElementType[type_str.upper()]
        except (KeyError, AttributeError):
            return ElementType.COLORLESS

    def _parse_attacks(self, attacks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse attacks data from card definition, including target field."""
        parsed_attacks = []
        for attack in attacks_data:
            parsed_attacks.append({
                'name': attack.get('name', ''),
                'cost': [ElementType[cost.upper()] for cost in attack.get('cost', [])],
                'damage': attack.get('damage', '0'),
                'effect': attack.get('effect', ''),
                'target': attack.get('target', 'opponent_active')  # Default to opponent's active
            })
        return parsed_attacks

"""Active Pokemon implementation for managing Pokemon in play."""
from typing import Dict, Set, Optional
from enum import Enum
import random
from .pokemon import Pokemon, ElementType, StatusCondition
from .trainer import Tool

class ActivePokemon:
    def __init__(self, card: Pokemon, turn_played: int):
        """Initialize an active Pokemon from a Pokemon card.
        
        Args:
            card: The Pokemon card being played
            turn_played: The turn number when this Pokemon was played
        """
        self.card = card
        self.turn_played = turn_played
        
        # Battle state
        self.damage_counters = 0
        self.attached_tool: Optional[Tool] = None
        self.status: Optional[StatusCondition] = None  # Current status condition
        self.status_turn: Optional[int] = None  # Turn when status was applied
        self.attached_energies: Dict[ElementType, int] = {element: 0 for element in ElementType}

    @property
    def name(self) -> str:
        """Get the Pokemon's name."""
        return self.card.name
        
    @property
    def hp(self) -> int:
        """Get the Pokemon's max HP."""
        return self.card.hp
        
    @property
    def current_hp(self) -> int:
        """Get the Pokemon's current HP."""
        return self.hp - self.damage_counters
        
    @property
    def element_type(self) -> ElementType:
        """Get the Pokemon's element type."""
        return self.card.element_type
        
    @property
    def weakness(self) -> Optional[str]:
        """Get the Pokemon's weakness."""
        return self.card.weakness
        
    @property
    def retreat_cost(self) -> int:
        """Get the Pokemon's retreat cost."""
        return self.card.retreat_cost

    def apply_status(self, status: StatusCondition, turn: int) -> None:
        """Apply a status condition to this Pokemon."""
        self.status = status
        self.status_turn = turn

    def clear_status(self) -> None:
        """Clear the current status condition."""
        self.status = None
        self.status_turn = None

    def attach_energy(self, energy_type: ElementType) -> None:
        """Attach energy from energy zone."""
        self.attached_energies[energy_type] += 1

    def remove_energy(self, energy_type: ElementType) -> bool:
        """Remove energy and return it to energy zone."""
        if self.attached_energies[energy_type] > 0:
            self.attached_energies[energy_type] -= 1
            return True
        return False

    def get_total_energy(self) -> int:
        """Get total attached energy count."""
        return sum(self.attached_energies.values())

    def apply_status_effects(self) -> int:
        """Apply status effects at the end of turn. Returns damage dealt."""
        total_damage = 0

        if not hasattr(self,'statcus_conditions'):
            return total_damage
        
        if StatusCondition.POISON in self.statcus_conditions:
            total_damage += 10
            
        if StatusCondition.BURN in self.status_conditions:
            total_damage += 20
            # Burn requires coin flip to remove
            if random.choice([True, False]):
                self.remove_status(StatusCondition.BURN)
                
        return total_damage

    def can_attack(self) -> bool:
        """Check if Pokemon can attack based on energy and status."""
        if StatusCondition.SLEEP in self.status_conditions:
            if random.choice([True, False]):
                self.remove_status(StatusCondition.SLEEP)
                return True
            return False
            
        if StatusCondition.PARALYSIS in self.status_conditions:
            return False
            
        return self.get_total_energy() > 0

    def can_retreat(self) -> bool:
        """Check if Pokemon can retreat."""
        return (self.get_total_energy() >= self.retreat_cost and
                (not hasattr(self,'status_conditions') or StatusCondition.PARALYSIS not in self.status_conditions))

    def is_confused(self) -> bool:
        """Check if Pokemon is confused."""
        return StatusCondition.CONFUSION in self.status_conditions

    def is_knocked_out(self) -> bool:
        """Check if Pokemon is knocked out."""
        return self.damage_counters >= self.card.hp

    def calculate_points(self) -> int:
        """Calculate points value when knocked out."""
        return self.card.calculate_points()

    def can_evolve(self, current_turn: int) -> bool:
        """Check if Pokemon can evolve this turn."""
        return current_turn > self.turn_played and current_turn > 2

    def attach_tool(self, tool: Tool) -> bool:
        """Attach a Pokemon Tool card.
        
        Returns:
            bool: True if tool was attached successfully
        """
        if self.attached_tool is not None:
            return False
        self.attached_tool = tool
        return True

    def remove_tool(self) -> Optional[Tool]:
        """Remove and return the attached tool card."""
        tool = self.attached_tool
        self.attached_tool = None
        return tool

    def can_perform_attack(self, attack: dict) -> bool:
        """Check if this Pokémon can perform the given attack (energy + status)."""
        # Check status conditions
        if self.status is not None:
            if self.status == StatusCondition.SLEEP:
                return False
            if self.status == StatusCondition.PARALYSIS:
                return False
        # Check energy requirements
        attached = self.attached_energies.copy()
        cost = attack.get('cost', [])
        colorless_count = 0
        # First, satisfy all colored energy requirements
        for energy in cost:
            if not isinstance(energy, ElementType):
                try:
                    energy = ElementType[energy.upper()]
                except Exception:
                    if str(energy).upper() == 'COLORLESS':
                        colorless_count += 1
                        continue
                    return False
            if energy.name == 'COLORLESS':
                colorless_count += 1
                continue
            if attached.get(energy, 0) > 0:
                attached[energy] -= 1
            else:
                return False
        # Now check if we have enough remaining energies for colorless
        if colorless_count > 0:
            if sum(attached.values()) < colorless_count:
                return False
        return True

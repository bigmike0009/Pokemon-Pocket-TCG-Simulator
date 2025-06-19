"""CLI-based game board visualizer for Pokemon TCG."""

import os
import re
import platform
from typing import List, Optional
from colorama import init, Fore, Back, Style

from .game_state import GameState
from .pokemon import Pokemon, ElementType, StatusCondition
from .trainer import Tool, Trainer, Item, Supporter
from .active_pokemon import ActivePokemon
from .cards import Card
from .elementTypes import ELEMENT_COLORS, STATUS_COLORS, ELEMENT_SYMBOLS

# Initialize colorama
init()

# Define color mappings for different elements

class BoardView:
    """A class to handle the CLI visualization of the game board."""

    def __init__(self):
        """Initialize the board view."""
        self.clear_command = 'cls' if platform.system() == 'Windows' else 'clear'

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system(self.clear_command)

    def _get_visible_length(self, text: str) -> int:
        """Calculate the visible length of a string, excluding ANSI color codes and accounting for double-width Unicode symbols."""
        import re
        try:
            from wcwidth import wcswidth
        except ImportError:
            # Fallback: basic len if wcwidth is not available
            def wcswidth(s):
                return len(s)
        # Remove all ANSI escape sequences
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_text = ansi_escape.sub('', text)
        return wcswidth(clean_text)

    def _pad_line(self, content: str, total_width: int = 24) -> str:
        """Pad a line to the specified width, accounting for ANSI color codes."""
        visible_length = self._get_visible_length(content)
        needed_padding = max(0, total_width - visible_length)
        return content + " " * needed_padding

    def _draw_empty_card(self, slot_number: Optional[int] = None) -> str:
        """Draw an empty card slot with dashed borders."""
        # Start with top dashed border
        empty_card = ["┌─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐"]
        
        # Match the height of a full Pokemon card (11 lines including borders)
        empty_lines = ["┆                        ┆" for _ in range(8)]
        
        # Insert the slot number or "EMPTY" in the middle
        middle_index = len(empty_lines) // 2
        if slot_number is not None:
            # Ensure the slot number is properly centered and padded
            slot_text = f"#{slot_number}".center(24)
            empty_lines[middle_index] = f"┆{slot_text}┆"
        else:
            empty_lines[middle_index] = "┆         EMPTY          ┆"
        
        empty_card.extend(empty_lines)
        # Add bottom dashed border
        empty_card.append("└─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘")
        
        return "\n".join(empty_card)

    def _draw_pokemon_card(self, pokemon: Optional[ActivePokemon], is_active: bool = False, bench_slot: Optional[int] = None, in_hand=False) -> str:
        """Draw a single Pokemon card representation."""
        CARD_WIDTH = 24  # Standard width for card content
        
        if not pokemon:
            return self._draw_empty_card(bench_slot)

        # Get base colors and data
        color = ELEMENT_COLORS.get(pokemon.element_type, Fore.WHITE)
        status = getattr(pokemon, 'status', None)
        status_color = STATUS_COLORS.get(status, '')
        card_data = pokemon.card
        
        card = []
        
        # Border
        card.append("┌────────────────────────┐")
        
        # Top line: Evolution stage (left) and HP/Element (right)
        element_str = f"{color}{card_data.element_type.value[:3]}{Style.RESET_ALL}"
        evolution = card_data.evolution_type[:10]
        hp_str = f"{pokemon.current_hp:>3}/{card_data.hp:<3}"
        content = f"{evolution:<10} {hp_str} {element_str}"
        card.append(f"│{self._pad_line(content)}│")
        
        # Tool (left) and Status (right)
        tool = getattr(pokemon, 'tool', None)
        tool_str = f"{Fore.YELLOW}{(tool.name if tool else '')[:10]}{Style.RESET_ALL}"
        status_text = f"{status_color}{(status.value if status else '')[:8]}{Style.RESET_ALL}"
        content = f"{tool_str:<10} {status_text:>12}"
        card.append(f"│{self._pad_line(content)}│")
        
        # Name centered with EX
        name = (card_data.name[:16] + (" EX" if card_data.is_ex else ""))[:CARD_WIDTH]
        content = f"{color}{name:^{CARD_WIDTH}}{Style.RESET_ALL}"
        card.append(f"│{self._pad_line(content)}│")
        
        # Ability if present
        if card_data.ability and card_data.ability['name'] != 'No ability':
            ability_name = card_data.ability['name'][:15]
            content = f"{Fore.CYAN}Ability: {ability_name}{Style.RESET_ALL}"
            card.append(f"│{self._pad_line(content)}│")
            # Show full ability effect below
            if in_hand:
                effect_text = card_data.ability.get('effect', '')
                if effect_text:
                    for line in re.findall('.{1,22}', effect_text):
                        card.append(f"│{self._pad_line(Fore.WHITE + line + Style.RESET_ALL)}│")
        else:
            card.append("│                        │")
        # Attack(s) with effect details
        for attack in card_data.attacks:
            energy_cost = []
            for e_type in attack['cost']:
                element = ElementType(e_type)
                e_color = ELEMENT_COLORS.get(element, Fore.WHITE)
                energy_cost.append(f"{e_color}{element.value[0]}{Style.RESET_ALL}")
            cost = "".join(energy_cost)
            
            damage = attack.get('damage', '0')
            has_effect = '(A)' if attack.get('effect') else '   '
            attack_name = attack['name'][:12].center(12)
            content = f"{cost}{attack_name}{has_effect} {damage}"
            card.append(f"│{self._pad_line(content)}│")
            # Show attack effect in detail below (if present)
            if in_hand:
                if attack.get('effect'):
                    for line in re.findall('.{1,22}', attack['effect']):
                        card.append(f"│{self._pad_line(Fore.LIGHTBLACK_EX + line + Style.RESET_ALL)}│")
        # Fill remaining space for attacks
        num_attacks = len(card_data.attacks)
        while num_attacks < 2:
            card.append("│                        │")
            num_attacks += 1
        
        # Weakness and Retreat Cost
        weakness_str = card_data.weakness[:3] if card_data.weakness else '---'
        content = f"WK:{weakness_str:<3} {' '*8}RC: {card_data.retreat_cost:>1}"
        card.append(f"│{self._pad_line(content)}│")
        
        # Energy at bottom
        # Show attached energies using ELEMENT_SYMBOLS and counts
        attached_energies = getattr(pokemon, 'attached_energies', None)
        if attached_energies and any(count > 0 for count in attached_energies.values()):
            # Build a string like: 🔥x2 ⚡x1 💧x3
            energy_strs = []
            for e_type, count in attached_energies.items():
                if count > 0:
                    symbol = ELEMENT_SYMBOLS.get(e_type, '?')
                    energy_strs.append(f"{symbol}x{count}" if count > 1 else f"{symbol}")
            content = " ".join(energy_strs)
            card.append(f"│{self._pad_line(content)}│")
        else:
            card.append("│                        │")
        
        card.append("└────────────────────────┘")
        
        return "\n".join(card)

    def _draw_trainer_card(self, card: 'Trainer') -> str:
        """Draw a trainer card representation."""
        CARD_WIDTH = 24  # Standard width for card content
        
        card_lines = []
        
        # Border
        card_lines.append("┌────────────────────────┐")
        
        # Card type at top (Item/Supporter/Tool)
        card_type = card.card_type if hasattr(card, 'card_type') else card.__class__.__name__
        content = f"{Fore.CYAN}{card_type:^{CARD_WIDTH}}{Style.RESET_ALL}"
        card_lines.append(f"│{self._pad_line(content)}│")

        # Card name
        name = card.name[:CARD_WIDTH]
        content = f"{Fore.YELLOW}{name:^{CARD_WIDTH}}{Style.RESET_ALL}"
        card_lines.append(f"│{self._pad_line(content)}│")
        
        # Blank line
        card_lines.append("│                        │")

        # Effect text (stored in ability field for trainer cards)
        if hasattr(card, 'ability'):
            effect = card.ability
            if isinstance(effect, dict):
                effect_name = effect.get('name', 'Effect')
                effect_text = effect.get('effect', '')
            else:
                effect_name = 'Effect'
                effect_text = effect if isinstance(effect, str) else ''
            
            # Display the effect name like Pokemon abilities
            content = f"{Fore.CYAN}{effect_name}{Style.RESET_ALL}"
            card_lines.append(f"│{self._pad_line(content)}│")
            
            # Split effect text into multiple lines
            while effect_text:
                line = effect_text[:20]
                effect_text = effect_text[20:]
                content = f"{Fore.WHITE}{line}{Style.RESET_ALL}"
                card_lines.append(f"│{self._pad_line(content)}│")
        
        # Fill remaining space to match Pokemon card height
        while len(card_lines) < 9:
            card_lines.append("│                        │")
        
        # Bottom border
        card_lines.append("└────────────────────────┘")
        
        return "\n".join(card_lines)

    def _draw_hand_card(self, card: 'Card') -> str:
        """Draw a card that is in a player's hand."""
        from .pokemon import Pokemon
        from .trainer import Trainer

        if isinstance(card, Pokemon):
            # Create a temporary ActivePokemon without status, tools, or energy
            temp_pokemon = ActivePokemon(card, 1)
            return self._draw_pokemon_card(temp_pokemon, in_hand=True)
        elif isinstance(card, Trainer):
            return self._draw_trainer_card(card)
        else:
            return self._draw_empty_card()  # Fallback for unknown card types

    def _draw_energy_zone(self, current_energy: Optional[ElementType], next_energy: Optional[ElementType]) -> str:
        """Draw the energy zone representation."""
        result = []
        # Current energy
        if current_energy is not None:
            color = ELEMENT_COLORS.get(current_energy, Fore.WHITE)
            symbol = ELEMENT_SYMBOLS.get(current_energy, "?")
            result.append(f"Energy Zone: {color}{symbol}{Style.RESET_ALL}")
        else:
            result.append("Energy Zone: Empty")
        # Next energy preview
        if next_energy is not None:
            color = ELEMENT_COLORS.get(next_energy, Fore.WHITE)
            symbol = ELEMENT_SYMBOLS.get(next_energy, "?")
            result.append(f"Next Energy: {color}{symbol}{Style.RESET_ALL}")
        else:
            result.append("Next Energy: None")
        return " | ".join(result)

    def _draw_score(self, player_score: int, opponent_score: int) -> str:
        """Draw the current score."""
        return f"Score: {Fore.GREEN}{player_score}{Style.RESET_ALL} - {Fore.RED}{opponent_score}{Style.RESET_ALL}"

    def _draw_energy_discard_pile(self, energy_discard: list) -> str:
        """Draw the energy discard pile as a row of energy symbols."""
        if not energy_discard:
            return "(empty)"
        return " ".join(f"{ELEMENT_SYMBOLS.get(e, '?')}" for e in energy_discard)

    def render(self, game_state: GameState, options: Optional[List[dict]] = None):
        """Render the current game state to the terminal, with optional player options menu."""
        self.clear_screen()
        
        # Draw turn indicator and score
        print(self._draw_score(game_state.scores[0], game_state.scores[1]))
        
        print("=" * 80)
        
        # Opponent's deck and discard at the top
        print(f"Opponent's {self._draw_energy_zone(game_state.opponent_energy_zone, game_state.next_energy[1])} | Opponent's Deck: {len(game_state.players[1].deck)} cards | Discard: {len(game_state.opponent_card_discard)} cards | Energy Discard: {self._draw_energy_discard_pile(game_state.opponent_energy_discard)}")
        
       # Draw opponent's hand as list and active card if it's their turn
        print("\nOpponent's Hand:")
        print(self._draw_hand_list(game_state.hands[1], is_opponent=True))
        
        # Draw opponent's pokemon positions
        positions = ["Active"] + ["Bench"] * 3  # Always show all 3 bench positions
        print("\n" + "    ".join(f"{pos:^26}" for pos in positions))
        
        # Draw opponent's pokemon in one row
        pokemon_cards = [self._draw_pokemon_card(game_state.active_pokemon[1])]  # Active slot
        
        # Add bench cards or empty slots for opponent
        bench = game_state.benched_pokemon[1]
        for i in range(3):  # Always process 3 bench slots
            if i < len(bench):
                pokemon_cards.append(self._draw_pokemon_card(bench[i], bench_slot=i+1))
            else:
                pokemon_cards.append(self._draw_pokemon_card(None, bench_slot=i+1))
        
        if pokemon_cards:
            card_lines = ["   ".join(x) for x in zip(*[p.split('\n') for p in pokemon_cards])]
            print("\n".join(card_lines))
        print()
        if not game_state.current_player_idx == 0:
            print(f"{Fore.RED}** OPPONENT'S TURN **{Style.RESET_ALL}")
        # Draw middle section with scores
        print("-" * 110)

        if game_state.current_player_idx == 0:
            print(f"{Fore.GREEN}** YOUR TURN **{Style.RESET_ALL}")
        print()
        
        # Draw player's pokemon in one row
        pokemon_cards = [self._draw_pokemon_card(game_state.active_pokemon[0])]  # Active slot

        # Add bench cards or empty slots for player
        bench = game_state.benched_pokemon[0]
        for i in range(3):  # Always process 3 bench slots
            if i < len(bench):
                pokemon_cards.append(self._draw_pokemon_card(bench[i], bench_slot=i+1))
            else:
                pokemon_cards.append(self._draw_pokemon_card(None, bench_slot=i+1))
        
        if pokemon_cards:
            card_lines = ["   ".join(x) for x in zip(*[p.split('\n') for p in pokemon_cards])]
            print("\n".join(card_lines))

        # Draw player's pokemon positions
        positions = ["Active"] + ["Bench"] * 3  # Always show all 3 bench positions
        print("    ".join(f"{pos:^26}" for pos in positions))
          # Draw player's hand as list and active card if it's their turn
        print("\nYour Hand:")
        print(self._draw_hand_list(game_state.hands[0], is_opponent=False))
        
        # Player's energy zone
        print(f"\nYour {self._draw_energy_zone(game_state.player_energy_zone, game_state.next_energy[0])} | Your Deck: {len(game_state.players[0].deck)} cards | Discard: {len(game_state.player_card_discard)} cards | Energy Discard: {self._draw_energy_discard_pile(game_state.player_energy_discard)}")
        
        print("=" * 80)
        if game_state.turn_number > 0:
            print(f"{Fore.GREEN}Turn #{game_state.turn_number} - {game_state.players[game_state.current_player_idx].name}'s turn{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTBLACK_EX}Setup Phase:{Style.RESET_ALL}")

        if game_state.current_player_idx == 1 and game_state.turn_number > 0:
            print(f"\nOpponent's Selected Card: ({game_state.active_hand_card[1] + 1})")
            print("\n".join(self._draw_active_card_section(game_state, 1)))

        if game_state.current_player_idx == 0 and game_state.turn_number > 0:
            print(f"\nYour Selected Card: ({game_state.active_hand_card[0] +1})")
            print("\n".join(self._draw_active_card_section(game_state, 0)))

        # Display options menu if provided
        # (Moved to game.py for better CLI UX)

    def render_turn_info(self, current_turn: int, active_player: str):
        """Display turn information."""
        
        print(f"\nTurn {current_turn} - {active_player}'s turn")
        print("-" * 80)

    def _draw_hand_list(self, hand: List['Card'], is_opponent: bool = False) -> str:
        """Draw a numbered list of cards in hand with appropriate colors."""
        if not hand:
            return "No cards in hand"
            
        lines = []
        for i, card in enumerate(hand):
            from .pokemon import Pokemon
            from .trainer import Trainer, Item, Supporter, Tool
            
            # Set color based on card type
            if isinstance(card, Pokemon):
                color = ELEMENT_COLORS.get(card.element_type, Fore.WHITE)
            elif isinstance(card, Tool):
                color = Fore.YELLOW
            elif isinstance(card, (Item, Supporter)):
                color = Fore.CYAN
            else:
                color = Fore.WHITE
                
            # Format the line with index and card name
            line = f"{i+1:2d}. {color}{card.name}{Style.RESET_ALL}"
            if isinstance(card, Pokemon):
                line += f" ({card.evolution_type} - {card.element_type.value})"
            elif isinstance(card, Trainer):
                line += f" ({card.card_type})"
            lines.append(line)
            
        #I would like the lines to display 3 to a line, then a newlin
        formatted_lines = []        
        for i in range(0, len(lines), 5):
            formatted_lines.append(" | ".join(lines[i:i+5]))

        

        return "\n".join(formatted_lines)

    def _draw_active_card_section(self, game_state: GameState, player_idx: int) -> List[str]:
        """Draw the active card section for a player."""
        active_idx = game_state.active_hand_card[player_idx]
        if active_idx is None or active_idx >= len(game_state.hands[player_idx]):
            return ["No active card selected"]
            
        active_card = game_state.hands[player_idx][active_idx]
        return self._draw_hand_card(active_card).split('\n')

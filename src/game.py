"""Main game loop and player interaction."""
import random
from typing import List, Optional
from .cards import Card
from .game_state import GameState
from .pokemon import Pokemon
from .board_view import BoardView
from .deck import Deck
import string
import time

class Player:
    def __init__(self, name: str, deck: List[Card], game_state=None, player_idx=None):
        self.name = name
        self.deck = deck
        self.hand: List[Card] = []
        self.discard_pile: List[Card] = []  # Legacy, for compatibility
        self.game_state = game_state  # Reference to GameState for discards
        self.player_idx = player_idx  # 0 or 1
        
    def draw_card(self) -> Optional[Card]:
        """Draw a card from the deck."""
        if not self.deck:
            return None
        card = self.deck.pop()
        self.hand.append(card)
        return card
        
    def discard_card(self, card: Card):
        """Move a card to the discard pile (and GameState pile if available)."""
        if card in self.hand:
            self.hand.remove(card)
        self.discard_pile.append(card)
        if self.game_state is not None and self.player_idx is not None:
            self.game_state.discard_card(self.player_idx, card)
        
    def discard_energy(self, energy_type):
        """Move an energy to the energy discard pile (GameState)."""
        if self.game_state is not None and self.player_idx is not None:
            self.game_state.discard_energy(self.player_idx, energy_type)
        
    def has_basic_pokemon(self) -> bool:
        """Check if there's at least one basic Pokemon in hand."""
        return any(isinstance(card, Pokemon) and card.evolution_type == 'Basic' 
                  for card in self.hand)

class _FallbackDeck:
    def __init__(self, cards):
        from .pokemon import ElementType
        self.cards = cards
        # Fallback: allow all energy types if not specified
        self.energy_types = [e for e in ElementType]

class Game:
    def __init__(self, player1_name: str, player1_deck, player2_name: str, player2_deck, manual: bool = True):
        self.state = GameState()
        self.manual = manual
        self.board_view = BoardView() if manual else None
        self._player_decks = []
        # Always wrap decks so both have energy_types
        for deck in (player1_deck, player2_deck):
            if hasattr(deck, 'energy_types'):
                self._player_decks.append(deck)
            else:
                self._player_decks.append(_FallbackDeck(deck))
        self.state.players = [Player(player1_name, self._player_decks[0].cards, self.state, 0),
                              Player(player2_name, self._player_decks[1].cards, self.state, 1)]
        self._retreated_this_turn = {0: False, 1: False}
        # Register the faint callback
        self.state.faint_callback = self.handle_pokemon_faint

    def handle_pokemon_faint(self, fainted_pokemon, owner_idx):
        """Handle all logic for when a Pokémon faints (is knocked out)."""
        player = self.state.players[owner_idx]
        opponent_idx = 1 - owner_idx
        opponent = self.state.players[opponent_idx]
        # Print faint message
        print(f"\n{player.name}'s {fainted_pokemon.card.name} fainted!")
        # Move to discard pile
        self.state.card_discard_piles[owner_idx].append(fainted_pokemon.card)
        # Remove from board (already done in apply_damage)
        # Score increment is already handled in apply_damage
        # If fainted Pokémon was active, prompt for new active if possible
        if self.state.active_pokemon[owner_idx] is None:
            bench = self.state.benched_pokemon[owner_idx]
            # Redraw board before showing menu
            if self.board_view:
                self.board_view.render(self.state)
            if bench:
                # Prompt player to select a new active Pokémon
                if self.manual:
                    print(f"{player.name}, choose a Benched Pokémon to promote to Active:")
                    options = []
                    for i, poke in enumerate(bench):
                        options.append({
                            'key': str(i+1),
                            'dispkey': str(i+1),
                            'desc': f"Promote: {poke.card.name} (HP: {poke.hp})",
                            'group': 'promote',
                            'bench_idx': i
                        })
                    selected = self._run_menu(options, "Select a Pokémon to promote to Active:")
                    if not selected:
                        # If user cancels, auto-promote first
                        target_idx = 0
                    else:
                        target_idx = selected['bench_idx']
                else:
                    # Auto: promote first benched Pokémon
                    target_idx = 0
                new_active = bench.pop(target_idx)
                self.state.active_pokemon[owner_idx] = new_active
                print(f"{player.name} promoted {new_active.card.name} to Active!")
                if self.board_view:
                    self.board_view.render(self.state)
            else:
                # No Pokémon left to promote: player loses
                print(f"{player.name} has no Pokémon left! {opponent.name} wins!")
                self.state.scores[opponent_idx] = 3  # Force win

    def setup_game(self):
        """Perform initial game setup."""
        # Shuffle decks
        for player in self.state.players:
            random.shuffle(player.deck)
        # Initialize next_energy for both players if Deck objects are available
        if hasattr(self, '_player_decks') and len(self._player_decks) == 2:
            for idx, deck in enumerate(self._player_decks):
                self.state.initialize_player_energy(idx, deck.energy_types)
        # Initial draw
        self._perform_initial_draw()
        # Initial board setup: place Active and Benched Pokémon
        self._setup_initial_board()
        # Coin flip for first player
        self.state.current_player_idx = random.randint(0, 1)
        if self.manual:
            self._display_game_board()

    def _perform_initial_draw(self):
        """Handle initial 5-card draw with basic Pokemon guarantee."""
        for idx, player in enumerate(self.state.players):
            # Draw until we have a basic Pokemon
            while True:
                random.shuffle(player.deck)
                for _ in range(5):
                    player.draw_card()
                self.state.sync_hands_with_players()  # Sync after drawing
                if player.has_basic_pokemon():
                    break
                # If no basic Pokemon, shuffle back and redraw
                player.deck.extend(player.hand)
                player.hand.clear()
            self.state.sync_hands_with_players()  # Final sync after setup

    def _setup_initial_board(self):
        """Prompt each player to select Active and Benched Pokémon from their hand using menu and one-touch input."""
        import readchar
        for idx, player in enumerate(self.state.players):
            if self.manual and self.board_view:
                self.board_view.render(self.state)
            print(f"\n{player.name}, set up your board:")
            # List all Basic Pokémon in hand (filter only Pokemon cards)
            basic_indices = [i for i, card in enumerate(player.hand) if isinstance(card, Pokemon) and card.evolution_type == 'Basic']
            if not basic_indices:
                raise Exception(f"{player.name} has no Basic Pokémon in hand after initial draw!")
            # --- Select Active Pokémon ---
            if self.manual:
                while True:
                    if self.board_view:
                        self.board_view.render(self.state)
                    print("Choose your Active Pokémon:")
                    # Only show Pokemon cards as options, grouped in one line
                    options = []
                    option_strs = []
                    for i, hand_idx in enumerate(basic_indices):
                        poke = player.hand[hand_idx]
                        options.append({
                            'key': str(i+1),
                            'dispkey': str(i+1),
                            'desc': f"{poke.name} (HP: {poke.hp}, Element: {poke.element_type.name})",
                            'group': 'active',
                            'hand_idx': hand_idx
                        })
                        option_strs.append(f"[{i+1}] {poke.name}")
                    print(" ".join(option_strs))
                    print("Select a Pokémon by pressing its number...")
                    key = readchar.readkey()
                    if key.isdigit() and 1 <= int(key) <= len(basic_indices):
                        choice = int(key) - 1
                        active_idx = basic_indices[choice]
                        break
                    else:
                        print("Invalid key. Try again.")
            else:
                # Auto: pick first Basic Pokémon
                active_idx = basic_indices[0]
            # Move selected Pokémon to Active slot
            active_pokemon = player.hand.pop(active_idx)
            self.state.set_active_pokemon(idx, active_pokemon)
            self.state.sync_hands_with_players()

            # Remove from basic_indices and adjust indices
            basic_indices = [i for i in basic_indices if i != active_idx]
            basic_indices = [i-1 if i > active_idx else i for i in basic_indices]
            # --- Select Benched Pokémon, one at a time ---
            bench_choices = []
            if self.manual and basic_indices:
                while len(bench_choices) < 3 and basic_indices:
                    if self.board_view:
                        self.board_view.render(self.state)
                    print("Choose a Benched Pokémon (press Enter to skip):")
                    # Only show Pokemon cards as options, grouped in one line
                    options = []
                    option_strs = []
                    for i, hand_idx in enumerate(basic_indices):
                        poke = player.hand[hand_idx]
                        options.append({
                            'key': str(i+1),
                            'dispkey': str(i+1),
                            'desc': f"{poke.name} (HP: {poke.hp}, Element: {poke.element_type.name})",
                            'group': 'bench',
                            'hand_idx': hand_idx
                        })
                        option_strs.append(f"[{i+1}] {poke.name}")
                    print(" ".join(option_strs))
                    print("Press a number to add to Bench, or Enter to finish.")
                    key = readchar.readkey()
                    if key == '\r' or key == '\n':
                        break
                    if key.isdigit() and 1 <= int(key) <= len(basic_indices):
                        choice = int(key) - 1
                        bench_idx = basic_indices[choice]
                        bench_poke = player.hand.pop(bench_idx)
                        self.state.add_benched_pokemon(idx, bench_poke)
                        self.state.sync_hands_with_players()

                        # Remove from basic_indices and adjust indices
                        basic_indices = [i for i in basic_indices if i != bench_idx]
                        basic_indices = [i-1 if i > bench_idx else i for i in basic_indices]
                        # Re-render after each bench placement
                        if self.board_view:
                            self.board_view.render(self.state)
                    else:
                        print("Invalid key. Try again.")
            else:
                # Auto: pick up to 3 more Basic Pokémon
                for bench_idx in basic_indices[:3]:
                    bench_poke = player.hand.pop(bench_idx)
                    self.state.add_benched_pokemon(idx, bench_poke)
            if self.manual:
                print(f"{player.name} setup complete.\n")
        self.state.turn_number += 1

    def run(self):
        """Main game loop with clear turn phases: start, main, end."""
        self.setup_game()
        while True:
            self._start_turn_phase()
            if self.check_win(): return self.check_win()
            self._handle_main_phase()
            if self.check_win(): return self.check_win()
            self._end_turn_phase()
            if self.check_win(): return self.check_win()

    def check_win(self):
        # Check for win by points
        winner = self.state.check_win_condition()
        if winner is not None:
            print(f"Player {winner} wins the game!")
            return winner
        # Check for win by running out of Pokémon (active + bench)
        
        return None

    def _start_turn_phase(self):
        """Start of turn: update energy, draw card, and handle start-of-turn effects."""
        deck = self._player_decks[self.state.current_player_idx]
        if not hasattr(self, '_retreated_this_turn'):
            self._retreated_this_turn = {}
        self._retreated_this_turn.setdefault(self.state.current_player_idx, False)
        self._reset_retreated_flags()
        self._used_supporter_this_turn = False
        # Only draw a card if not the very first turn
        if self.state.turn_number > 1:
            self.state.draw_new_player_energy(self.state.current_player_idx, deck.energy_types)
            self.state.players[self.state.current_player_idx].draw_card()
            self.state.sync_hands_with_players()
        #else:
            # On the very first turn, promote next energy to energy zone and draw new next energy, but do not draw a card
            #self.state.draw_new_player_energy(self.state.current_player_idx, deck.energy_types)
        if self.manual:
            self._display_game_board()
        # Future: handle start-of-turn abilities, effects, etc.

    def _end_turn_phase(self):
        """End of turn: handle end-of-turn effects, status checks, and switch player."""
        self.state.end_turn()
        # Future: handle end-of-turn triggers, abilities, etc.
        if self.manual:
            self._display_game_board()

    def _display_game_board(self):
        if self.board_view:
            self.board_view.render(self.state)

    def _run_menu(self, options, prompt, allow_escape=True):
        """Reusable menu system for nested menus. Returns selected option or None if Esc."""
        import readchar
        from colorama import Fore, Style
        valid_keys = {opt['key']: opt for opt in options}
        while True:
            print(f"\n{prompt}")
            self._print_options_menu(options)
            key = readchar.readkey()
            if allow_escape and key == '\x1b':
                return None
            selected = valid_keys.get(key)
            if selected and selected.get('enabled', True):
                return selected
            elif selected and not selected.get('enabled', True):
                print(f"{Fore.LIGHTBLACK_EX}You cannot select this option now.{Style.RESET_ALL}")
            else:
                print("Invalid key. Try again.")

    def _assign_energy_menu(self, player_idx):
        """Handle assigning energy from energy zone to a Pokémon."""
        player = self.state.players[player_idx]
        energy_zone = self.state.energy_zones[player_idx]
        if not energy_zone:
            print("No energy available to assign.")
            return
        # Gather all Pokémon on board (active + benched)
        pokemons = []
        if self.state.active_pokemon[player_idx]:
            pokemons.append(('Active', self.state.active_pokemon[player_idx]))
        for i, poke in enumerate(self.state.benched_pokemon[player_idx]):
            pokemons.append((f"Bench {i+1}", poke))
        if len(pokemons) == 1:
            # Only one Pokémon, assign energy directly
            target = pokemons[0][1]
        else:
            # Build submenu
            options = []
            for i, (label, poke) in enumerate(pokemons):
                options.append({
                    'key': str(i+1),
                    'dispkey': str(i+1),
                    'desc': f"Assign to {label}: {poke.name} (HP: {poke.hp})",
                    'group': 'assign_target',
                    'poke': poke
                })
            options.append({'key': '\x1b', 'dispkey': 'esc', 'desc': 'Back', 'group': 'back'})
            selected = self._run_menu(options, "Select a Pokémon to assign energy to:")
            if not selected or selected.get('group') == 'back':
                return  # Cancelled
            target = selected['poke']
        # Assign energy (use the single energy, then clear the zone)
        energy = energy_zone
        if hasattr(target, 'attach_energy'):
            target.attach_energy(energy)
        elif hasattr(target, 'energy_attached'):
            target.energy_attached.append(energy)
        else:
            target.energy_attached = [energy]
        self.state.energy_zones[player_idx] = None
        print(f"Assigned {energy} to {target.name}.")
        self.state.sync_hands_with_players()
        if self.board_view:
            self.board_view.render(self.state)

    def _get_player_options(self, player_idx: int) -> list:
        """Generate a list of available actions for the current player as option dicts."""
        from colorama import Fore, Style
        player = self.state.players[player_idx]
        options = []
        # Example: view hand cards
        for i, card in enumerate(player.hand):
            # Always allow viewing
            options.append({
                'key': str(i+1),
                'dispkey': str(i+1),
                'desc': f"View hand card {i+1} in the active slot",
                'group': 'view_card',
                'card_idx': i
            })
            # Play card option (Enter key, only for selected card)
            is_basic_pokemon = hasattr(card, 'evolution_type') and getattr(card, 'evolution_type', None) == 'Basic'
            can_play = False
            reason = ''
            if is_basic_pokemon:
                # Can play if no active or bench has < 3
                state = self.state
                idx = player_idx
                if not state.active_pokemon[idx]:
                    can_play = True
                elif len(state.benched_pokemon[idx]) < 3:
                    can_play = True
                else:
                    reason = 'Bench full'
            # TODO: Add logic for other card types
            # Only add Enter key for the currently selected card
            if self.state.active_hand_card[player_idx] == i:
                options.append({
                    'key': '\r',
                    'dispkey': 'Enter',
                    'desc': f"Play card {i+1}" + (f" ({reason})" if not can_play and reason else ''),
                    'group': 'play_card',
                    'card_idx': i,
                    'enabled': can_play,
                    'target': None,  # For Pokémon, no target
                })
        # Add retreat option
        active_poke = self.state.active_pokemon[player_idx]
        bench = self.state.benched_pokemon[player_idx]
        can_retreat = False
        retreat_reason = ''
        # Only allow retreat if: active exists, at least 1 benched, enough energy, not paralyzed, and not already retreated this turn
        if active_poke and bench and len(bench) > 0:
            if hasattr(self, '_retreated_this_turn') and self._retreated_this_turn.get(player_idx, False):
                retreat_reason = 'Already retreated'
            elif not active_poke.can_retreat():
                retreat_reason = 'Not enough energy or paralyzed'
            else:
                can_retreat = True
        else:
            retreat_reason = 'No bench Pokémon'
        options.append({
            'key': 'r',
            'dispkey': 'R',
            'desc': 'Retreat Active Pokémon' + (f' ({retreat_reason})' if not can_retreat and retreat_reason else ''),
            'group': 'retreat',
            'enabled': can_retreat
        })
        # Add assign energy option
        has_energy = bool(self.state.energy_zones[player_idx])
        options.append({
            'key': 'e',
            'dispkey': 'E',
            'desc': 'Assign energy',
            'group': 'assign_energy',
            'enabled': has_energy
        })
        # Add attack option if active Pokémon has attacks
        active_poke = self.state.active_pokemon[player_idx]
        if active_poke and hasattr(active_poke.card, 'attacks'):
            for i, attack in enumerate(active_poke.card.attacks):
                can_attack = active_poke.can_perform_attack(attack)
                desc = f"Attack: {attack['name']} {[e.name for e in attack.get('cost', [])]} {attack['damage']}{f' - {attack['effect']}' if attack.get('effect') else ''}"
                options.append({
                    'key': string.ascii_lowercase[i],
                    'dispkey': string.ascii_uppercase[i],
                    'desc': desc,
                    'group': 'attack',
                    'attack_idx': i,
                    'enabled': can_attack
                })
        # End turn option (use '\x1b' for ESC key)
        options.append({'key': '\x1b', 'dispkey':'esc', 'desc': 'End turn', 'group': 'end_turn'})
        return options

    def _print_options_menu(self, options):
        from colorama import Fore, Style
        from collections import defaultdict
        print("\n" + "-" * 40)
        print(f"{Fore.CYAN}Available Actions:{Style.RESET_ALL}")
        grouped = defaultdict(list)
        for opt in options:
            grouped[opt.get('group', 'other')].append(opt)
        for group, opts in grouped.items():
            if group == 'view_card' and len(opts) > 1:
                keys = [opt['key'] for opt in opts]
                try:
                    key_nums = sorted(int(k) for k in keys)
                    if key_nums == list(range(key_nums[0], key_nums[-1]+1)):
                        key_str = f"[{key_nums[0]}-{key_nums[-1]}]"
                    else:
                        key_str = f"[{', '.join(keys)}]"
                except Exception:
                    key_str = f"[{', '.join(keys)}]"
                print(f"  {key_str} View Card X in the active slot")
            else:
                for opt in opts:
                    key = opt.get('dispkey', '?')
                    desc = opt.get('desc', '')
                    enabled = opt.get('enabled', True)
                    if not enabled:
                        print(f"  [{key}] {Fore.LIGHTBLACK_EX}{desc}{Style.RESET_ALL}")
                    else:
                        print(f"  [{key}] {desc}")
        print("-" * 40)
        print()  # Add a blank line for input cursor separation
        print("Press a key to select an action...")

    def _handle_main_phase(self):
        """Handle player actions during main phase."""
        if self.manual:
            import readchar
           
            player = self.state.players[self.state.current_player_idx]
            while True:
                # Always get fresh options for every keypress to reflect latest state
                options = self._get_player_options(self.state.current_player_idx)
                self.board_view.render(self.state)
                self._print_options_menu(options)
                valid_keys = {opt['key']: opt for opt in options}
                key = readchar.readkey()
                if key.isdigit() and int(key) > 0 and int(key) <= len(player.hand):
                    idx = int(key) - 1
                    selected = next((opt for opt in options if opt.get('group') == 'view_card' and opt.get('card_idx') == idx), None)
                else:
                    selected = valid_keys.get(key)
                if selected:
                    if selected['group'] == 'view_card':
                        self.state.active_hand_card[self.state.current_player_idx] = selected['card_idx']
                        print(f"Viewing card {selected['card_idx']+1}")
                        continue
                    elif selected['group'] == 'play_card':
                        if not selected.get('enabled', True):
                            print("You cannot play this card now.")
                            continue
                        card_idx = selected['card_idx']
                        card = player.hand[card_idx]
                        # Only handle Basic Pokémon for now
                        if hasattr(card, 'evolution_type') and getattr(card, 'evolution_type', None) == 'Basic':
                            played = card.play(self.state, self.state.turn_number)
                            if played:
                                print(f"Played {card.name} to the field.")
                                player.hand.pop(card_idx)
                                self.state.sync_hands_with_players()
                                continue
                            else:
                                print("Could not play this Pokémon (bench full or other rule).")
                                continue
                        # TODO: Add logic for other card types
                    elif selected['group'] == 'assign_energy':
                        if not selected.get('enabled', True):
                            print("No energy available to assign.")
                            continue
                        self._assign_energy_menu(self.state.current_player_idx)
                        continue
                    elif selected['group'] == 'retreat':
                        if not selected.get('enabled', True):
                            print("You cannot retreat now.")
                            continue
                        self._retreat_menu(self.state.current_player_idx)
                        continue
                    elif selected['group'] == 'attack':
                        if not selected.get('enabled', True):
                            print("You cannot perform this attack now.")
                            continue
                        attack_idx = selected['attack_idx']
                        active_poke = self.state.active_pokemon[self.state.current_player_idx]
                        attack = active_poke.card.attacks[attack_idx]
                        # Re-validate attack before performing
                        if not active_poke.can_perform_attack(attack):
                            print("You do not have the required energy or status to perform this attack.")
                            continue
                        # Perform the attack (damage calculation, energy cost, etc.)
                        self._perform_attack(self.state.current_player_idx, attack_idx)
                        break  # Attack ends the turn
                    elif selected['group'] == 'end_turn':
                        print("Ending turn...")
                        break
                else:
                    print("Invalid key. Try again.")
        else:
            print("Simulating player actions...")
            # Placeholder for AI decision-making logic

    def _retreat_menu(self, player_idx):
        """Handle retreating the active Pokémon."""
        player = self.state.players[player_idx]
        active_poke = self.state.active_pokemon[player_idx]
        bench = self.state.benched_pokemon[player_idx]
        if not active_poke or not bench:
            print("No Pokémon to retreat to.")
            return
        # If only one benched Pokémon, auto-switch
        if len(bench) == 1:
            target_idx = 0
        else:
            # Build submenu for bench selection
            options = []
            for i, poke in enumerate(bench):
                options.append({
                    'key': str(i+1),
                    'dispkey': str(i+1),
                    'desc': f"Switch in: {poke.name} (HP: {poke.hp})",
                    'group': 'bench_target',
                    'bench_idx': i
                })
            options.append({'key': '\x1b', 'dispkey': 'esc', 'desc': 'Cancel', 'group': 'cancel'})
            selected = self._run_menu(options, "Select a Pokémon to switch in:")
            if not selected or selected.get('group') == 'cancel':
                print("Retreat cancelled.")
                return
            target_idx = selected['bench_idx']
        # Pay retreat cost (discard attached energies, any type)
        cost = active_poke.retreat_cost
        for _ in range(cost):
            # Remove from any energy type with >0
            for e_type, count in active_poke.attached_energies.items():
                if count > 0:
                    active_poke.attached_energies[e_type] -= 1
                    player.discard_energy(e_type)
                    break
        # Remove all status conditions
        active_poke.clear_status()
        # Switch active and selected bench Pokémon
        new_active = bench.pop(target_idx)
        self.state.active_pokemon[player_idx], new_active.turn_played = new_active, self.state.turn_number
        bench.append(active_poke)
        print(f"{player.name} retreated to {new_active.name}!")
        self._retreated_this_turn[self.state.current_player_idx] = True
        self.board_view.render(self.state)

    def _reset_retreated_flags(self):
        """Reset retreat flags at the start of each turn."""
        self._retreated_this_turn = {0: False, 1: False}

    def _perform_attack(self, player_idx: int, attack_idx: int):
        """Perform the selected attack, handling targeting, damage, and effects. Ends turn after attack."""
        state = self.state
        attacker = state.active_pokemon[player_idx]
        attack = attacker.card.attacks[attack_idx]
        opponent_idx = 1 - player_idx
        targets = []
        # Determine targets based on attack['target']
        if attack['target'] == 'opponent_active':
            if state.active_pokemon[opponent_idx]:
                targets = [state.active_pokemon[opponent_idx]]
        elif attack['target'] == 'opponent_bench':
            if state.benched_pokemon[opponent_idx]:
                import random
                targets = [random.choice(state.benched_pokemon[opponent_idx])]
        elif attack['target'] == 'random_opponent':
            all_targets = [p for p in ([state.active_pokemon[opponent_idx]] if state.active_pokemon[opponent_idx] else []) + state.benched_pokemon[opponent_idx]]
            if all_targets:
                import random
                targets = [random.choice(all_targets)]
        elif attack['target'] == 'multi_random':
            all_targets = [p for p in ([state.active_pokemon[opponent_idx]] if state.active_pokemon[opponent_idx] else []) + state.benched_pokemon[opponent_idx]]
            import random
            n = min(2, len(all_targets))  # Example: hit 2 at random
            targets = random.sample(all_targets, n) if all_targets else []
        else:
            # Default: opponent's active
            if state.active_pokemon[opponent_idx]:
                targets = [state.active_pokemon[opponent_idx]]
        # Calculate base damage
        try:
            base_damage = int(attack.get('damage', 0))
        except ValueError:
            base_damage = 0
        # Apply modifiers (elemental weakness, tools, etc.)
        attack_results = []
        for target in targets:
            damage = base_damage
            # Elemental weakness (+20 if target is weak to attacker's type)
            if hasattr(target.card, 'weakness') and target.card.weakness:
                if str(attacker.card.element_type.value).lower() == str(target.card.weakness).lower():
                    damage += 20
            # TODO: Add logic for tools, abilities, trainers, etc.
            # (Leave hooks for future expansion)
            print(f"{attacker.card.name} uses {attack['name']}! {target.card.name} took {damage} damage.")
            time.sleep(3)
            state.apply_damage(target, damage, owner_idx=opponent_idx)
            
        # Refresh board view after attack
        if self.board_view:
            self.board_view.render(self.state)
        # Print attack results
        for line in attack_results:
            print(line)
        input("\nPress Enter to continue...")

import json
import os

CARDLIST_PATH = os.path.join("resources", "CardList.json")
OUTPUT_PATH = "resources/pokemon_with_abilities.json"  # Change this to your desired output filename
OUTPUT_FIELDS = 'ALL'  # Set to 'ALL' or a list of field names, e.g. ['name', 'type', 'hp']

####
#['name',]
def card_filter(card):
    # --- EDIT THIS FUNCTION TO CHANGE YOUR FILTER ---
    # Example: return True for all cards with an ability
    # return bool(card.get("ability"))
    # Example: return True for all cards whose type is 'grass'
    # return card.get("type", "").lower() == "grass"
    # Example: filter by HP greater than 100
    # return int(card.get("hp", 0)) > 100
    # --- YOUR CUSTOM FILTER BELOW ---
    return "Pokémon" in card.get("card_type", "N/A") and not card.get("ability",{}).get("name", "No ability") == "No ability"   # <--- Change this line as needed

def remove_duplicate_dictionaries(list_of_dicts):
    """
    Removes duplicate dictionaries from a list of dictionaries.

    Args:
        list_of_dicts: A list of dictionaries.

    Returns:
        A new list containing only the unique dictionaries from the input list,
        maintaining the original order of the first occurrence.
    """
    seen = set()
    unique_dicts = []
    for d in list_of_dicts:
        # Convert dictionary items to a frozenset for hashability
        # Ensure consistent order by sorting items before creating frozenset
        hashable_dict = frozenset(sorted(d.items()))
        if hashable_dict not in seen:
            seen.add(hashable_dict)
            unique_dicts.append(d)
    return unique_dicts

def main():
    with open(CARDLIST_PATH, "r", encoding="utf-8") as f:
        cards = json.load(f)
    filtered = [card for card in cards if card_filter(card)]
    if OUTPUT_FIELDS == 'ALL':
        output_cards = filtered
    else:
        output_cards = [{field: card.get(field) for field in OUTPUT_FIELDS} for card in filtered]

    #output_cards = remove_duplicate_dictionaries(output_cards)  # Remove duplicates
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output_cards, f, indent=2, ensure_ascii=False)
    print(f"Filtered {len(filtered)} cards. Output written to {OUTPUT_PATH}.")

if __name__ == "__main__":
    main()

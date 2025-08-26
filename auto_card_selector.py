import random

def auto_select_cards(cards, history):
    from itertools import combinations

    current_hand_indices = list(range(1, 9))  # indices 1 to 8
    recent_hand = history[-1] if history else set()

    all_combos = list(combinations(current_hand_indices, 5))
    valid_combos = [set(c) for c in all_combos if set(c) != recent_hand]

    if not valid_combos:
        return list(random.choice(all_combos))  # fallback: repeat if necessary

    return sorted(random.choice(valid_combos))


#Test run
'''
if __name__ == "__main__":
    test_cards = ["AS", "KS", "QS", "JS", "10S", "9S", "8S", "7S"]
    history = [[1, 2, 3, 5, 7]]

    new_selection = auto_select_cards(test_cards, history)
    print("Auto-selected card indices:", new_selection)
'''
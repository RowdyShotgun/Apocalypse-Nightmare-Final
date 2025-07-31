"""
main.py

Entry point for the text adventure game.
- Greets the player and prompts for their name.
- Sets up the initial game state and starts the main menu loop.
- Handles game restart logic.
"""
# main.py
# Import game_state to set initial values if needed, and print_slow for intro
from game_data import game_state
from utils import print_slow
from game_actions import handle_vision_event
from menus import main_menu_loop



def game():
    from utils import print_slow_colored, colorize_name, create_box

    # Create welcome box
    welcome_box = create_box("APOCALYPSE NIGHTMARE")
    print(welcome_box)
    
    print_slow_colored("Welcome to Apocalypse Nightmare!", "highlight", mode='slow')
    print_slow_colored("Press Enter to begin...", "info", mode='slow')
    input()
    
    # Add dramatic loading effect
    from utils import dramatic_pause
    print_slow_colored("Loading your apocalyptic journey", "info", mode='slow')
    dramatic_pause(1.5)
    # Prompt for protagonist name
    print_slow_colored("What is your name? (Press Enter for default)", "info")
    from utils import safe_input
    name = safe_input("> ")
    if not name:
        name = "You"
    game_state["protagonist_name"] = name
    print_slow_colored(f"Your name is set to: {colorize_name(name)}", "character")

    # The handle_vision_event function will set the starting location in game_state
    handle_vision_event()

    # Start the main game loop, which handles all menus and choices
    result = main_menu_loop()
    if result == 'restart':
        # Reset game_state to initial values
        from game_data import game_state as gs_template
        for k in list(game_state.keys()):
            del game_state[k]
        for k, v in gs_template.items():
            game_state[k] = v if not isinstance(v, (dict, list, set)) else v.copy()
        print_slow("Restarting the game...\n")
        game()
    # If result == 'exit', just return and let program end

if __name__ == "__main__":
    game()
    
"""
menus.py

Handles all user interaction, menu navigation, and the main game loop for the text adventure game.
- Displays menus and options based on game state.
- Dispatches user choices to game_actions functions.
- Contains the main_menu_loop and all menu handler functions.
"""
import sys
from game_data import game_state, INVENTORY_ITEMS, TRUST_THRESHOLDS, TIME_PHASES
from utils import print_slow, print_colored
from game_actions import (
    advance_time, display_location,
    handle_vision_event,
    handle_talk_parents_action, handle_talk_alex_action, handle_talk_maya_action,
    handle_talk_ben_action, handle_talk_jake_action,
    handle_town_hall_interaction_action, handle_computer_use_action, handle_shout_warning,
    handle_gather_supplies_action,
    handle_involve_friends_escape_action, handle_general_store_interaction_action,
    handle_steal_general_store_action,
    handle_burger_hut_work_action, handle_go_to_class_action,
    handle_bunker_access_action, handle_military_base_approach_action,
    handle_military_base_action, handle_laser_activation, handle_escape_base_attempt,
    display_inventory, handle_allies_escape_ending, handle_solo_escape_ending,
    handle_town_evacuated_ending, handle_missile_destroyed_ending,
    handle_time_up_ending, handle_jailed_ending, buy_tech_parts_action,
    handle_steal_school_action, handle_steal_tech_store_action, handle_jake_favor_action,
    build_jake_trust_opportunity, handle_truck_escape_ending, handle_truck_travel_action,
    handle_pawn_shop_sell_action, handle_local_bus_travel, handle_search_for_car_action
)
from colorama import Fore

# --- Helper Functions for Menus ---
def display_menu(options):
    """Displays a numbered list of options and returns the chosen action function
    or a special value/tuple if sub-choices need to be passed."""
    
    while True: # Loop until valid input
        for idx, (desc, _) in enumerate(options, 1):
            # Determine color based on option type
            if any(utility in desc.lower() for utility in ["show inventory", "show status", "help", "quit", "go back"]):
                print_colored(f"{idx}. {desc}", "warning")  # Utility options in warning color
            else:
                print_colored(f"{idx}. {desc}", "info")     # Navigation/action options in info color
        
        try:
            choice_str = input("\nEnter your choice: ").strip()
            if choice_str.isdigit() and 1 <= int(choice_str) <= len(options):
                return options[int(choice_str) - 1][1] # Return the function/lambda directly
            else:
                print_colored("❌ Invalid choice. Please enter the number corresponding to your action.", "warning")
                print_colored(f"💡 Tip: Type a number between 1 and {len(options)}", "info")
                # Re-display location information after invalid input
                from game_actions import display_location
                display_location()
        except KeyboardInterrupt:
            print_colored("\nMenu interrupted. Exiting game.", "warning")
            sys.exit(0)

def show_time_status():
    """Displays the current game time and phase."""
    from utils import create_countdown_box
    print(create_countdown_box(game_state['time_remaining'], game_state['current_day_phase']))
    print("-" * 30) # Separator for clarity

def set_location(loc):
    """Changes the player's current location."""
    game_state["current_location"] = loc
    # No return to main_menu_loop here; it will naturally loop and call the next menu for the new location.

def exit_game():
    """Handles quitting the game."""
    print_slow("Are you sure you want to quit? (yes/no)")
    confirm = input("> ").strip().lower()
    if confirm == "yes":
        print_slow("Thanks for playing!")
        sys.exit(0)
    else:
        print_slow("Returning to the game.")

def display_status():
    """Displays comprehensive player status."""
    from utils import colorize_money, colorize_name, print_colored, create_box
    
    # Create status header box
    status_box = create_box("📊 PLAYER STATUS")
    print(status_box)
    
    # Resources & Stats
    print_colored("🎯 RESOURCES & STATS", "highlight")
    print_colored(f"🧠 Knowledge: {game_state['knowledge']} (Research & Learning)", "highlight")
    print_colored(f"🔧 Tech Parts: {game_state['tech_parts']} (Electronic Components)", "item")
    cash_amount = f"{game_state['cash']} unit(s)"
    print_colored(f"💰 Cash: {colorize_money(cash_amount)} (Currency)", "money")
    print_colored(f"🏛️ Authority: {game_state['authority_of_town']} (Town Influence)", "info")
    
    # Key Items & Access
    print_colored("\n🔑 KEY ITEMS & ACCESS", "highlight")
    print_colored(f"🎒 Has Backpack: {'Yes' if INVENTORY_ITEMS['BACKPACK'] in game_state['inventory'] else 'No'}", "inventory")
    print_colored(f"🔑 Has Car Keys: {'Yes' if game_state['has_car_keys'] else 'No'}", "item")
    print_colored(f"⛽ Car Gas: {game_state['car_gas']}% (Truck Fuel)", "info")
    print_colored(f"🏰 Bunker Unlocked: {'Yes' if game_state['bunker_unlocked'] else 'No'}", "success")
    
    # Friend relationships section
    print_colored("\n👥 FRIEND RELATIONSHIPS", "highlight")
    print_colored(f"- {colorize_name('Alex')} (Skeptic): {game_state['trust_alex']} / 10", "character")
    print_colored(f"- {colorize_name('Maya')} (Optimist): {game_state['trust_maya']} / 10", "character")
    print_colored(f"- {colorize_name('Ben')} (Pragmatist): {game_state['trust_ben']} / 10", "character")
    print_colored(f"- {colorize_name('Jake')} (Bully): {game_state['trust_jake']} / 10", "character")
    
    # Show ending progress hints
    print_colored("\n🎯 ENDING PROGRESS", "highlight")
    
    # Missile Destroyed ending requirements
    if game_state["knowledge"] >= 7 and game_state["tech_parts"] >= 2:
        print_colored("Ready for Missile Destroyed ending!", "success")
    else:
        missing = []
        if game_state["knowledge"] < 7:
            missing.append(f"Knowledge ({game_state['knowledge']}/7)")
        if game_state["tech_parts"] < 2:
            missing.append(f"Tech Parts ({game_state['tech_parts']}/2)")
        print_colored(f"❌ Missile Destroyed: Need {', '.join(missing)}", "warning")
    
    # Allies Escape ending requirements
    if (game_state.get("has_shared_vision_with_friends", False) and
        game_state["trust_alex"] >= 4 and game_state["trust_maya"] >= 5 and game_state["trust_ben"] >= 4):  # Back to requiring effort
        print_colored("✅ Ready for Allies Escape ending!", "success")
    else:
        missing = []
        if not game_state.get("has_shared_vision_with_friends", False):
            missing.append("Share vision with friends")
        if game_state["trust_alex"] < 4:  # Back to requiring effort
            missing.append(f"Alex trust ({game_state['trust_alex']}/4)")
        if game_state["trust_maya"] < 5:  # Back to requiring effort
            missing.append(f"Maya trust ({game_state['trust_maya']}/5)")
        if game_state["trust_ben"] < 4:  # Back to requiring effort
            missing.append(f"Ben trust ({game_state['trust_ben']}/4)")
        print_colored(f"❌ Allies Escape: Need {', '.join(missing)}", "warning")
    
    # Truck Escape ending requirements
    if ("truck_keys" in game_state["inventory"] and game_state["car_gas"] >= 30):
        print_colored("✅ Ready for Truck Escape ending!", "success")
    else:
        missing = []
        if "truck_keys" not in game_state["inventory"]:
            missing.append("Truck keys")
        if game_state["car_gas"] < 30:
            missing.append(f"Gas ({game_state['car_gas']}%/30%)")
        print_colored(f"❌ Truck Escape: Need {', '.join(missing)}", "warning")
    
    print("-" * 50)
    
    # Show contextual hint
    from game_actions import get_contextual_hint
    hint = get_contextual_hint()
    print_colored(f"\n💡 HINT: {hint}", "info")
    
    input("Press Enter to continue...")


# --- Location-Specific Menu Handlers ---
# Each handler displays its menu and dispatches to game_actions.py functions.

def handle_home_menu():
    options = [
        ("Go to town", lambda: set_location("town_square")),
        ("Go to school entrance", lambda: set_location("school_entrance")),
        ("Use computer", handle_computer_use_menu),
        ("Talk to parents", handle_talk_parents_menu),
        ("Show inventory", display_inventory),
        ("Show status", display_status),
        ("Quit", exit_game),
    ]
    action = display_menu(options)
    action()

def handle_town_square_menu():
    # Check for game-ending conditions based on accumulated state in Town Square
    if game_state["mayor_warned"] and game_state["mob_of_civilians"] and game_state["time_remaining"] > 0:
        game_state["ending_achieved"] = "Town Evacuated"
        return
    options = [
        ("Warn people openly", lambda: handle_shout_warning()),
        ("Work at Burger Hut", lambda: set_location("burger_hut")),
        ("Go home", lambda: set_location("home")),
        ("Go to school entrance", lambda: set_location("school_entrance")),
        ("Go to bus stop", lambda: set_location("bus_stop")),
        ("Go to town hall", lambda: set_location("town_hall")),
        ("Go to tech store", lambda: set_location("tech_store")),
        ("Go to military base", lambda: set_location("military_base")),
        ("Go to general store", lambda: set_location("general_store")),
        ("Go to pawn shop", lambda: set_location("pawn_shop")),
        ("Show inventory", display_inventory),
        ("Show status", display_status),
        ("Quit", exit_game),
    ]
    
    # Add truck travel options if available
    options = add_truck_travel_options(options, "town_square")
    
    action = display_menu(options)
    action()

def handle_school_entrance_menu():
    # Check for Jake trust building opportunity
    from game_actions import build_jake_trust_opportunity
    build_jake_trust_opportunity()
    
    options = [
        ("Go to class", lambda: handle_go_to_class_action()),
        ("Steal from school", lambda: handle_steal_school_action()),
        ("Go to newspaper club", lambda: set_location("newspaper_club")),
        ("Go home", lambda: set_location("home")),
        ("Go to town square", lambda: set_location("town_square")),
        ("Show inventory", display_inventory),
        ("Show status", display_status),
        ("Quit", exit_game),
    ]
    
    # Add truck travel options if available
    options = add_truck_travel_options(options, "school_entrance")
    
    action = display_menu(options)
    action()

def handle_newspaper_club_menu():
    def handle_friends_submenu():
        while True:
            options = [
                ("Talk to Alex", lambda: handle_talk_alex_menu()),
                ("Talk to Maya", lambda: handle_talk_maya_menu()),
                ("Talk to Ben", lambda: handle_talk_ben_menu()),
            ]
            # Show Jake if you have any trust with him or if he owes a favor
            if game_state["trust_jake"] > 0 or game_state.get("jake_owed_favor", False):
                options.append(("Talk to Jake", lambda: handle_talk_jake_menu()))
            # Use a lambda that returns a sentinel value for Go back
            options.append(("Go back", lambda: "__BACK__"))
            action = display_menu(options)
            result = action()
            if result == "__BACK__":
                break
    options = [
        ("Talk to friends", handle_friends_submenu),
        ("Go to school entrance", lambda: set_location("school_entrance")),
        ("Show inventory", display_inventory),
        ("Show status", display_status),
        ("Quit", exit_game),
    ]
    action = display_menu(options)
    action()

def handle_general_store_menu():
    # display_location() already called in main_menu_loop
    options = [
        ("Interact with Mr. Jenkins / Supplies",
         lambda: handle_general_store_interaction_menu()),
        # Sub-menu for store actions
        ("Go to town square", lambda: set_location("town_square")),
        ("Show inventory", display_inventory),
        ("Show status", display_status),
        ("Quit", exit_game),
    ]
    
    # Add truck travel options if available
    options = add_truck_travel_options(options, "general_store")
    
    action = display_menu(options)
    action()

def handle_town_hall_menu():
    # display_location() already called in main_menu_loop
    options = [
        ("Talk to secretary", lambda: handle_town_hall_interaction_menu()), # Sub-menu for secretary
        ("Go to town square", lambda: set_location("town_square")),
        ("Show inventory", display_inventory),
        ("Show status", display_status),
        ("Quit", exit_game),
    ]
    action = display_menu(options)
    if action: action()

def handle_bus_stop_menu():
    bus_ticket_cost = 1 # CHANGED: Bus ticket cost is 1 cash unit
    def buy_out_of_state_ticket():
        if game_state["cash"] >= bus_ticket_cost and game_state["time_remaining"] > 0:
            if (game_state.get("has_shared_vision_with_friends", False) and
                game_state["trust_alex"] >= 4 and game_state["trust_maya"] >= 4 and game_state["trust_ben"] >= 4):
                game_state["cash"] -= bus_ticket_cost # Deduct cash for allies escape
                game_state["ending_achieved"] = "Allies Escape"
                return
            else:
                game_state["cash"] -= bus_ticket_cost # Deduct cash for solo escape
                game_state["ending_achieved"] = "Solo Escape"
                return
        else:
            print_slow("You don't have enough cash for a bus ticket, or there's no time left.")
            return
    options = [
        ("Travel to outskirts using local bus pass", lambda: handle_local_bus_travel()),
        (f"Buy ticket to out of state (Requires {bus_ticket_cost} Cash unit(s))", buy_out_of_state_ticket),
        ("Go to town square", lambda: set_location("town_square")),
        ("Show inventory", display_inventory),
        ("Show status", display_status),
        ("Quit", exit_game),
    ]
    action = display_menu(options)
    action()

def handle_tech_store_menu():
    options = [
        ("Buy tech parts (1 Cash unit required)", buy_tech_parts_action),
        ("Steal from tech store", lambda: handle_steal_tech_store_action()),
        ("Go to town square", lambda: set_location("town_square")),
        ("Show inventory", display_inventory),
        ("Show status", display_status),
        ("Quit", exit_game),
    ]
    
    # Add truck travel options if available
    options = add_truck_travel_options(options, "tech_store")
    
    action = display_menu(options)
    action()

def handle_military_base_menu():
    # Check for immediate missile destroyed ending if conditions met and player is at base
    if (game_state["military_base_accessed"] and
        game_state["knowledge"] >= 7 and
        game_state["tech_parts"] >= 2 and
        game_state["time_remaining"] > 0):
        game_state["ending_achieved"] = "Missile Destroyed"
        return # Exit menu to trigger game end in main_menu_loop

    options = [
        ("Approach gate (Sneak/Authority)",
         lambda: handle_military_base_approach_menu()),
        # Sub-menu for approach options
        ("Go to town square", lambda: set_location("town_square")),
        ("Show inventory", display_inventory),
        ("Show status", display_status),
        ("Quit", exit_game),
    ]
    action = display_menu(options)
    action()


def handle_outskirts_road_menu():
    # Check for truck escape ending if player has truck keys and sufficient gas
    if ("truck_keys" in game_state["inventory"] and 
        game_state["car_gas"] >= 30 and 
        game_state["time_remaining"] > 0):
        from game_actions import handle_truck_escape_ending
        if handle_truck_escape_ending():
            return  # Exit menu to trigger game end in main_menu_loop
    
    options = [
        ("Search for car", lambda: handle_search_for_car_action()),
        ("Go to bus stop", lambda: set_location("bus_stop")),
    ]
    
    # Only show bunker option if player has discovered it
    if "bunker_rumor" in game_state["inventory"]:
        options.append(("Go to neighbor's bunker", lambda: set_location("neighbors_bunker")))
    
    options.extend([
        ("Show inventory", display_inventory),
        ("Show status", display_status),
        ("Quit", exit_game),
    ])
    
    # Add truck travel options if available
    options = add_truck_travel_options(options, "outskirts_road")
    
    action = display_menu(options)
    action()


def handle_neighbors_bunker_menu():
    # Check for escape ending from bunker
    if game_state["bunker_unlocked"] and game_state["inventory"].count("supplies") >= 3 and game_state["time_remaining"] > 0:
        if (game_state.get("has_shared_vision_with_friends", False) and
            game_state["trust_alex"] >= TRUST_THRESHOLDS["HIGH"] and 
            game_state["trust_maya"] >= TRUST_THRESHOLDS["HIGH"] and 
            game_state["trust_ben"] >= TRUST_THRESHOLDS["HIGH"]):
            game_state["ending_achieved"] = "Allies Escape"
        else:
            game_state["ending_achieved"] = "Solo Escape"
        return # Exit menu to trigger game end in main_menu_loop

    options = [
        ("Examine door", lambda: handle_bunker_access_action("examine door")),
        ("Knock on door", lambda: handle_bunker_access_action("knock")),
        ("Enter (if unlocked)", lambda: handle_bunker_access_action("enter")),
        ("Go to outskirts road", lambda: set_location("outskirts_road")),
        ("Show inventory", display_inventory),
        ("Show status", display_status),
        ("Quit", exit_game),
    ]
    action = display_menu(options)
    if action: action()


def handle_burger_hut_menu():
    options = [
        ("Work a shift", lambda: handle_burger_hut_work_action("yes")),
        # Pass 'yes' directly to action
        ("Go to town square", lambda: set_location("town_square")),
        ("Show inventory", display_inventory),
        ("Show status", display_status),
        ("Quit", exit_game),
    ]
    action = display_menu(options)
    if action: action()


def handle_pawn_shop_menu():
    # display_location() already called in main_menu_loop
    options = [
        ("Sell stolen items", lambda: handle_pawn_shop_sell_action()),
        ("Show inventory", display_inventory),
        ("Return to town square", lambda: set_location("town_square")),
    ]
    action = display_menu(options)
    action()


# --- Sub-Menus (interactions that have their own choices) ---

def handle_computer_use_menu():
    # Only re-loop if still in home (prevent infinite loop if loc changed)
    if game_state["current_location"] == "home": # Only re-loop if still in home (prevent infinite loop if loc changed)
        while True:
            options = [
                ("Search for nuclear threats", lambda: handle_computer_use_action(1)),
                ("Research missile defense", lambda: handle_computer_use_action(2)),
                ("Look up survival tips", lambda: handle_computer_use_action(3)),
                ("Go back", lambda: "__BACK__")
            ]
            action = display_menu(options)
            result = action()
            if result == "__BACK__":
                break
    else:
        print_slow("You need to be at home to use the computer.")





def handle_talk_parents_menu():
    # Only show initial dialogue options if not already warned
    if not game_state["parents_warned"]:
        print_slow("You consider telling them about your terrifying vision. It's a huge risk.")
        options = [
            ("Tell them about the nuclear missile vision", lambda: handle_talk_parents_action(1)),
            ("Keep silent and talk about something else", lambda: handle_talk_parents_action(2)),
        ]
    else: # If already warned, just a simple "go back" type option
        print_slow("Your parents are still going about their day. They sometimes glance at you with lingering worry.")
        print_slow("They haven't brought up your 'feverish' vision again.")
        options = [
            ("Talk about mundane things", lambda: handle_talk_parents_action(2)), # Re-use action for mundane talk
            ("Go back", lambda: None),
        ]
    action = display_menu(options)
    if action: action()


def handle_talk_alex_menu():
    # Pre-dialogue based on previous interaction status
    if not game_state.get("talked_to_alex_about_vision", False):
        print_slow("Alex glances up. 'What's up? Got a new scoop for the paper?'")
        options = [
            ("Tell him about the nuclear missile vision", lambda: handle_talk_alex_action(1)),
            ("Ask for his research help on a hypothetical disaster", lambda: handle_talk_alex_action(2)),
            ("Talk about newspaper club business", lambda: handle_talk_alex_action(3)),
        ]
    else:
        # Post-dialogue when vision has already been discussed
        if game_state["trust_alex"] >= 4:
            print_slow("Alex is still processing your warning. 'I'm checking the news, but nothing official yet. Still, I'm with you. What's our next move?'")
        elif game_state["trust_alex"] >= 2:
            print_slow("Alex seems a bit awkward. He quickly changes the subject, clearly unconvinced by your vision.")
        else:
            print_slow("Alex avoids eye contact and quickly finds an excuse to leave. He's clearly uncomfortable around you now.")
        options = [
            ("Go back", lambda: None),
        ]
    action = display_menu(options)
    if action: action()

def handle_talk_maya_menu():
    if not game_state.get("talked_to_maya_about_vision", False):
        print_slow("Maya smiles warmly. 'Hi! You look worried. Want to talk about it?'")
        options = [
            ("Confide in her about the vision", lambda: handle_talk_maya_action(1)),
            ("Talk about art or other light topics", lambda: handle_talk_maya_action(2)),
        ]
    else:
        if game_state["trust_maya"] >= 4:
            print_slow("Maya is anxious but supportive. 'I'm here for you, no matter what happens. We'll face this together.'")
        elif game_state["trust_maya"] >= 2:
            print_slow("Maya tries to offer comfort, but her voice is strained. She clearly thinks you're overwhelmed.")
        else:
            print_slow("Maya avoids eye contact and quickly finds an excuse to leave. She's clearly uncomfortable around you now.")
        options = [
            ("Go back", lambda: None),
        ]
    action = display_menu(options)
    if action: action()

def handle_talk_ben_menu():
    if not game_state.get("talked_to_ben_about_vision", False):
        print_slow("Ben glances up from his tinkering. 'Hey. Got a problem? Or something interesting for this old radio?'")
        options = [
            ("Tell him about the vision", lambda: handle_talk_ben_action(1)),
            ("Ask him for help with something practical (e.g., getting supplies)", lambda: handle_talk_ben_action(2)),
            ("Talk about his radio projects", lambda: handle_talk_ben_action(3)),
        ]
    else:
        if game_state["trust_ben"] >= 4:
            print_slow("Ben is focused on solutions. 'Okay, so what's the next practical step? We need a clear objective.'")
        elif game_state["trust_ben"] >= 2:
            print_slow("Ben gives you a sympathetic look but quickly shifts the conversation to something more concrete.")
        else:
            print_slow("Ben avoids eye contact and finds an excuse to fiddle with his radio, clearly uncomfortable with you.")
        options = [
            ("Go back", lambda: None),
        ]
    action = display_menu(options)
    if action: action()

def handle_talk_jake_menu():
    # Pre-dialogue based on previous interaction status or low trust
    if game_state["trust_jake"] < 3 and not game_state.get("talked_to_jake_about_vision", False):
        print_slow("Jake just glares at you. 'What do you want, loser?' He doesn't seem interested in talking.")
        options = [
            ("Go back", lambda: None),
        ]
    elif not game_state.get("talked_to_jake_about_vision", False):
        print_slow("Jake leans against the wall. 'What do you want, nerd?' There's a hint of boredom, not outright hostility.")
        options = [
            ("Tell him about the vision (carefully)", lambda: handle_talk_jake_action(1)),
            ("Ask for a favor (e.g., getting past someone, intimidating someone)", lambda: handle_talk_jake_action(2)),
            ("Challenge his authority (risky)", lambda: handle_talk_jake_action(3)),
            ("Show him respect or offer help", lambda: handle_talk_jake_action(4)),
            ("Stand up for him or defend him", lambda: handle_talk_jake_action(5)),
            ("Reminisce about old times", lambda: handle_talk_jake_action(6)),
        ]
        # Add favor option if Jake owes a favor
        if game_state.get("jake_owed_favor", False):
            options.append(("Ask Jake for a favor", lambda: handle_jake_favor_action()))
    else:
        # Post-dialogue when vision has already been discussed
        if game_state["trust_jake"] >= 5:
            print_slow("Jake looks agitated. 'Still nothing concrete? We need to do something, pronto!'")
        else:
            print_slow("Jake avoids eye contact, mumbling something about being busy. He doesn't want to talk about your 'crazy' vision.")
        options = [
            ("Go back", lambda: None),
        ]
        # Add favor option if Jake owes a favor
        if game_state.get("jake_owed_favor", False):
            options.append(("Ask Jake for a favor", lambda: handle_jake_favor_action()))
    action = display_menu(options)
    if action: action()


def handle_town_hall_interaction_menu():
    print_slow("You enter the Town Hall. The secretary looks up, unimpressed.")
    print_slow(f"Secretary Davies asks: 'Do you have an appointment?'")
    options = [
        ("Demand to see the Mayor and show proof", lambda: handle_town_hall_interaction_action(1)),
        ("Try to explain the urgency to the secretary", lambda: handle_town_hall_interaction_action(2)),
        ("Leave politely", lambda: handle_town_hall_interaction_action(3)),
    ]
    action = display_menu(options)
    if action: action()


def handle_general_store_interaction_menu():
    # Check if player is banned from the store
    if game_state.get("jenkins_banned", False):
        print_slow("You approach the General Store, but Mr. Jenkins spots you through the window.")
        print_slow("'Get lost, kid! You're not welcome here anymore!' he shouts, pointing to a 'BANNED' sign.")
        print_slow("You've been permanently banned from the General Store.")
        game_state["current_location"] = "town_square"
        return
    
    print_slow("You enter the General Store. Mr. Jenkins, the proprietor, is behind the counter.")
    options = [
        ("Try to buy supplies (e.g., food, gas)", lambda: handle_general_store_interaction_action(1)),
        ("Attempt to steal supplies", lambda: handle_steal_general_store_sub_menu()), # This leads to a sub-menu for stealing
        ("Talk to Mr. Jenkins about the situation", lambda: handle_general_store_interaction_action(3)),
        ("Help Mr. Jenkins with heavy boxes", lambda: handle_general_store_interaction_action(4)),
        ("Leave the store", lambda: handle_general_store_interaction_action(5)),
    ]
    action = display_menu(options)
    if action: action()


def handle_steal_general_store_sub_menu():
    print_slow("You eye a small gas can. Attempt to steal it?")
    while True:
        options = [
            ("Yes, try to steal.", lambda: handle_steal_general_store_action(1)),
            ("No, it's too risky.", lambda: "__BACK__"),
        ]
        action = display_menu(options)
        result = action()
        if result == "__BACK__":
            break





def handle_gather_supplies_menu():
    print_slow("You need supplies for survival or to fuel your escape.")
    while True:
        options = []
        
        # Check if player is banned from general store
        if game_state.get("jenkins_banned", False):
            options.append(("General Store (BANNED - cannot enter)", lambda: print_slow("You've been banned from the General Store.")))
        else:
            options.append(("Go to the General Store (buy or steal)", lambda: handle_gather_supplies_action(1)))
        
        options.extend([
            ("Go to Burger Hut (earn cash)", lambda: handle_gather_supplies_action(2)),
            ("Search for items at Home", lambda: handle_gather_supplies_action(3)),
            ("Go back", lambda: "__BACK__"),
        ])
        
        action = display_menu(options)
        result = action()
        if result == "__BACK__":
            break


def handle_involve_friends_escape_menu():
    print_slow("You consider involving your friends in your escape plan.")
    while True:
        options = [
            ("Go to the Newspaper Club (Talk to friends)", lambda: handle_involve_friends_escape_action(1)),
            ("Seek access to the Neighbor's Bunker (if you know about it)", lambda: handle_involve_friends_escape_action(2)),
            ("Go back", lambda: "__BACK__"),
        ]
        action = display_menu(options)
        result = action()
        if result == "__BACK__":
            break


def handle_bunker_access_menu():
    # display_location() already called in main_menu_loop
    options = [
        ("Examine door", lambda: handle_bunker_access_action("examine door")),
        ("Knock on door", lambda: handle_bunker_access_action("knock")),
        ("Enter (if unlocked)", lambda: handle_bunker_access_action("enter")),
        ("Go back", lambda: None), # Simple back to previous menu
    ]
    action = display_menu(options)
    if action: action()


def handle_military_base_approach_menu():
    """Handles the approach to the military base with multiple options."""
    print_slow("You stand before the **Military Base**, a formidable fortress. This is your chance to stop the missile.")
    while True:
        options = [
            ("Sneak past the guards (requires high knowledge and tech parts)", "sneak"),
            ("Bluff your way in (requires high authority)", "bluff"),
            ("Bribe the guard (requires 2 cash units)", "bribe"),
            ("Retreat to Town Square", "retreat"),
        ]
        action = display_menu(options)
        if action == "sneak":
            if game_state["knowledge"] >= 5 and game_state["tech_parts"] >= 2:
                print_slow("You expertly avoid the patrols, using your knowledge and tech skills to bypass security systems.")
                game_state["military_base_accessed"] = True
                game_state["current_location"] = "military_base"
                print_slow("You have successfully snuck into the base!")
                return
            else:
                print_slow("You try to sneak in, but lack the skills or equipment. A guard spots you and you are forced to retreat!")
                return
        elif action == "bluff":
            if game_state["authority_of_town"] >= 5:
                print_slow("You confidently approach the gate, flashing your credentials and leveraging your authority. The guard hesitates, then lets you in.")
                game_state["military_base_accessed"] = True
                game_state["current_location"] = "military_base"
                print_slow("You have successfully bluffed your way into the base!")
                return
            else:
                print_slow("You try to bluff your way in, but the guard is unconvinced. You are turned away.")
                return
        elif action == "bribe":
            if game_state["cash"] >= 2:
                print_slow("You discreetly offer the guard some cash. He glances around, pockets the money, and lets you in.")
                game_state["cash"] -= 2
                game_state["military_base_accessed"] = True
                game_state["current_location"] = "military_base"
                print_slow("You have successfully bribed your way into the base!")
                return
            else:
                print_slow("You don't have enough cash to bribe the guard. He scoffs and tells you to leave.")
                return
        elif action == "retreat":
            print_slow("You decide to retreat and return to the Town Square.")
            game_state["current_location"] = "town_square"
            return


def handle_military_base_actions_internal_menu():
    # This menu is displayed *after* successfully entering the military base
    print_slow("You're deep inside the military base. Your goal: the satellite laser control room.")
    print_slow("You know the missile launch is imminent. You need to act fast.")
    options = [
        ("Search for the Laser Control Room", lambda: handle_military_base_action(1)),
        ("Look for military personnel to convince", lambda: handle_military_base_action(2)),
        ("Attempt to use a computer terminal", lambda: handle_military_base_action(3)),
        ("Give up and try to escape the base", lambda: handle_military_base_action(4)),
    ]
    action = display_menu(options)
    if action: action()


def add_truck_travel_options(options, current_location):
    """Adds smart truck travel options to a menu if player has truck keys and gas."""
    if ("truck_keys" in game_state["inventory"] and game_state["car_gas"] >= 10):
        # Smart truck travel options based on current location and game state
        truck_options = []
        
        if current_location == "town_square":
            # Town Square is the hub - show key destinations
            truck_options = [
                ("🚗 Drive to School", lambda: handle_truck_travel_action("school_entrance")),
                ("🚗 Drive to General Store", lambda: handle_truck_travel_action("general_store")),
                ("🚗 Drive to Tech Store", lambda: handle_truck_travel_action("tech_store")),
                ("🚗 Drive to Bus Stop", lambda: handle_truck_travel_action("bus_stop")),
                ("🚗 Drive to Outskirts Road", lambda: handle_truck_travel_action("outskirts_road")),
            ]
                
        elif current_location == "school_entrance":
            # From school, prioritize getting back to town or supplies
            truck_options = [
                ("🚗 Drive to Town Square", lambda: handle_truck_travel_action("town_square")),
                ("🚗 Drive to General Store", lambda: handle_truck_travel_action("general_store")),
                ("🚗 Drive to Bus Stop", lambda: handle_truck_travel_action("bus_stop")),
                ("🚗 Drive to Outskirts Road", lambda: handle_truck_travel_action("outskirts_road")),
            ]
                
        elif current_location == "general_store":
            # From store, prioritize getting back to town or school
            truck_options = [
                ("🚗 Drive to Town Square", lambda: handle_truck_travel_action("town_square")),
                ("🚗 Drive to School", lambda: handle_truck_travel_action("school_entrance")),
                ("🚗 Drive to Bus Stop", lambda: handle_truck_travel_action("bus_stop")),
                ("🚗 Drive to Outskirts Road", lambda: handle_truck_travel_action("outskirts_road")),
            ]
            # Only show tech store if player needs tech parts
            if game_state["tech_parts"] < 2:
                truck_options.append(("🚗 Drive to Tech Store", lambda: handle_truck_travel_action("tech_store")))
                
        elif current_location == "tech_store":
            # From tech store, prioritize getting back to town
            truck_options = [
                ("🚗 Drive to Town Square", lambda: handle_truck_travel_action("town_square")),
                ("🚗 Drive to General Store", lambda: handle_truck_travel_action("general_store")),
                ("🚗 Drive to Bus Stop", lambda: handle_truck_travel_action("bus_stop")),
                ("🚗 Drive to Outskirts Road", lambda: handle_truck_travel_action("outskirts_road")),
            ]
            # Only show military base if player has high knowledge and tech parts
            if game_state["knowledge"] >= 5 and game_state["tech_parts"] >= 2:
                truck_options.append(("🚗 Drive to Military Base", lambda: handle_truck_travel_action("military_base")))
                
        elif current_location == "outskirts_road":
            # From outskirts, prioritize getting back to town or to bus stop
            truck_options = [
                ("🚗 Drive to Town Square", lambda: handle_truck_travel_action("town_square")),
                ("🚗 Drive to Bus Stop", lambda: handle_truck_travel_action("bus_stop")),
                ("🚗 Drive to General Store", lambda: handle_truck_travel_action("general_store")),
            ]
        else:
            # Default fallback - just get back to town
            truck_options = [
                ("🚗 Drive to Town Square", lambda: handle_truck_travel_action("town_square")),
            ]
        
        # Insert truck options after the first few regular options
        insert_index = min(3, len(options))
        for i, option in enumerate(truck_options):
            options.insert(insert_index + i, option)
    
    return options


# --- Main Menu Dispatcher ---
# This dictionary maps current_location to its corresponding menu handler function.
menu_handlers = {
    "home": handle_home_menu,
    "town_square": handle_town_square_menu,
    "school_entrance": handle_school_entrance_menu,
    "newspaper_club": handle_newspaper_club_menu,
    "general_store": handle_general_store_menu,
    "town_hall": handle_town_hall_menu,
    "bus_stop": handle_bus_stop_menu,
    "tech_store": handle_tech_store_menu,
    "military_base": handle_military_base_actions_internal_menu,
    "outskirts_road": handle_outskirts_road_menu,
    "neighbors_bunker": handle_neighbors_bunker_menu,
    "burger_hut": handle_burger_hut_menu,
    "pawn_shop": handle_pawn_shop_menu,
}

def prompt_restart_or_exit():
    while True:
        print_slow("\nWould you like to start over or exit? (restart/exit)")
        choice = input("> ").strip().lower()
        if choice in ("restart", "r", "start over", "again"):
            return 'restart'
        elif choice in ("exit", "quit", "q"):
            print_slow("Thanks for playing!")
            return 'exit'
        else:
            print_slow("Please type 'restart' or 'exit'.")

def main_menu_loop():
    """The central game loop that dispatches to the appropriate menu handler."""
    from game_data import validate_game_state
    
    while True: # Keep looping until an ending is achieved or game is quit
        # Validate game state for integrity
        errors = validate_game_state()
        if errors:
            print_colored("Game state validation errors detected:", "warning")
            for error in errors:
                print_colored(f"  - {error}", "warning")
            print_colored("Attempting to continue...", "info")
        
        # Check for game over condition at the beginning of each loop
        if game_state.get("ending_achieved"):
            # Call the specific ending handlers from game_actions
            if game_state["ending_achieved"] == "Time's Up":
                handle_time_up_ending()
            elif game_state["ending_achieved"] == "Jailed":
                handle_jailed_ending()
            elif game_state["ending_achieved"] == "Allies Escape":
                handle_allies_escape_ending()
            elif game_state["ending_achieved"] == "Solo Escape":
                handle_solo_escape_ending()
            elif game_state["ending_achieved"] == "Town Evacuated":
                handle_town_evacuated_ending()
            elif game_state["ending_achieved"] == "Missile Destroyed":
                handle_missile_destroyed_ending()

            print_slow("\nThank you for playing!")
            result = prompt_restart_or_exit()
            return result

        # Display location details (description, time status)
        display_location() # Only call once per menu loop

        # Get the appropriate menu handler
        handler = menu_handlers.get(game_state["current_location"])
        if handler:
            try:
                handler() # Call the appropriate menu handler function
            except Exception as e:
                print_colored(f"Error in menu handler: {e}", "warning")
                print_colored("Returning to main menu...", "info")
                game_state["current_location"] = "home"  # Safe fallback
        else:
            print_colored(f"Error: No menu handler for location: {game_state['current_location']}. Exiting game.", "warning")
            sys.exit(0)
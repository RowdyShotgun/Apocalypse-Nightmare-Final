# game_actions.py

# Import necessary data and utilities
import time
import random
from game_data import game_state, locations, INVENTORY_ITEMS, TRUST_THRESHOLDS, TIME_PHASES
from utils import print_slow, clear_screen
from colorama import Fore, Style

# --- Game State Management Functions ---
def advance_time(hours=1, silent=False):
    """Decreases time remaining and updates day phase.
    Provides narrative cues for phase changes.
    'silent=True' prevents narrative messages for minor time deductions."""
    try:
        game_state["time_remaining"] -= hours

        # Ensure time doesn't go below zero
        if game_state["time_remaining"] < 0:
            game_state["time_remaining"] = 0

        if game_state["time_remaining"] == 0:
            game_state["ending_achieved"] = "Time's Up"
            if not silent:
                print_slow("\n--- The clock strikes zero. Your time has run out. ---", mode='slow')
            return

        old_day_phase = game_state["current_day_phase"]
        new_day_phase = old_day_phase

        # Update day phase based on remaining time
        if game_state["time_remaining"] <= 12 and old_day_phase == "morning":
            new_day_phase = "afternoon"
        elif game_state["time_remaining"] <= 6 and old_day_phase == "afternoon":
            new_day_phase = "evening"
        elif game_state["time_remaining"] <= 1 and old_day_phase == "evening":
            new_day_phase = "night"

        if new_day_phase != old_day_phase and not silent:
            print_slow(f"\n--- The day progresses. It is now {new_day_phase.title()}. ---", mode='slow')
            print_slow(f"You have approximately {game_state['time_remaining']} hours left.", mode='slow')

        game_state["current_day_phase"] = new_day_phase

        # Add time feedback for non-silent time advances
        if not silent and hours > 0.1:  # Only show for significant time advances
            if hours >= 1:
                print_slow(f"⏰ {hours} hour(s) have passed.", mode='fast')
            else:
                print_slow(f"⏰ {hours * 60:.0f} minutes have passed.", mode='fast')

        # Add specific time-triggered narrative events
        if game_state["time_remaining"] <= 10 and not game_state["news_warning_issued"]:
            try:
                print_slow(
                    "\nA local radio station interrupts its regular programming with a brief, garbled message about 'unusual atmospheric disturbances'. "
                    "It's subtle, but enough to send a chill down your spine.",
                    mode='slow'
                )
                game_state["news_warning_issued"] = True
                if "radio_warning" not in game_state["inventory"]:
                    game_state["inventory"].append("radio_warning")
                    print_slow("You gained a **Radio Warning** as evidence!", mode='slow')
            except Exception as e:
                # Silently handle any errors in time-triggered events
                pass

        if game_state["time_remaining"] <= 5 and not game_state["military_activity_noticed"]:
            try:
                print_slow(
                    "\nOutside, you notice increased military vehicle traffic. "
                    "Humvees and supply trucks rumble through the streets. "
                    "Something is definitely happening.",
                    mode='slow'
                )
                game_state["military_activity_noticed"] = True
            except Exception as e:
                # Silently handle any errors in time-triggered events
                pass
    except Exception as e:
        # If time advancement fails, just continue without crashing
        pass

def build_jake_trust_opportunity():
    """Creates an opportunity to build trust with Jake through random events or specific actions."""
    # Only trigger if Jake's trust is still low and we haven't had this opportunity yet
    if (game_state["trust_jake"] <= 3 and 
        not game_state.get("jake_trust_opportunity_given", False) and
        random.random() < 0.5):  # 50% chance when conditions are met (increased from 30%)
        
        print_slow("\nYou notice Jake being hassled by some older kids in the hallway.")
        print_slow("They're making fun of his jacket and pushing him around.")
        
        choice = input("Do you want to step in and help? (yes/no): ").strip().lower()
        if choice in ["yes", "y"]:
            print_slow("You step forward. 'Hey, leave him alone!'")
            print_slow("The older kids look surprised, then back off. 'Whatever, losers.'")
            print_slow("Jake looks at you with a mix of surprise and gratitude.")
            game_state["trust_jake"] += 3  # Increased from +2
            print_slow("Jake's trust in you has increased significantly!")
        else:
            print_slow("You decide not to get involved. Jake shoots you a disappointed look.")
            game_state["trust_jake"] -= 1
        
        game_state["jake_trust_opportunity_given"] = True
        advance_time(0.5, silent=True)

# This display_location function should be called by menus.py to show current location info
def display_location():
    """Display current location information."""
    from utils import create_box, create_countdown_box, colorize_location, print_slow_colored
    from game_data import locations
    
    # Set default location if none exists
    if not game_state.get("current_location"):
        game_state["current_location"] = "home"
    
    # Display location description
    if game_state["current_location"] == "home":
        print_slow("You look around your familiar home, the morning sun streaming in.", mode='slow')
    else:
        location_name = colorize_location(game_state["current_location"].replace("_", " ").title())
        print_slow_colored(f"You are at: {location_name}", "location", mode='slow')
        
        # Display the actual location description from game_data
        if game_state["current_location"] in locations:
            location_desc = locations[game_state["current_location"]]["description"]
            print_slow(location_desc, mode='slow')
    
    # Display time and countdown
    time_box = create_countdown_box(game_state["time_remaining"], game_state["current_day_phase"])
    print_slow(time_box, mode='slow')

# --- Initial Event ---
def handle_vision_event():
    """Handle the initial vision event that starts the game."""
    print_slow("You wake up in a cold sweat, your heart pounding. The nightmare was so vivid...", mode='slow')
    print_slow("A nuclear missile. Your city. The explosion. The end.", mode='slow')
    print_slow("But it felt so real...", mode='slow')
    
    # Set player to home location
    game_state["current_location"] = "home"

# --- Specific Action Functions (receive choices from menus) ---

def handle_talk_parents_action(choice_num):
    """Handles specific choices when talking to parents."""
    from utils import colorize_name, print_slow_colored
    
    if not game_state["parents_warned"]:
        if choice_num == 1: # Tell them about the nuclear missile vision.
            print_slow_colored(f"{colorize_name(game_state['protagonist_name'])} sits down and explains the vision, pouring out fear and urgency.", "character", mode='slow')
            print_slow_colored("Your mom puts a hand to your forehead, concern in her eyes. 'Are you feeling alright, sweetie? You look a little feverish.'", "character", mode='slow')
            print_slow_colored("Your dad suggests you've been working too hard. They clearly don't believe you.", "character", mode='slow')
            game_state["parents_warned"] = True
            print_slow("A wave of sadness washes over you. You couldn't even convince them.", mode='slow')
            input("Press Enter to continue...")
        elif choice_num == 2: # Keep silent and talk about something else.
            print_slow_colored(f"{colorize_name(game_state['protagonist_name'])} decides to keep the burden to themselves. 'Just checking in. Everything okay?'", "character", mode='slow')
            print_slow("They nod, oblivious. The conversation drifts to mundane topics.", mode='slow', color=Fore.YELLOW)
            input("Press Enter to continue...")
    else: # Already warned parents
        print_slow("Your parents are still going about their day. They sometimes glance at you with lingering worry.", mode='slow')
        print_slow("They haven't brought up your 'feverish' vision again.", mode='slow')
        input("Press Enter to continue...")
    advance_time(0.5, silent=True)


def handle_talk_alex_action(choice_num):
    """Handles specific choices when talking to Alex."""
    from utils import colorize_name, print_slow_colored
    
    if not game_state.get("talked_to_alex_about_vision", False):
        if choice_num == 1: # Tell him about the nuclear missile vision.
            print_slow_colored(f"You recount your terrifying vision in detail. {colorize_name('Alex')} listens intently, but his expression remains analytical.", "character", mode='slow')
            game_state["has_shared_vision_with_friends"] = True
            game_state["talked_to_alex_about_vision"] = True
            if game_state["trust_alex"] >= 4:  # Back to requiring effort
                print_slow_colored(f"{colorize_name('Alex')} nods slowly. 'That's wild... but you usually don't make things up. I'll help you look into it. What kind of proof do we need?'", "character", mode='slow')
                game_state["knowledge"] += 1
            elif game_state["trust_alex"] >= 2:
                print_slow_colored(f"{colorize_name('Alex')} raises an eyebrow. 'That sounds crazy, {colorize_name(game_state['protagonist_name'])}. Are you sure you're okay? Maybe you should get some sleep.'", "character", mode='slow')
                game_state["trust_alex"] -= 0.5  # Reduced penalty from -1
            else:
                print_slow_colored(f"{colorize_name('Alex')} snorts. 'You're losing it, {colorize_name(game_state['protagonist_name'])}. Stick to facts, not fantasies.' He dismisses you.", "character", mode='slow')
                game_state["trust_alex"] -= 1  # Reduced penalty from -2
        elif choice_num == 2: # Ask for his research help on a hypothetical disaster.
            print_slow("You frame it as a hypothetical scenario for an article: 'If a major disaster hit, what kind of supplies would a town need? How would people evacuate?'", mode='slow')
            print_slow("Alex brightens. 'An excellent hypothetical! I've actually researched emergency preparedness for a past project. Let me dig out my notes.'", mode='slow')
            game_state["knowledge"] += 2
            game_state["inventory"].append("survival_notes_alex")
            print_slow("Alex hands you some detailed notes on disaster preparedness. You gain **Survival Notes**.", mode='slow')
        elif choice_num == 3: # Talk about newspaper club business.
            print_slow("You chat about the next newspaper issue, discussing headlines and deadlines. It's a mundane, comforting distraction.", mode='slow')
            game_state["trust_alex"] += 0.5
            print_slow("You feel slightly more connected with Alex.")
    else: # If already talked to Alex about vision
        if game_state["trust_alex"] >= 4:  # Back to requiring effort
            print_slow("Alex is still processing your warning. 'I'm checking the news, but nothing official yet. Still, I'm with you. What's our next move?'", mode='slow')
        elif game_state["trust_alex"] >= 2:
            print_slow("Alex seems a bit awkward. He quickly changes the subject, clearly unconvinced by your vision.", mode='slow')
        else:
            print_slow("Alex avoids eye contact and grunts a non-committal response. He's clearly trying to distance himself.", mode='slow')
    input("Press Enter to continue...")
    advance_time(0.5, silent=True)

def handle_talk_maya_action(choice_num):
    """Handles specific choices when talking to Maya."""
    from utils import colorize_name, print_slow_colored
    
    if not game_state.get("talked_to_maya_about_vision", False):
        if choice_num == 1: # Confide in her about the vision.
            print_slow_colored(f"{colorize_name(game_state['protagonist_name'])} tells {colorize_name('Maya')} everything, the terrifying vision, the bomb, the short time left.", "character", mode='slow')
            game_state["has_shared_vision_with_friends"] = True
            game_state["talked_to_maya_about_vision"] = True
            if game_state["trust_maya"] >= 5:  # Back to requiring effort
                print_slow_colored("Her eyes widen, and her usual optimism falters. She looks genuinely scared. 'Oh my god... that's... terrifying. But I believe you. What can we even do?'", "character", mode='slow')
                game_state["trust_maya"] += 5
                print_slow("Maya is shaken, but she believes you. Your bond with her deepens.", mode='slow')
            elif game_state["trust_maya"] >= 3:  # Moderate trust - concerned but not convinced
                print_slow_colored("Maya's brow furrows. 'That sounds awful. Maybe it was just a really bad dream?' She's clearly concerned, but struggles to accept it.", "character", mode='slow')
                game_state["trust_maya"] += 1
            else:
                print_slow_colored("Maya looks uncomfortable and quickly changes the subject, clearly worried about your mental state.", "character", mode='slow')
                game_state["trust_maya"] -= 0.5  # Reduced penalty
        elif choice_num == 2: # Talk about art or other light topics.
            print_slow(f"{game_state['protagonist_name']} talks about her sketches and the latest school gossip. Maya seems happy for the distraction.", mode='slow')
            game_state["trust_maya"] += 0.5
            print_slow("You feel slightly more connected with Maya.")
    else:
        if game_state["trust_maya"] >= 5:  # Back to requiring effort
            print_slow("Maya is anxious but supportive. 'I'm here for you, no matter what happens. We'll face this together.'", mode='slow')
        elif game_state["trust_maya"] >= 3:
            print_slow("Maya tries to offer comfort, but her voice is strained. She's clearly thinks you're overwhelmed.", mode='slow')
        else:
            print_slow("Maya avoids eye contact and quickly finds an excuse to leave. She's clearly uncomfortable around you now.", mode='slow')
    input("Press Enter to continue...")
    advance_time(0.5, silent=True)

def handle_talk_ben_action(choice_num):
    """Handles specific choices when talking to Ben."""
    from utils import colorize_name, print_slow_colored
    
    if not game_state.get("talked_to_ben_about_vision", False):
        if choice_num == 1: # Tell him about the nuclear missile vision.
            print_slow_colored(f"{colorize_name(game_state['protagonist_name'])} tells {colorize_name('Ben')} about the nuclear missile vision, emphasizing the urgency and practical implications.", "character", mode='slow')
            game_state["has_shared_vision_with_friends"] = True
            game_state["talked_to_ben_about_vision"] = True
            if game_state["trust_ben"] >= 4:  # Back to requiring effort
                print_slow_colored(f"{colorize_name('Ben')}'s eyes narrow, considering. 'That's heavy... but if it's true, we need supplies. A place to go. What's the plan?'", "character", mode='slow')
                game_state["trust_ben"] += 10
                game_state["knowledge"] += 1
                game_state["inventory"].append("survival_checklist")
                print_slow_colored("Ben starts listing things: 'Water, non-perishables, a map, maybe a working vehicle...' You gained **Survival Checklist**.", "item", mode='slow')
            elif game_state["trust_ben"] >= 2:
                print_slow_colored(f"{colorize_name('Ben')} looks uncomfortable. 'Look, I'm not really good with... hypothetical apocalypses. What's the actual problem, {colorize_name(game_state['protagonist_name'])}?' He tries to change the subject.", "character", mode='slow')
                game_state["trust_ben"] -= 0.5  # Reduced penalty from -1
            else:
                print_slow_colored(f"{colorize_name('Ben')} shakes his head. 'Sounds like a bad acid trip, {colorize_name(game_state['protagonist_name'])}. You okay?' He dismisses your story completely.", "character", mode='slow')
                game_state["trust_ben"] -= 1  # Reduced penalty from -2
        elif choice_num == 2: # Ask him for help with something practical (e.g., getting supplies).
            print_slow(f"{game_state['protagonist_name']} asks Ben: 'I need to get out of here, or get some serious supplies. You know this town better than anyone. Any ideas?'", mode='slow')
            
            if game_state["has_car_keys"]:
                # Player has already discovered the truck
                print_slow(
                    "Ben taps his chin. 'Hmm. A truck with no gas... that's a problem.' "
                    "He pauses. 'I might know where some spare fuel cans are. "
                    "And old Mr. Henderson's truck always has the keys in it.'",
                    mode='slow'
                )
            else:
                # Player hasn't discovered the truck yet
                print_slow(
                    "Ben taps his chin. 'Hmm. You'd need fuel for any vehicle you find.' "
                    "He pauses. 'I might know where some spare fuel cans are. "
                    "And old Mr. Henderson's truck always has the keys in it.'",
                    mode='slow'
                )
            
            # Ben offers gas from his generator
            print_slow("Ben thinks for a moment. 'Actually, I have some gas for my generator. I can spare a can if you need it.'")
            print_slow("He disappears for a moment and returns with a small gas can.")
            if "gas_can" not in game_state["inventory"]:
                game_state["inventory"].append("gas_can")
                game_state["car_gas"] += 30
                print_slow("Ben hands you a **Gas Can**. You gained 30% gas!")
            else:
                game_state["car_gas"] += 30
                print_slow("Ben refills your gas can. You gained 30% gas!")
            
            # Add bunker information if Ben has high trust
            if game_state["trust_ben"] >= 6 and "bunker_rumor" not in game_state["inventory"]:
                print_slow("Ben lowers his voice. 'Also... I heard a rumor about a neighbor who built a bunker out in the hills. Supposedly it's well-hidden, but if you know where to look...'")
                game_state["inventory"].append("bunker_rumor")
                print_slow("Ben gives you directions to the hidden bunker. You gained **Bunker Rumor**!")
            
            game_state["trust_ben"] += 5
            game_state["inventory"].append("tip_henderson_truck")
            print_slow("Ben gives you some useful information about Mr. Henderson's truck. You gained **Truck Tip**.", mode='slow')
        elif choice_num == 3: # Talk about practical things (e.g., school, work, etc.).
            print_slow(f"{game_state['protagonist_name']} and {colorize_name('Ben')} discuss practical matters - school, work, the usual stuff.", mode='slow')
            game_state["trust_ben"] += 1
            print_slow("You feel slightly more connected with Ben.")
    else: # If already talked to Ben about vision
        if game_state["trust_ben"] >= 4:  # Back to requiring effort
            print_slow("Ben is focused on practical matters. 'So what's our next move? We need a plan, and fast.'", mode='slow')
        elif game_state["trust_ben"] >= 2:
            print_slow("Ben seems a bit awkward, clearly still processing your warning but trying to be supportive.", mode='slow')
        else:
            print_slow("Ben avoids the topic entirely, clearly uncomfortable with your 'crazy' story.", mode='slow')
    input("Press Enter to continue...")
    advance_time(0.5, silent=True)

def print_jake_post_vision_dialogue():
    """Prints Jake's reaction after the vision has been shared, depending on his trust level."""
    if game_state["trust_jake"] >= 5:  # Back to requiring effort
        print_slow("Jake looks agitated. 'Still nothing concrete? We need to do something, pronto!'")
    else:
        print_slow("Jake avoids eye contact, mumbling something about being busy. He doesn't want to talk about your 'crazy' vision.")

def handle_talk_jake_action(choice_num):
    """Handles specific choices when talking to Jake."""
    if game_state["trust_jake"] < 3 and not game_state.get("talked_to_jake_about_vision", False):
        print_slow(f"Jake just glares at {game_state['protagonist_name']}. 'What do you want, loser?' He doesn't seem interested in talking.")
        input("Press Enter to continue...")
    elif not game_state.get("talked_to_jake_about_vision", False):
        if choice_num == 1: # Tell him about the vision (carefully).
            print_slow(f"You briefly and gravely tell him about the impending doom, trying to appeal to any hidden survival instinct.")
            game_state["talked_to_jake_about_vision"] = True
            if game_state["trust_jake"] >= 5:  # Back to requiring effort
                print_slow(f"Jake's tough facade cracks, a flicker of fear in his eyes. 'You're serious? Fine. If you need muscle, I'm in.'")
                game_state["trust_jake"] += 10
                game_state["mob_of_civilians"] = True
                print_slow("Jake seems to take you seriously, and you feel like he could help you rally others.")
            elif game_state["trust_jake"] >= 3:
                print_slow(f"Jake laughs, but it sounds forced. 'A bomb? You're crazy, {game_state['protagonist_name']}.' He shakes his head, but he doesn't walk away immediately.")
                game_state["trust_jake"] -= 0.5  # Reduced penalty from -1
            else:
                print_slow(f"Jake scoffs. 'And I thought *I* was messed up. Get lost.' He pushes you slightly.")
                game_state["trust_jake"] -= 1  # Reduced penalty from -2
        elif choice_num == 2: # Ask for a favor (e.g., getting past someone, intimidating someone).
            print_slow("You ask him to 'handle' a minor obstacle (e.g., distract someone, 'convince' someone to move).")
            if game_state["trust_jake"] >= 3:
                print_slow("'Maybe. What's in it for me?' Jake considers, a smirk on his face. He's open to helping for a price.")
                game_state["jake_owed_favor"] = True
            else:
                print_slow("'Get your own dirty work done.' Jake dismisses you.")
        elif choice_num == 3: # Challenge his authority (risky).
            print_slow("You try to challenge Jake's usual bullying. 'Why don't you pick on someone your own size?'")
            if game_state["trust_jake"] <= 2:
                print_slow("Jake shoves you hard against the lockers. 'That's it, runt! You asked for it!'")
                game_state["ending_achieved"] = "Jailed"
            else:
                print_slow("Jake seems surprised, a flicker of respect in his eyes. 'Whoa, feisty today. Watch it.'")
                game_state["trust_jake"] += 1
        elif choice_num == 4: # NEW: Show him respect or offer help.
            print_slow("You approach Jake differently. 'Hey, I know things are rough. Need any help with anything?'")
            if game_state["trust_jake"] <= 2:
                print_slow("Jake looks surprised, then suspicious. 'Why would you help me?' But there's a hint of curiosity.")
                game_state["trust_jake"] += 1
                print_slow("Jake seems to appreciate the gesture, even if he's not sure about your motives.")
            else:
                print_slow("Jake nods slightly. 'Maybe. Thanks.' He seems to appreciate the offer.")
                game_state["trust_jake"] += 1
        elif choice_num == 5: # NEW: Stand up for him or defend him.
            print_slow("You notice someone else giving Jake trouble. You step in to help.")
            print_slow("Jake looks at you with a mix of surprise and grudging respect.")
            game_state["trust_jake"] += 2
            print_slow("Jake seems to remember this gesture. 'Thanks... I guess.'")
        elif choice_num == 6: # NEW: Reminisce about old times.
            print_slow("You bring up some old memories from when you were kids. 'Remember when we used to...'")
            print_slow("Jake's expression softens slightly. 'Yeah, those were simpler times.'")
            game_state["trust_jake"] += 1
            print_slow("Jake seems to appreciate the trip down memory lane. His guard lowers a bit.")
    else: # If Jake has already been told the vision
        print_jake_post_vision_dialogue()
    advance_time(0.5, silent=True)


def handle_town_hall_interaction_action(choice_num):
    """Handles specific choices when interacting at Town Hall."""
    if choice_num == 1: # Demand to see the Mayor and show proof.
        evidence_found = False
        if "survival_notes_alex" in game_state["inventory"] or "radio_warning" in game_state["inventory"] or "bunker_rumor" in game_state["inventory"]:
            evidence_found = True

        if game_state["knowledge"] >= 5 and evidence_found:
            print_slow(
                "You present your evidence, explaining it with compelling knowledge. The mayor is called in, "
                "and his face goes pale as he reviews your proof. 'This... this is serious. "
                "We'll begin evacuation procedures immediately.'",
                mode='slow'
            )
            game_state["authority_of_town"] += 5
            game_state["mayor_warned"] = True
            print_slow("The Mayor is convinced! You gained significant **Authority of Town**.")
        else:
            print_slow(
                "You have nothing convincing to show or lack the knowledge to present it effectively. "
                "The mayor is not impressed."
            )
            print_slow(
                "You're quickly escorted out. Your warnings fall on deaf ears."
            )
            game_state["authority_of_town"] -= 1
            game_state["current_location"] = "town_square"
    elif choice_num == 2: # Try to explain the urgency to the secretary.
        print_slow("You try to calmly explain your vision, the impending doom, the need for action.")
        print_slow("The secretary listens, her eyes widening slightly, but then she shakes her head.")
        print_slow("'Son, I appreciate your concern, but the Mayor is very busy. Perhaps you should see a doctor.'")
        game_state["authority_of_town"] -= 0.5
        print_slow("You feel a slight dip in how seriously you're being taken.")
    elif choice_num == 3: # Leave politely.
        print_slow("You decide it's a dead end for now and leave quietly.")
        game_state["current_location"] = "town_square"
    advance_time(1)
    try:
        input("Press Enter to continue...")
    except (EOFError, KeyboardInterrupt):
        # Handle input errors gracefully
        pass


def handle_computer_use_action(choice_num):
    """Handles specific choices when using the computer."""
    # Give backpack the first time the computer is used
    if "backpack" not in game_state["inventory"]:
        print_slow("You notice your old **Backpack** slung over the back of your computer chair. This will help you carry more supplies!")
        game_state["inventory"].append("backpack")
    if choice_num == 1: # Search for 'nuclear threat' or 'impending doom'.
        print_slow(
            "You search for global nuclear threats. The results are overwhelming, but nothing points specifically to your town. "
            "It makes the world seem too big, your vision too small."
        )
        game_state["knowledge"] += 1
        print_slow("🧠 You gained Knowledge! (Research & Learning)")
        print_slow("💡 Tip: Knowledge helps you understand technology and convince others.")
        advance_time(1)
    elif choice_num == 2: # Look for unusual local news reports.
        print_slow(
            "You comb through local news archives. You find a few strange reports: unexplained seismic activity, "
            "odd military transport sightings on obscure backroads."
        )
        game_state["knowledge"] += 2
        print_slow(
            "🧠 You gained Knowledge! (Research & Learning)"
        )
        print_slow("💡 Tip: Knowledge helps you understand technology and convince others.")
        advance_time(1)
    elif choice_num == 3: # Check for survival guides or emergency bunkers.
        print_slow("You search for guides on surviving an apocalypse and local private bunkers.")
        found_rumor = False
        if game_state["knowledge"] >= 2:
            found_rumor = True
        else:
            if random.random() < 0.3:
                found_rumor = True
        if found_rumor:
            if "bunker_rumor" not in game_state["inventory"]:
                print_slow(
                    "You stumble upon an old, obscure forum post mentioning a well-hidden local bunker, possibly your neighbor's. "
                    "It gives vague directions."
                )
                game_state["inventory"].append("bunker_rumor")
                print_slow(
                    "You gain **Knowledge** about local survival tactics and a **Rumor about a Neighbor's Bunker**."
                )
            else:
                print_slow("You recall the rumor you already found about a neighbor's bunker. No new details emerge.")
        else:
            print_slow("You find some generic survival tips, but nothing specific to your town.")
        advance_time(1)
    elif choice_num == 4: # Stop using the computer.
        print_slow("You close the computer, feeling a mix of dread and growing certainty.")
        input("Press Enter to continue...")
        advance_time(0.5, silent=True)
        return True # Signal to the menu to go back
    return False # Signal to the menu to stay in computer menu


def handle_shout_warning():
    """Handles the 'warn openly' action."""
    print_slow(f"You take a deep breath and scream, 'A BOMB IS COMING! WE NEED TO EVACUATE!'")
    
    # Check if Maya believes and can help
    maya_bonus = 0
    if game_state["trust_maya"] >= 5 and game_state.get("talked_to_maya_about_vision", False):
        maya_bonus = 2
        print_slow("Maya steps forward beside you, her voice trembling but determined. 'He's telling the truth! I believe him!'")
        print_slow("Her genuine fear and conviction seem to affect some of the crowd. People look more concerned now.")
    
    # Calculate effective authority (base + Maya's help)
    effective_authority = game_state["authority_of_town"] + maya_bonus
    
    if effective_authority >= 3:
        print_slow("A few people stop, looking startled. Some begin murmuring, a seed of doubt planted. The crowd begins to swell slightly.")
        game_state["mob_of_civilians"] = True
        game_state["authority_of_town"] += 1
        if maya_bonus > 0:
            print_slow("Maya's support made all the difference. People are starting to take you seriously.")
    else:
        print_slow("People stop, stare, then quickly avert their gaze, murmuring. Some point and laugh.")
        print_slow("You're dismissed as a lunatic. Your efforts feel futile, and you feel a wave of embarrassment.")
        if game_state["trust_alex"] > 0:
            game_state["trust_alex"] -= 1
        game_state["failed_public_warning"] = True # NEW: Set flag if warning fails
    advance_time(0.5)





def handle_gather_supplies_action(choice_num):
    """Handles specific choices for gathering supplies."""
    if choice_num == 1: # Go to the General Store (buy or steal).
        game_state["current_location"] = "general_store"
        print_slow(f"You head to the General Store.")
    elif choice_num == 2: # Go to Burger Hut (earn cash).
        game_state["current_location"] = "burger_hut"
        print_slow(f"You head to the Burger Hut.")
    elif choice_num == 3: # Search for items at Home.
        print_slow("You search through your home, starting with the kitchen.")
        if "kitchen_supplies_taken" not in game_state["inventory"]:
            print_slow("In the kitchen, you find some canned goods and non-perishable food items.")
            game_state["inventory"].append("kitchen_supplies_taken")
            game_state["inventory"].append("supplies")
            print_slow("You found some **Supplies** from the kitchen!")
        else:
            print_slow("You've already searched the kitchen thoroughly. There's nothing else useful here.")
        input("Press Enter to continue...")
        advance_time(0.5, silent=True)
    elif choice_num == 4: # Go back.
        print_slow("You decide to rethink gathering supplies.")
        advance_time(0.1, silent=True)


def handle_involve_friends_escape_action(choice_num):
    """Handles specific choices for involving friends in escape."""
    if choice_num == 1: # Go to the Newspaper Club (Talk to friends).
        game_state["current_location"] = "newspaper_club"
        print_slow(f"You head to the Newspaper Club.")
    elif choice_num == 2: # Seek access to the Neighbor's Bunker (if you know about it).
        if "bunker_rumor" in game_state["inventory"]:
            game_state["current_location"] = "neighbors_bunker"
            print_slow(f"You head towards the neighbor's bunker.")
        else:
            print_slow("You don't know enough about a neighbor's bunker to seek it out. Maybe try researching it first?")
            input("Press Enter to continue...")
            advance_time(0.1, silent=True)
    elif choice_num == 3: # Go back.
        print_slow("You decide to rethink involving friends in your escape.")
        advance_time(0.1, silent=True)


def handle_general_store_interaction_action(choice_num):
    cash_unit_cost = 1 # Define cost for general store items

    if choice_num == 1: # Try to buy supplies (e.g., food, gas).
        if game_state["cash"] >= cash_unit_cost: # Check if player has enough cash units
            print_slow(
                f"You buy some canned food and a small gas can for {cash_unit_cost} cash unit(s). "
                "Mr. Jenkins grunts, taking your money."
            )
            game_state["cash"] -= cash_unit_cost # Deduct cash unit
            game_state["inventory"].append("canned_food")
            if "gas_can" not in game_state["inventory"]:
                game_state["inventory"].append("gas_can")
                game_state["car_gas"] += 30
                print_slow("You now have **Canned Food** and a **Gas Can**.")
            else:
                print_slow("You now have **Canned Food**.")
        else:
            print_slow(
                f"You don't have enough cash for anything useful. You have {game_state['cash']} cash unit(s), "
                f"but need {cash_unit_cost}."
            )
    elif choice_num == 2: # Attempt to steal supplies.
        print_slow("You eye a small gas can. Attempt to steal it?")
        return "steal_sub_menu" # Signal to menus.py to show sub-menu
    elif choice_num == 3: # Talk to Mr. Jenkins about the situation.
        print_slow("You try to tell Mr. Jenkins about your vision. He stares at you with a blank expression.")
        print_slow("'Kid, just pay for your candy,' he grunts, clearly not believing a word.")
        game_state["authority_of_town"] -= 0.5
        print_slow("You feel less credible in this town.")
    elif choice_num == 4: # Help Mr. Jenkins with heavy boxes.
        if not game_state.get("jenkins_helped", False):
            print_slow("You notice Mr. Jenkins struggling with some heavy boxes in the back of the store.")
            print_slow("'Hey kid, give me a hand with these boxes? I'll give you something for your trouble.'")
            
            choice = input("Help Mr. Jenkins? (yes/no): ").strip().lower()
            if choice in ["yes", "y"]:
                print_slow("You help Mr. Jenkins move the heavy boxes to the storage room.")
                
                # 15% chance of breaking the box and getting kicked out
                if random.random() < 0.15:
                    print_slow("CRASH! One of the boxes slips from your grip and breaks open.")
                    print_slow("'What did you do?!' Mr. Jenkins yells. 'Get out of my store! You're banned!'")
                    game_state["jenkins_banned"] = True
                    game_state["current_location"] = "town_square"
                    print_slow("You've been banned from the general store for the rest of the game.")
                else:
                    print_slow("The boxes are moved safely. Mr. Jenkins nods appreciatively.")
                    print_slow("'Thanks, kid. Here, take some supplies as payment.'")
                    game_state["inventory"].append("supplies")
                    print_slow("You gained some **Supplies**!")
                    game_state["authority_of_town"] += 0.5
                    print_slow("Mr. Jenkins seems to respect you more now.")
                
                game_state["jenkins_helped"] = True
            else:
                print_slow("'Suit yourself,' Mr. Jenkins grumbles, continuing to struggle with the boxes.")
        else:
            print_slow("You've already helped Mr. Jenkins with the boxes.")
    elif choice_num == 5: # Leave the store.
        print_slow("You leave the general store.")
        game_state["current_location"] = "town_square"
    advance_time(0.5)
    return None # Default return for actions without sub-menus


def handle_jake_favor_action():
    """Handles asking Jake for a favor, after he owes one."""
    if game_state.get("jake_owed_favor", False):
        print_slow(f"You approach {game_state['protagonist_name']}. 'Remember that favor you owe me?'")
        print_slow("Jake grunts. 'Yeah, yeah. What do you need?'")
        # Give a specific useful item as a favor
        if game_state["cash"] < 1:
            print_slow("You ask him to 'acquire' some cash for you.")
            print_slow("Jake nods, disappears for a bit, and returns with a single cash unit, looking smug. "
                       "'Don't ask where I got it.'"
            )
            game_state["cash"] += 1
            print_slow("You gained **1 Cash Unit**!")
        elif game_state["inventory"].count("supplies") < 2:
            print_slow("You ask him to get some general supplies.")
            print_slow("Jake rolls his eyes, but eventually comes back with a small bag of non-perishables. 'Happy now?'")
            game_state["inventory"].append("supplies")
            print_slow("You gained some **Supplies**!")
        else:
            print_slow("You ask him to get a rare tech part.")
            print_slow("Jake sighs, but after some time, he returns with a scavenged **Tech Part**. 'Took some doing. You owe me.'")
            game_state["tech_parts"] += 1
            game_state["inventory"].append("scavenged_tech_part")
            print_slow("You gained a **Tech Part**!")
        game_state["jake_owed_favor"] = False # Favor is used up
        game_state["trust_jake"] -= 1 # Using a favor might slightly annoy him
        print_slow("Jake's favor has been used.")
    else:
        print_slow("Jake doesn't owe you a favor right now.")
    advance_time(0.5)


def handle_steal_general_store_action(sub_choice_num):
    """Handles the nested choice for stealing from general store."""
    has_backpack = "backpack" in game_state["inventory"]
    success_chance = 0.65 if has_backpack else 0.35
    if sub_choice_num == 1: # Yes, try to steal.
        if random.random() < success_chance:
            print_slow(
                f"You expertly slip the **Gas Can** into your {'backpack' if has_backpack else 'jacket'} "
                "when Mr. Jenkins isn't looking."
            )
            if "gas_can" not in game_state["inventory"]:
                game_state["inventory"].append("gas_can")
            game_state["car_gas"] += 50
            print_slow("You gained a **Gas Can**!")
        else:
            print_slow("You fumble, and Mr. Jenkins' eyes snap to you. 'Get out of my store, you thief!' He shoves you out the door. You've made an enemy.")
            game_state["ending_achieved"] = "Jailed"
    elif sub_choice_num == 2: # No, it's too risky.
        print_slow("You decide against stealing. It's not worth the risk.")
    advance_time(0.5)


def handle_burger_hut_work_action(choice_str):
    """Handles the actual working action at Burger Hut."""
    from utils import colorize_money, print_slow_colored
    
    cash_earned = 1 # One cash unit earned per shift
    if choice_str == "yes":
        if game_state["time_remaining"] >= 4:
            print_slow("You spend four grueling hours flipping burgers and dealing with customers.")
            game_state["cash"] += cash_earned
            advance_time(4)
            print_slow_colored(f"You earned {colorize_money(f'**{cash_earned} Cash Unit(s)**')}!", "success")
        else:
            print_slow("You don't have enough time left for a full shift.")
            print_slow("You leave the Burger Hut feeling frustrated.")
    else: # choice_str == "no"
        print_slow("You decide not to work right now. Time is precious.")
    game_state["current_location"] = "town_square" # Always return to town after interaction
    advance_time(0.1, silent=True)


def handle_go_to_class_action():
    """Handles the 'go to class' action from school."""
    if not game_state["has_attended_class"]: # NEW: Check if class already attended
        print_slow(f"You attend a class. It's hard to focus with the weight of the vision.")
        knowledge_gain = 1
        if "notebook" in game_state["inventory"]:
            knowledge_gain += 1
            print_slow("Your notebook helps you take better notes and understand more. (+1 Knowledge)", color=Fore.CYAN)
        game_state["knowledge"] += knowledge_gain
        advance_time(2)
        game_state["has_attended_class"] = True # NEW: Set flag after attending
        print_slow(f"🧠 You gained {knowledge_gain} Knowledge! (Research & Learning)")
        print_slow("💡 Tip: Knowledge helps you understand technology and convince others.")
        
        # Small trust boost for being in class with Jake (shows you're not avoiding him)
        if game_state["trust_jake"] <= 2:
            print_slow("Jake notices you actually showed up to class. He gives you a slight nod of acknowledgment.")
            game_state["trust_jake"] += 1
            print_slow("Jake's trust in you has increased slightly!")
        
        # NEW: Supplies reward for attending class (represents gathering supplies from school)
        if "school_supplies_taken" not in game_state["inventory"]:
            print_slow("After class, you manage to grab some supplies from the school's emergency kit.")
            game_state["inventory"].append("school_supplies_taken")
            game_state["inventory"].append("supplies")
            print_slow("You gained some **Supplies** from school!")
        
        # After class, present menu to talk to Jake or return
        while True:
            print_slow("After class, you see Jake lingering by the door.")
            print("1. Talk to Jake")
            print("2. Return to school entrance")
            choice = input("> ").strip()
            if choice == "1":
                handle_talk_jake_action(1) # Pass a dummy choice for Jake's specific logic
            elif choice == "2":
                break
            else:
                print_slow("Invalid choice. Please enter 1 or 2.")
    else:
        print_slow("You've already attended class today. There's nothing new to learn from another lecture.")
        input("Press Enter to continue...")
        advance_time(0.1, silent=True) # Small time cost for trying again





def handle_bunker_access_action(action_type):
    """Handles specific choices for bunker access."""
    if action_type == "examine door":
        print_slow(locations["neighbors_bunker"]["interactions"]["examine door"])
        input("Press Enter to continue...")
        advance_time(0.5, silent=True)
    elif action_type == "knock":
        if not game_state["bunker_unlocked"]:
            print_slow(locations["neighbors_bunker"]["interactions"]["knock"])
            if "bunker_rumor" in game_state["inventory"] and game_state["trust_ben"] >= 10:
                print_slow(
                    "Recalling Ben's tip, you try the code he mentioned. There's a click and a hiss as the heavy door "
                    "swings open."
                )
                game_state["bunker_unlocked"] = True
                print_slow("The **Neighbor's Bunker** is now unlocked!")
            else:
                print_slow("You knock heavily, but only silence answers. No one seems to be home. The door remains locked.")
        else: # Already unlocked
            print_slow("The bunker door is already open. You can now enter.")
        advance_time(0.5)
    elif action_type == "enter":
        if game_state["bunker_unlocked"]:
            print_slow("You step inside the cool, damp air of the bunker. It's surprisingly well-stocked.")
            if "bunker_supplies_taken" not in game_state["inventory"]:
                game_state["inventory"].append("bunker_supplies_taken")
                game_state["inventory"].append("supplies")
                game_state["inventory"].append("tech_parts")
                game_state["inventory"].append("tech_parts")
                print_slow("You find a cache of **Supplies** and some advanced **Tech Parts**.")
            else:
                print_slow("You've already taken the main supplies from here.")
            game_state["current_location"] = "neighbors_bunker" # Stay in bunker after entering
        else:
            print_slow("The bunker door is locked tight. You can't enter yet.")
        advance_time(1)


def handle_military_base_approach_action(choice_num):
    """Handles specific choices for approaching the military base."""
    # NEW: Check for failed public warning first, only if trying to approach or sneak/use authority
    if game_state["failed_public_warning"] and choice_num in [1, 2]: # If they try to sneak or use authority after failing publicly
        print_slow(
            "Your previous chaotic public warnings have been noted by authorities. As you approach the base, "
            "you're immediately recognized and apprehended."
        )
        game_state["ending_achieved"] = "Jailed"
        advance_time(0.5)
        return # End action here, immediately to Jailed ending

    if choice_num == 1: # Attempt to Sneak In.
        print_slow(
            "You approach the military base perimeter, scanning for weak points in the fence."
        )
        print_slow(
            "Searchlights sweep the area. You can see guards patrolling the perimeter."
        )
        
        if game_state["knowledge"] >= 3 and game_state["tech_parts"] >= 1:
            print_slow(
                "Your knowledge of security systems helps you identify blind spots in the camera coverage."
            )
            print_slow(
                "Using your **Tech Parts**, you carefully disable a camera and create a small diversion."
            )
            print_slow(
                "Heart pounding, you wait for the right moment..."
            )
            input("Press Enter to continue...")
            
            print_slow(
                "A guard turns away to investigate the diversion. This is your chance!"
            )
            print_slow(
                "You slip through the fence and duck behind some equipment. The base sprawls before you."
            )
            print_slow(
                "You've successfully infiltrated the **Military Base**!"
            )
            game_state["military_base_accessed"] = True
            game_state["current_location"] = "military_base"
        else:
            print_slow(
                "You can't find a way in without being spotted. A guard dog barks, and you hear shouts."
            )
            print_slow(
                "Alarms blare! You are quickly apprehended."
            )
            game_state["ending_achieved"] = "Jailed"
    elif choice_num == 2: # Try to Use Authority to Get In (if you have it).
        if game_state["authority_of_town"] >= 5:
            print_slow(
                "You boldly approach the main gate, your confidence bolstered by your authority in town."
            )
            print_slow(
                "The guard at the gate looks you over carefully, then checks a clipboard."
            )
            print_slow(
                "After a tense moment, he nods and waves you through. 'Proceed, sir.'"
            )
            print_slow(
                "You walk through the gate, the military base opening up before you."
            )
            print_slow(
                "You've gained access to the **Military Base** through official channels!"
            )
            game_state["military_base_accessed"] = True
            game_state["current_location"] = "military_base"
        else:
            print_slow(
                "You try to assert authority, but the guard just stares blankly. 'Beat it, kid. Civilians aren't allowed here.'"
            )
            print_slow(
                "He gestures firmly with his rifle. You quickly back away."
            )
    elif choice_num == 3: # Go back to Town Square.
        print_slow("You decide to rethink your approach to the military base and head back to town.")
        game_state["current_location"] = "town_square"
    advance_time(1)


def handle_military_base_action(choice_num):
    """Handles actions taken while inside the military base."""
    if choice_num == 1: # Search for the Laser Control Room.
        print_slow(
            "You navigate through corridors, looking for signs to a 'Laser Control' or 'Satellite Operations' room."
        )
        if game_state["knowledge"] >= 5:
            print_slow(
                "Your extensive research pays off. You find a heavily secured door marked 'Orbital Defense Control'."
            )
            handle_laser_activation() # This specific critical action has its own input loop
        else:
            print_slow(
                "The base is a maze. You get lost, wasting precious time. Footsteps echo nearby."
            )
            advance_time(1)
            if game_state["time_remaining"] <= 0:
                game_state["ending_achieved"] = "Time's Up"
        if game_state["time_remaining"] <= 5 and not game_state["ending_achieved"]:
            print_slow(
                "A patrol spots you! 'Intruder alert!'"
            )
            game_state["ending_achieved"] = "Jailed"

    elif choice_num == 2: # Look for military personnel to convince.
        print_slow(
            "You encounter a lone technician. Do you try to convince them?"
        )
        if game_state["authority_of_town"] >= 7 and game_state["knowledge"] >= 4:
            print_slow(
                "You quickly explain the situation, backing it up with compelling data. The technician looks shocked, "
                "then determined. 'My God... you're right! I'll help you!'"
            )
            handle_laser_activation() # Directly to laser activation
        else:
            print_slow(
                "You try to explain, but the technician just stares, then presses an alarm button. 'Intruder!'"
            )
            game_state["ending_achieved"] = "Jailed"
    elif choice_num == 3: # Attempt to use a computer terminal.
        print_slow(
            "You find an unsecured computer terminal. Can you access anything useful?"
        )
        if game_state["knowledge"] >= 6 and game_state["tech_parts"] >= 2:
            print_slow(
                "You quickly hack into the system using your technical skills and parts. You gain access to critical missile trajectory data and laser controls!"
            )
            handle_laser_activation() # Directly to laser activation
        else:
            print_slow(
                "The terminal is locked, or your skills aren't enough. You trigger an alert trying to bypass the security."
            )
            game_state["ending_achieved"] = "Jailed"
    elif choice_num == 4: # Give up and try to escape the base.
        handle_escape_base_attempt()
    advance_time(0.5)


def handle_laser_activation():
    # This is a critical point; if triggered, it needs to directly handle the outcome.
    # It still has its own internal input loop because it's a very specific, final choice sequence.
    print_slow("You are in the **Orbital Defense Control Room**. The satellite laser controls are before you.")
    print_slow("The countdown clock blazes: T-minus 5 minutes to impact!")
    print("\nYour options:")
    print("1. Calibrate and fire the laser (requires high knowledge).")
    print("2. Abort the mission, it's too late.")
    choice = input("> ").strip().lower()

    if choice == "1":
        if game_state["knowledge"] >= 7: # Very high knowledge required for precision
            print_slow(
                "With trembling hands, you input the coordinates and arm the laser. "
                "A brilliant beam of light shoots into the sky."
            )
            print_slow(
                "Moments later, a distant explosion lights up the horizon, followed by absolute silence."
            )
            print_slow("The missile is destroyed. You saved them all.")
            game_state["ending_achieved"] = "Missile Destroyed"
        else:
            print_slow("You try to operate the complex controls, but they make no sense. You lack the critical knowledge.")
            print_slow("The countdown hits zero. You failed.")
            game_state["ending_achieved"] = "Time's Up"
    elif choice == "2":
        print_slow("You realize the task is too daunting, or too late. You turn away from the controls.")
        print_slow(
            "The countdown hits zero. The world goes silent, then black."
        )
        game_state["ending_achieved"] = "Time's Up"
    else:
        print_slow("Invalid choice. The clock ticks louder.")
        handle_laser_activation() # Re-prompt for this specific choice until valid


def handle_escape_base_attempt():
    print_slow("You try to sneak out of the military base.")
    if game_state["knowledge"] >= 4 and "backpack" in game_state["inventory"]:
        print_slow(
            "Using your knowledge of the base layout and your cunning, you manage to find a hidden exit."
        )
        game_state["current_location"] = "outskirts_road"
        print_slow("You made it out! But the missile is still a threat, and time is running out to escape.")
    else:
        print_slow("You trigger another alarm. More guards converge on your position.")
        print_slow("There's no escape. You're surrounded.")
        game_state["ending_achieved"] = "Jailed"
    advance_time(0.5)


# --- Inventory Display ---
def display_inventory():
    """Displays the player's current inventory."""
    from utils import colorize_item, print_colored, create_box
    
    clear_screen()
    
    # Create inventory header box
    inventory_box = create_box("🎒 INVENTORY")
    print(inventory_box)
    
    if not game_state["inventory"]:
        print_colored("Your inventory is empty.", "warning")
    else:
        print_colored("You are carrying:", "info")
        for item in game_state["inventory"]:
            print_colored(f"• {colorize_item(item.replace('_', ' ').title())}", "inventory")
    
    # Show resource counters
    print_colored("\n📊 RESOURCE COUNTERS:", "info")
    print_colored(f"🧠 Knowledge: {game_state['knowledge']} (Research & Learning)", "highlight")
    print_colored(f"🔧 Tech Parts: {game_state['tech_parts']} (Electronic Components)", "item")
    print_colored(f"💰 Cash: {game_state['cash']} unit(s) (Currency)", "money")
    
    # Check if player can break down stolen calculator
    if "stolen_calculator" in game_state["inventory"] and game_state["knowledge"] >= 4:
        print_colored("\n🔧 You could break down the stolen calculator for tech parts!", "highlight")
        print_colored("💡 Tip: Knowledge helps you understand how to break down electronics.", "info")
        choice = input("Break down calculator for tech parts? (yes/no): ").strip().lower()
        if choice in ["yes", "y"]:
            print_slow("You carefully disassemble the calculator, salvaging the circuit board and other electronic components.")
            game_state["inventory"].remove("stolen_calculator")
            game_state["tech_parts"] += 1
            print_slow("You gained a **Tech Part** from the calculator!")
            input("Press Enter to continue...")
            advance_time(0.5, silent=True)
    
    print("-" * 30)
    input("Press Enter to continue...")


# --- Ending Functions (called by main_menu_loop when ending_achieved is set) ---
# These functions should ONLY print the narrative.

def display_mushroom_cloud():
    """Displays ASCII mushroom cloud for dramatic effect."""
    mushroom_cloud = """
     _.-^^---....,,--
 _--                  --_
<                        >)
|                         |
 \._                   _./
    ```--. . , ; .--'''
          | |   |
       .-=||  | |=-.
       `-=#######=-'
          | ;  :|
 _____.,-#######~,._____
"""
    print_slow(mushroom_cloud, wrap=False)

def get_contextual_hint():
    """Provides contextual hints based on current game state."""
    hints = []
    
    # Time-based hints
    if game_state["time_remaining"] <= 3:
        hints.append("⏰ Time is running out! Focus on your most important goals.")
    
    # Resource-based hints
    if game_state["knowledge"] < 3:
        hints.append("🧠 Consider attending class or using the computer to gain knowledge.")
    if game_state["tech_parts"] < 1:
        hints.append("🔧 You might need tech parts for advanced actions.")
    if game_state["cash"] < 2:
        hints.append("💰 You could work at Burger Hut or sell items for cash.")
    
    # Trust-based hints
    if game_state["trust_alex"] < 4:  # Back to requiring effort
        hints.append("🔍 Alex might have useful information if you gain his trust.")
    if game_state["trust_maya"] < 5:  # Back to requiring effort
        hints.append("💝 Maya could provide moral support and encouragement.")
    if game_state["trust_ben"] < 4:  # Back to requiring effort
        hints.append("🔧 Ben's practical knowledge could be valuable.")
    if game_state["trust_jake"] < 2:
        hints.append("👊 Jake might help if you show him respect.")
    
    # Location-based hints
    if game_state["current_location"] == "home" and game_state["time_remaining"] > 8:
        hints.append("🏠 You're safe at home, but time is ticking.")
    if game_state["current_location"] == "town_square":
        hints.append("🏛️ The town square connects to many important locations.")
    
    return hints[0] if hints else "💡 Explore different locations and talk to people to discover your options."

def handle_allies_escape_ending():
    print_slow("--- Ending Achieved: Allies Escape ---", color=Fore.RED)
    print_slow(
        "Against all odds, you convinced your friends and family. Together, you boarded the last bus or "
        "sealed yourselves in the bunker.", color=Fore.RED
    )
    print_slow(
        "The world outside might be ending, but you face it with those you love. A new, uncertain future awaits, "
        "but not alone.", color=Fore.RED
    )
    print_slow("This is just the beginning of your struggle for survival, together.", color=Fore.RED)
    print_slow("...", color=Fore.RED)
    display_mushroom_cloud()
    input("\nPress Enter to continue...")

def handle_solo_escape_ending():
    print_slow("--- Ending Achieved: Solo Escape ---", color=Fore.RED)
    print_slow("You made it out. Whether on the last bus or deep within the bunker, you are safe from the initial blast.", color=Fore.RED)
    print_slow(
        "The silence is deafening, punctuated only by the distant rumble. You're alive, but utterly alone. "
        "The weight of survival rests entirely on your shoulders.", color=Fore.RED
    )
    print_slow("This new world is a desolate place, but you have a chance to carve out a new existence.", color=Fore.RED)
    print_slow("...", color=Fore.RED)
    display_mushroom_cloud()
    input("\nPress Enter to continue...")

def handle_town_evacuated_ending():
    print_slow("--- Ending Achieved: Town Evacuated ---", color=Fore.RED)
    print_slow(
        "Through sheer force of will and undeniable evidence, you rallied the town. The Mayor finally acted, "
        "and the buses left just in time.", color=Fore.RED
    )
    print_slow(
        "Chaos gave way to organized departure. The town is empty, but its people are safe, scattered but alive, "
        "thanks to you.", color=Fore.RED
    )
    print_slow(
        "You watch the last bus disappear over the horizon, a bittersweet victory. Your town is gone, but its "
        "spirit lives on through its people.", color=Fore.RED
    )
    print_slow("...", color=Fore.RED)
    display_mushroom_cloud()
    input("\nPress Enter to continue...")

def handle_missile_destroyed_ending():
    # Rainbow effect for the missile destroyed ending
    rainbow = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    lines = [
        "--- Ending Achieved: Missile Destroyed ---",
        "You infiltrated the military base, outwitted the security, and operated the legendary satellite laser. "
        "A blinding flash in the sky confirms your success.",
        "The missile is gone. The threat is averted. The world is safe, oblivious to how close it came to oblivion, "
        "or who saved it.",
        "You stand, exhausted but triumphant, the silent protector of humanity. Your vision was a warning, and you answered it."
    ]
    for i, line in enumerate(lines):
        print_slow(line, color=rainbow[i % len(rainbow)])
    
    # Display the dramatic ASCII art
    victory_art = """
                       d*##*.
 zP******e.           *    *o
4*       *          *      *
*        *        J*       *F
 b        *k       *>       *
  *k        *r     J*       d*
  *         *     *       *~
   *        *   *E       *
    *         *L   *      *F
     *.       4B   *      ******b
     *        *.  **     **      *F
      *       R*  *F     *      *
       *k      ?* u*     dF      .*
       ^*.      **     z*      u****e
        #*b             *E.dW@e*    ?*
         #*           .o**# d****c    ?F
          *      .d**# . zo*>   #*r .uF
          *L .u**      *&***k   .**d**F
           **            ^***P*P9*
          JP              .o****u:*P **
          *          ..ue*      *"
         d*          *F              *
         **     ....udE             4B
          #*    **** *r            @*
           ^*L        *            *F
             RN        4N           *
              *b                  d*
               **k                 *F
               **b                *F
                 **               *F
                 *                *
                  *L               *
                  *               *
                   *               *
"""
    print_slow(victory_art, color=Fore.GREEN)
    input("\nPress Enter to continue...")

# These are specific ending messages that will be called from menus.py
def handle_time_up_ending():
    print_slow("\n--- Ending Achieved: Time's Up ---", color=Fore.RED)
    print_slow("The sky darkens. A distant rumble grows louder, then deafening.", color=Fore.RED)
    print_slow("There's nowhere left to run. The vision was true.", color=Fore.RED)
    print_slow("...", color=Fore.RED)
    display_mushroom_cloud()
    print_slow("The end.", color=Fore.RED)
    input("\nPress Enter to continue...")

def handle_jailed_ending():
    print_slow("\n--- Ending Achieved: Jailed ---", color=Fore.RED)
    print_slow("The cold cell bars are your last sight. Your desperate warnings are met with mockery. You are trapped.", color=Fore.RED)
    print_slow("The distant, growing rumble is all the proof you needed. Your efforts end here, in despair.", color=Fore.RED)
    print_slow("...", color=Fore.RED)
    display_mushroom_cloud()
    print_slow("The end.", color=Fore.RED)
    input("\nPress Enter to continue...")

def handle_truck_escape_ending():
    """Handles the truck escape ending - requires truck keys and sufficient gas."""
    if game_state["time_remaining"] <= 0:
        print_slow("You try to start the truck, but time has run out.")
        return False
        
    if "truck_keys" not in game_state["inventory"]:
        print_slow("You don't have the truck keys. You can't start the vehicle.")
        print_slow("💡 Tip: You need to get the truck keys from Mr. Henderson first.")
        return False
        
    if game_state["car_gas"] < 30:
        print_slow("The truck sputters and dies. There's not enough gas to get out of town.")
        print_slow(f"💡 Tip: You need at least 30% gas to escape. Current gas: {game_state['car_gas']}%")
        return False
    
    print_slow("You turn the key in Mr. Henderson's truck. The engine roars to life!")
    print_slow("With a full tank of gas, you have enough fuel to escape the town.")
    
    # Check if friends are coming along
    if (game_state.get("has_shared_vision_with_friends", False) and
        game_state["trust_alex"] >= 4 and game_state["trust_maya"] >= 4 and game_state["trust_ben"] >= 4):
        print_slow("Your friends pile into the truck with you. Together, you drive away from the doomed town.")
        game_state["ending_achieved"] = "Allies Escape"
    else:
        print_slow("You drive alone, leaving the town behind as you head for safety.")
        game_state["ending_achieved"] = "Solo Escape"
    
    return True

# New alternative buying logic for tech parts
def buy_tech_parts_action():
    """Handle buying tech parts from the tech store."""
    from utils import colorize_money, colorize_item, print_slow_colored
    
    tech_parts_cost = 1 # One cash unit for tech parts
    if game_state["cash"] >= tech_parts_cost:
        game_state["cash"] -= tech_parts_cost
        game_state["tech_parts"] += 1
        game_state["inventory"].append("circuit board")
        print_slow_colored(f"You bought some {colorize_item('**Tech Parts**')} for {colorize_money(f'{tech_parts_cost} cash unit(s)')}!", "success")
        print_slow_colored("🔧 Tech Parts are electronic components needed for advanced technology.", "info")
        advance_time(0.5)
    else:
        cash_amount = f"{game_state['cash']} cash unit(s)"
        cost_amount = f"{tech_parts_cost}"
        print_slow_colored(f"You don't have enough cash for tech parts. You have {colorize_money(cash_amount)}, but need {colorize_money(cost_amount)}.", "warning")
        advance_time(0.1, silent=True)

def handle_steal_school_action():
    has_backpack = "backpack" in game_state["inventory"]
    success_chance = 0.65 if has_backpack else 0.35
    if random.random() < success_chance:
        print_slow("You manage to swipe a calculator from a teacher's desk without being noticed." + (" Your backpack helps you hide it." if has_backpack else ""))
        game_state["inventory"].append("stolen_calculator")
        print_slow("You gained a **Stolen Calculator**!")
        
        # Check if player can break it down for tech parts
        if game_state["knowledge"] >= 4:
            print_slow("You examine the calculator and realize you could break it down for useful electronic components.")
            print_slow("💡 Tip: Your knowledge helps you understand how to break down electronics.")
            choice = input("Break down the calculator for tech parts? (yes/no): ").strip().lower()
            if choice in ["yes", "y"]:
                print_slow("You carefully disassemble the calculator, salvaging the circuit board and other electronic components.")
                game_state["inventory"].remove("stolen_calculator")
                game_state["tech_parts"] += 1
                print_slow("🔧 You gained a Tech Part from the calculator!")
                print_slow("💡 Tip: Tech Parts are electronic components needed for advanced technology.")
            else:
                print_slow("You decide to keep the calculator intact for now.")
    else:
        print_slow("You get caught trying to steal! The principal is called, and soon the police arrive.")
        game_state["ending_achieved"] = "Jailed"
    advance_time(0.5)

def handle_steal_tech_store_action():
    has_backpack = "backpack" in game_state["inventory"]
    success_chance = 0.65 if has_backpack else 0.35
    if random.random() < success_chance:
        print_slow("You slip a tech part into your backpack and walk out, heart pounding." if has_backpack else "You manage to pocket a tech part and walk out, heart pounding.")
        game_state["inventory"].append("stolen_tech_part")
        print_slow("You gained a **Stolen Tech Part**!")
        # Convert stolen tech part to usable tech part
        game_state["tech_parts"] += 1
        game_state["inventory"].remove("stolen_tech_part")
        print_slow("🔧 The stolen tech part is now usable for your technical needs.")
        print_slow("💡 Tip: Tech Parts are electronic components needed for advanced technology.")
    else:
        print_slow("You get caught trying to steal! The store owner calls the police.")
        game_state["ending_achieved"] = "Jailed"
    advance_time(0.5)

def handle_pawn_shop_sell_action():
    """Handles selling stolen items at the pawn shop."""
    from utils import colorize_money, print_slow_colored
    
    sellable = [item for item in game_state["inventory"] if item.startswith("stolen_") or item == "gas_can"]
    if not sellable:
        print_slow("You have nothing the pawn shop wants right now.")
        print_slow("💡 Tip: The pawn shop buys stolen items and gas cans.")
        return
    
    print_slow("Items you can sell:")
    for idx, item in enumerate(sellable, 1):
        print_slow_colored(f"{idx}. {item.replace('_', ' ').title()}", "inventory")
    print_slow_colored(f"{len(sellable)+1}. Cancel", "warning")
    
    choice = input("> ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(sellable):
        item = sellable[int(choice)-1]
        game_state["inventory"].remove(item)
        game_state["cash"] += 1
        print_slow_colored(f"You sell the {item.replace('_', ' ')} for {colorize_money('1 cash unit')}!", "success")
        print_slow("💡 Tip: You can use this cash to buy gas or other supplies.")
    else:
        print_slow("You decide not to sell anything.")
    
    advance_time(0.1, silent=True)


def handle_truck_travel_action(destination):
    """Handles truck travel between locations - faster than walking but uses gas."""
    if "truck_keys" not in game_state["inventory"]:
        print_slow("You don't have the truck keys. You can't drive anywhere.")
        print_slow("💡 Tip: You need to get the truck keys from Mr. Henderson first.")
        return False
        
    if game_state["car_gas"] < 10:
        print_slow("The truck won't start. There's not enough gas for even a short trip.")
        print_slow(f"💡 Tip: You need at least 10% gas to start the truck. Current gas: {game_state['car_gas']}%")
        return False
    
    # Gas cost for travel (varies by distance)
    gas_cost = 5  # Base cost for any trip
    
    if game_state["car_gas"] < gas_cost:
        print_slow(f"You need at least {gas_cost}% gas to drive anywhere.")
        print_slow(f"💡 Tip: Current gas: {game_state['car_gas']}%, Required: {gas_cost}%")
        return False
    
    print_slow("You hop into Mr. Henderson's truck and start the engine.")
    print_slow(f"The drive to {destination.replace('_', ' ').title()} is quick and smooth.")
    
    # Deduct gas and time
    game_state["car_gas"] -= gas_cost
    game_state["current_location"] = destination
    advance_time(0.5, silent=True)  # Much faster than walking (which takes 1-2 hours)
    
    print_slow(f"You arrive at {destination.replace('_', ' ').title()}. Gas remaining: {game_state['car_gas']}%")
    print_slow("⏰ Time saved: Truck travel is much faster than walking!")
    return True

def handle_local_bus_travel():
    """Handles taking the local bus to outskirts."""
    print_slow("You board the local bus that runs around the outskirts of town.")
    print_slow("The ride is short but gives you a good view of the area where Mr. Henderson's truck is usually parked.")
    print_slow("You get off at the outskirts stop, near the main road leading out of town.")
    game_state["current_location"] = "outskirts_road"
    advance_time(0.5)
    input("Press Enter to continue...")

def handle_search_for_car_action():
    """Handles the 'search for car' interaction in outskirts - high time cost way to find Mr. Henderson's truck."""
    print_slow("You spend hours methodically searching the outskirts for any usable vehicles.")
    print_slow("After what feels like forever, you finally spot something - an old, beat-up truck parked behind some overgrown bushes.")
    print_slow("As you get closer, you recognize it as Mr. Henderson's truck. The keys are still in the ignition, as always.")
    
    if not game_state["has_car_keys"]:
        game_state["has_car_keys"] = True
        game_state["inventory"].append("truck_keys")
        print_slow("You got the **Truck Keys**! But the gas tank is almost empty.")
    else:
        print_slow("You're back at Mr. Henderson's truck. The gas tank is still empty.")
    
    # High time cost for finding it without tips
    advance_time(3)  # 3 hours of searching
    input("Press Enter to continue...")
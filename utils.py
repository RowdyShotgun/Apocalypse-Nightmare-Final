"""
utils.py

Utility functions for the text adventure game.
- clear_screen: Clears the console screen.
- print_slow: Prints text character by character for dramatic effect.
- Color utilities for names, locations, and items.
- Box drawing functions for UI elements.
"""
import time
import os
import sys
import re
import platform
from colorama import init, Fore, Back, Style

# Enhanced cross-platform input handling
def setup_input_handling():
    """Setup input handling based on the current platform."""
    global kbhit, getch
    
    system = platform.system().lower()
    
    if system == "windows":
        try:
            import msvcrt
            def kbhit():
                return msvcrt.kbhit()
            def getch():
                return msvcrt.getwch()
        except ImportError:
            # Fallback for Windows without msvcrt
            def kbhit():
                return False
            def getch():
                return None
    elif system in ["linux", "darwin"]:  # Linux or macOS
        try:
            import tty
            import termios
            import select
            
            def kbhit():
                """Check if a key has been pressed (non-blocking)."""
                try:
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(sys.stdin.fileno())
                        dr, dw, de = select.select([sys.stdin], [], [], 0)
                        return dr != []
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                except:
                    return False
            
            def getch():
                """Get a single character (blocking)."""
                try:
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(sys.stdin.fileno())
                        ch = sys.stdin.read(1)
                        return ch
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                except:
                    return None
        except ImportError:
            # Fallback for systems without tty/termios
            def kbhit():
                return False
            def getch():
                return None
    else:
        # Generic fallback for other systems
        def kbhit():
            return False
        def getch():
            return None

# Initialize input handling
setup_input_handling()

# Initialize colorama only once
try:
    init(autoreset=True)
except:
    pass  # Already initialized

# Color scheme for different game elements
COLORS = {
    "location": Fore.CYAN,
    "character": Fore.YELLOW,
    "item": Fore.GREEN,
    "warning": Fore.RED,
    "success": Fore.GREEN,
    "info": Fore.BLUE,
    "highlight": Fore.MAGENTA,
    "time": Fore.RED,
    "money": Fore.YELLOW,
    "inventory": Fore.GREEN,
    "box": Fore.WHITE
}

def clear_screen():
    """Clears the console screen for better readability."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_slow(text, delay=0.03, mode='fast', color=None):
    """Prints text character by character for dramatic effect, with optional color.

    Args:
        text (str): The text to print.
        delay (float): Delay between characters (overridden by mode).
        mode (str): 'fast' or 'slow' for different speeds.
        color: Optional colorama Fore color (e.g., Fore.CYAN).
    """
    if color:
        text = color + text + Style.RESET_ALL
    if mode == 'fast':
        delay = 0.01
    elif mode == 'slow':
        delay = 0.04
    
    # Handle color codes properly by printing them all at once
    if any(code in text for code in ['\x1b[', '[3', '[0']):
        # If text contains color codes, print it all at once to avoid artifacts
        print(text)
        return
    
    i = 0
    length = len(text)
    while i < length:
        sys.stdout.write(text[i])
        sys.stdout.flush()
        time.sleep(delay)
        i += 1
        if kbhit():
            key = getch()
            if key in ('\r', '\n'):
                sys.stdout.write(text[i:])
                sys.stdout.flush()
                break
    print()  # Newline at the end

def colorize_name(name):
    """Adds character color to a name."""
    return f"{COLORS['character']}{name}{Style.RESET_ALL}"

def colorize_location(location):
    """Adds location color to a location name."""
    return f"{COLORS['location']}{location}{Style.RESET_ALL}"

def colorize_item(item):
    """Adds item color to an item name."""
    return f"{COLORS['item']}{item}{Style.RESET_ALL}"

def colorize_money(amount):
    """Adds money color to a cash amount."""
    return f"{COLORS['money']}{amount}{Style.RESET_ALL}"

def colorize_time(time_left):
    """Adds time color to time remaining."""
    return f"{COLORS['time']}{time_left}{Style.RESET_ALL}"

def create_progress_bar(current, maximum, width=20):
    """Creates a visual progress bar."""
    filled = int((current / maximum) * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {current}/{maximum}"

def dramatic_pause(seconds=2):
    """Creates a dramatic pause with dots."""
    for i in range(3):
        print(".", end="", flush=True)
        time.sleep(seconds / 3)
    print()

def strip_ansi(text):
    """Remove ANSI color codes from a string for accurate width calculation."""
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)

def create_box(text, width=None, color=COLORS['box']):
    """Creates a box around text with optional color, handling color codes properly."""
    visible_text = strip_ansi(text)
    if width is None:
        width = len(visible_text) + 4
    
    # Ensure width is at least as wide as the visible text plus padding
    if width < len(visible_text) + 4:
        width = len(visible_text) + 4
    
    # Calculate the actual content width (accounting for color codes)
    content_width = width - 4  # Subtract the box borders and padding
    
    # Ensure content width is at least as wide as the visible text
    if content_width < len(visible_text):
        content_width = len(visible_text)
        width = content_width + 4
    
    # Create the box borders using simple ASCII characters for better compatibility
    top_bottom = "-" * (width - 2)
    
    # Build the box with proper color handling
    box_lines = []
    box_lines.append(f"{color}+{top_bottom}+{Style.RESET_ALL}")
    
    # Center the text properly
    centered_text = text.center(content_width)
    box_lines.append(f"{color}| {centered_text} |{Style.RESET_ALL}")
    
    box_lines.append(f"{color}+{top_bottom}+{Style.RESET_ALL}")
    
    return "\n".join(box_lines)

def create_countdown_box(time_left, phase):
    """Creates a special countdown box with time and phase, handling color codes properly."""
    # Round time to 1 decimal place to avoid long floating point numbers
    rounded_time = round(time_left, 1)
    time_text = f"{rounded_time}h remaining"
    phase_text = f"Phase: {phase.title()}"
    visible_time = strip_ansi(time_text)
    visible_phase = strip_ansi(phase_text)
    
    # Calculate width based on the longest visible text
    max_text_length = max(len(visible_time), len(visible_phase))
    width = max_text_length + 6  # Add padding for borders and spacing
    
    # Calculate the actual content width (accounting for borders and padding)
    content_width = width - 4  # Subtract the box borders and padding
    
    # Ensure content width is at least as wide as the longest text
    if content_width < max_text_length:
        content_width = max_text_length
        width = content_width + 4
    
    top_bottom = "═" * (width - 2)
    box = f"{COLORS['time']}╔{top_bottom}╗{Style.RESET_ALL}\n"
    box += f"{COLORS['time']}║ {time_text.center(content_width)} ║{Style.RESET_ALL}\n"
    box += f"{COLORS['time']}║ {phase_text.center(content_width)} ║{Style.RESET_ALL}\n"
    box += f"{COLORS['time']}╚{top_bottom}╝{Style.RESET_ALL}"
    return box

def print_colored(text, color_type):
    """Prints text with the specified color type."""
    color = COLORS.get(color_type, Fore.WHITE)
    print(f"{color}{text}{Style.RESET_ALL}")

def print_slow_colored(text, color_type, delay=0.03, mode='fast'):
    """Prints text slowly with the specified color type."""
    color = COLORS.get(color_type, Fore.WHITE)
    colored_text = f"{color}{text}{Style.RESET_ALL}"
    print_slow(colored_text, delay, mode)

def validate_numeric_input(prompt, min_val=None, max_val=None, default=None):
    """Validate numeric input with optional range checking and default value."""
    while True:
        try:
            user_input = input(prompt).strip()
            if not user_input and default is not None:
                return default
            value = int(user_input)
            if min_val is not None and value < min_val:
                print_colored(f"Please enter a number at least {min_val}.", "warning")
                continue
            if max_val is not None and value > max_val:
                print_colored(f"Please enter a number no more than {max_val}.", "warning")
                continue
            return value
        except ValueError:
            print_colored("Please enter a valid number.", "warning")

def validate_choice_input(prompt, valid_choices, case_sensitive=False):
    """Validate choice input against a list of valid options."""
    while True:
        user_input = input(prompt).strip()
        if not case_sensitive:
            user_input = user_input.lower()
            valid_choices = [choice.lower() if isinstance(choice, str) else choice for choice in valid_choices]
        
        if user_input in valid_choices:
            return user_input
        else:
            print_colored(f"Please enter one of: {', '.join(valid_choices)}", "warning")

def safe_input(prompt, max_length=100):
    """Safe input function with length validation and sanitization."""
    try:
        user_input = input(prompt).strip()
        if len(user_input) > max_length:
            print_colored(f"Input too long. Please keep it under {max_length} characters.", "warning")
            return safe_input(prompt, max_length)
        return user_input
    except (EOFError, KeyboardInterrupt):
        # Don't show warning for EOF (piped input) - just return empty string
        if isinstance(sys.exc_info()[1], EOFError):
            return ""
        print_colored("\nInput interrupted.", "warning")
        return ""
    except Exception as e:
        print_colored(f"Input error: {e}", "warning")
        return ""
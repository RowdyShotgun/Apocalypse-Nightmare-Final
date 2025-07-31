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

# Global settings
TEXT_WRAPPING_ENABLED = True  # Can be set to False to disable wrapping globally

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

def get_terminal_width():
    """Get the terminal width, with fallback to 80 characters."""
    return 80  # Simple fixed width

def wrap_text(text, width=None, preserve_color=True):
    """Wrap text to specified width, preserving color codes.
    
    Args:
        text (str): Text to wrap
        width (int): Maximum line width (defaults to terminal width)
        preserve_color (bool): Whether to preserve color codes
    
    Returns:
        list: List of wrapped lines
    """
    try:
        if width is None:
            width = get_terminal_width()
        
        # Ensure width is reasonable
        if width < 20:
            width = 80
        
        # If text is shorter than width, return as single line
        visible_text = strip_ansi(text)
        if len(visible_text) <= width:
            return [text]
    except Exception as e:
        # If wrapping fails, return the original text as a single line
        return [text]
    
    if not preserve_color:
        # Simple word wrapping without color preservation
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            if current_length + word_length + len(current_line) <= width:
                current_line.append(word)
                current_length += word_length
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = word_length
                else:
                    # Word is too long, force break it
                    lines.append(word[:width])
                    current_line = [word[width:]] if len(word) > width else []
                    current_length = len(word[width:]) if len(word) > width else 0
        
        if current_line:
            lines.append(' '.join(current_line))
        return lines
    
    else:
        # Complex wrapping that preserves color codes
        lines = []
        current_line = ""
        current_visible_length = 0
        i = 0
        
        while i < len(text):
            char = text[i]
            
            # Handle color codes
            if char == '\x1b' and i + 1 < len(text) and text[i + 1] == '[':
                # Find the end of the color code
                color_end = text.find('m', i)
                if color_end != -1:
                    color_code = text[i:color_end + 1]
                    current_line += color_code
                    i = color_end + 1
                    continue
            
            # Handle regular characters
            if current_visible_length >= width:
                # Find the last space in the current line
                last_space = current_line.rfind(' ')
                if last_space > 0 and current_visible_length > width * 0.7:
                    # Break at word boundary
                    lines.append(current_line[:last_space])
                    current_line = current_line[last_space + 1:] + char
                    current_visible_length = len(strip_ansi(current_line))
                else:
                    # Force break
                    lines.append(current_line)
                    current_line = char
                    current_visible_length = 1
            else:
                current_line += char
                current_visible_length = len(strip_ansi(current_line))
            
            i += 1
        
        if current_line:
            lines.append(current_line)
        
        return lines

def print_slow(text, delay=0.03, mode='fast', color=None, wrap=True, width=None):
    """Prints text character by character for dramatic effect, with optional color and wrapping.

    Args:
        text (str): The text to print.
        delay (float): Delay between characters (overridden by mode).
        mode (str): 'fast' or 'slow' for different speeds.
        color: Optional colorama Fore color (e.g., Fore.CYAN).
        wrap (bool): Whether to wrap text to terminal width.
        width (int): Custom width for wrapping (defaults to terminal width).
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
        if wrap:
            wrapped_lines = wrap_text(text, width)
            for line in wrapped_lines:
                print(line)
        else:
            print(text)
        return
    
    # Wrap text if requested and globally enabled
    if wrap and TEXT_WRAPPING_ENABLED:
        try:
            wrapped_lines = wrap_text(text, width)
            for line in wrapped_lines:
                i = 0
                length = len(line)
                while i < length:
                    sys.stdout.write(line[i])
                    sys.stdout.flush()
                    time.sleep(delay)
                    i += 1
                    if kbhit():
                        key = getch()
                        if key in ('\r', '\n'):
                            sys.stdout.write(line[i:])
                            sys.stdout.flush()
                            break
                print()  # Newline after each wrapped line
        except Exception as e:
            # If wrapping fails, fall back to original behavior
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
    else:
        # Original behavior without wrapping
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
    # Strip color codes to get actual text length
    visible_text = strip_ansi(text)
    
    # Calculate box width
    if width is None:
        width = len(visible_text) + 4
    
    # Ensure minimum width
    if width < len(visible_text) + 4:
        width = len(visible_text) + 4
    
    # Create the box borders
    top_bottom = "-" * (width - 2)
    
    # Build the box
    box_lines = []
    box_lines.append(f"{color}+{top_bottom}+{Style.RESET_ALL}")
    
    # Center the text within the box
    padding = width - len(visible_text) - 2  # Account for borders
    left_padding = padding // 2
    right_padding = padding - left_padding
    
    box_lines.append(f"{color}|{' ' * left_padding}{text}{' ' * right_padding}|{Style.RESET_ALL}")
    box_lines.append(f"{color}+{top_bottom}+{Style.RESET_ALL}")
    
    return "\n".join(box_lines)

def create_countdown_box(time_left, phase):
    """Creates a special countdown box with time and phase."""
    # Round time to 1 decimal place to avoid long floating point numbers
    rounded_time = round(time_left, 1)
    time_text = f"{rounded_time}h remaining"
    phase_text = f"Phase: {phase.title()}"
    
    # Calculate width based on the longest text
    max_text_length = max(len(time_text), len(phase_text))
    width = max_text_length + 4  # Add padding for borders
    
    # Create the box
    top_bottom = "═" * (width - 2)
    box = f"{COLORS['time']}╔{top_bottom}╗{Style.RESET_ALL}\n"
    
    # Center each line
    time_padding = width - len(time_text) - 2
    time_left_pad = time_padding // 2
    time_right_pad = time_padding - time_left_pad
    
    phase_padding = width - len(phase_text) - 2
    phase_left_pad = phase_padding // 2
    phase_right_pad = phase_padding - phase_left_pad
    
    box += f"{COLORS['time']}║{' ' * time_left_pad}{time_text}{' ' * time_right_pad}║{Style.RESET_ALL}\n"
    box += f"{COLORS['time']}║{' ' * phase_left_pad}{phase_text}{' ' * phase_right_pad}║{Style.RESET_ALL}\n"
    box += f"{COLORS['time']}╚{top_bottom}╝{Style.RESET_ALL}"
    
    return box

def print_colored(text, color_type):
    """Prints text with the specified color type."""
    color = COLORS.get(color_type, Fore.WHITE)
    print(f"{color}{text}{Style.RESET_ALL}")

def print_slow_colored(text, color_type, delay=0.03, mode='fast', wrap=True, width=None):
    """Prints text slowly with the specified color type and optional wrapping."""
    color = COLORS.get(color_type, Fore.WHITE)
    colored_text = f"{color}{text}{Style.RESET_ALL}"
    print_slow(colored_text, delay, mode, wrap=wrap, width=width)

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
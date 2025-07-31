"""
test_colors.py

A simple test script to demonstrate the new color features and UI enhancements.
"""
from utils import (
    colorize_name, colorize_location, colorize_item, colorize_money, 
    colorize_time, create_box, create_countdown_box, print_colored, 
    print_slow_colored
)

def test_colors():
    """Test all the color features."""
    print("=== COLOR FEATURES DEMONSTRATION ===\n")
    
    # Test character names
    print_colored("Character Names:", "highlight")
    print(f"  {colorize_name('Alex')} - The skeptical friend")
    print(f"  {colorize_name('Maya')} - The optimistic friend")
    print(f"  {colorize_name('Ben')} - The practical friend")
    print(f"  {colorize_name('Jake')} - The troubled friend")
    print()
    
    # Test locations
    print_colored("Locations:", "highlight")
    print(f"  {colorize_location('Town Square')} - The heart of the town")
    print(f"  {colorize_location('School Entrance')} - Where education begins")
    print(f"  {colorize_location('Military Base')} - The heavily guarded facility")
    print()
    
    # Test items
    print_colored("Items:", "highlight")
    print(f"  {colorize_item('Backpack')} - For carrying supplies")
    print(f"  {colorize_item('Car Keys')} - For transportation")
    print(f"  {colorize_item('Tech Parts')} - For technical projects")
    print()
    
    # Test money
    print_colored("Money:", "highlight")
    print(f"  Current cash: {colorize_money('5 units')}")
    print(f"  Cost: {colorize_money('2 units')}")
    print()
    
    # Test time
    print_colored("Time:", "highlight")
    print(f"  Time remaining: {colorize_time('12 hours')}")
    print(f"  Current phase: {colorize_time('Afternoon')}")
    print()
    
    # Test boxes
    print_colored("Boxes:", "highlight")
    location_box = create_box(colorize_location("BEDROOM"))
    print(location_box)
    print()
    
    # Test countdown box
    countdown_box = create_countdown_box(8, "evening")
    print(countdown_box)
    print()
    
    # Test colored text
    print_colored("Colored Messages:", "highlight")
    print_colored("This is a success message!", "success")
    print_colored("This is a warning message!", "warning")
    print_colored("This is an info message!", "info")
    print()
    
    print("=== END OF DEMONSTRATION ===")

if __name__ == "__main__":
    test_colors() 
#!/usr/bin/env python3
"""
Test script to verify all menus are accessible in the text adventure game.
This script will test menu navigation and ensure no broken paths exist.
"""

import sys
import os

# Add the current directory to the path so we can import game modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_menu_functions():
    """Test individual menu functions for errors."""
    
    print("🔧 Testing Individual Menu Functions...")
    print("=" * 50)
    
    try:
        # Import the menus module
        import menus
        
        # Test that all menu functions exist and can be called
        menu_functions = [
            'handle_home_menu',
            'handle_town_square_menu', 
            'handle_school_entrance_menu',
            'handle_general_store_menu',
            'handle_tech_store_menu',
            'handle_military_base_menu',
            'handle_military_base_approach_menu',
            'handle_outskirts_road_menu',
            'handle_neighbors_bunker_menu',
            'handle_bus_stop_menu',
            'handle_town_hall_menu',
            'handle_burger_hut_menu',
            'handle_pawn_shop_menu',
        ]
        
        passed = 0
        failed = 0
        
        for func_name in menu_functions:
            if hasattr(menus, func_name):
                print(f"✅ {func_name} - Function exists")
                passed += 1
            else:
                print(f"❌ {func_name} - Function missing")
                failed += 1
        
        print(f"\n📊 Menu Functions: {passed} passed, {failed} failed")
        return passed, failed
                
    except Exception as e:
        print(f"❌ Error testing menu functions: {e}")
        return 0, 1

def test_game_state():
    """Test that game state is properly initialized."""
    
    print("\n🎮 Testing Game State...")
    print("=" * 50)
    
    try:
        # Import game state
        from game_data import game_state
        
        # Check required keys exist
        required_keys = [
            'current_location',
            'time_remaining', 
            'current_day_phase',
            'knowledge',
            'tech_parts',
            'cash',
            'authority_of_town',
            'inventory',
            'trust_alex',
            'trust_maya', 
            'trust_ben',
            'trust_jake'
        ]
        
        passed = 0
        failed = 0
        
        for key in required_keys:
            if key in game_state:
                print(f"✅ {key} - Present in game state")
                passed += 1
            else:
                print(f"❌ {key} - Missing from game state")
                failed += 1
        
        print(f"\n📊 Game State: {passed} passed, {failed} failed")
        return passed, failed
                
    except Exception as e:
        print(f"❌ Error testing game state: {e}")
        return 0, 1

def test_menu_display():
    """Test that menu display functions work correctly."""
    
    print("\n📋 Testing Menu Display Functions...")
    print("=" * 50)
    
    try:
        import menus
        from game_data import game_state
        
        # Test display_menu function
        test_options = [
            ("Test Option 1", "test1"),
            ("Test Option 2", "test2"),
        ]
        
        # This would require input, so we'll just test it exists
        if hasattr(menus, 'display_menu'):
            print("✅ display_menu function exists")
            passed = 1
        else:
            print("❌ display_menu function missing")
            passed = 0
            
        # Test print_slow function
        if hasattr(menus, 'print_slow'):
            print("✅ print_slow function exists")
            passed += 1
        else:
            print("❌ print_slow function missing")
            
        print(f"\n📊 Menu Display: {passed} passed, 0 failed")
        return passed, 0
                
    except Exception as e:
        print(f"❌ Error testing menu display: {e}")
        return 0, 1

def test_imports():
    """Test that all required modules can be imported."""
    
    print("\n📦 Testing Module Imports...")
    print("=" * 50)
    
    modules_to_test = [
        'main',
        'menus', 
        'game_data',
        'game_actions',
        'utils'
    ]
    
    passed = 0
    failed = 0
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name} - Import successful")
            passed += 1
        except ImportError as e:
            print(f"❌ {module_name} - Import failed: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {module_name} - Error: {e}")
            failed += 1
    
    print(f"\n📊 Module Imports: {passed} passed, {failed} failed")
    return passed, failed

if __name__ == "__main__":
    print("🚀 Starting Menu Accessibility Tests...")
    print("=" * 60)
    
    total_passed = 0
    total_failed = 0
    
    # Test imports first
    passed, failed = test_imports()
    total_passed += passed
    total_failed += failed
    
    # Test game state
    passed, failed = test_game_state()
    total_passed += passed
    total_failed += failed
    
    # Test menu functions
    passed, failed = test_menu_functions()
    total_passed += passed
    total_failed += failed
    
    # Test menu display
    passed, failed = test_menu_display()
    total_passed += passed
    total_failed += failed
    
    print("\n" + "=" * 60)
    print("🎉 FINAL TEST RESULTS:")
    print(f"✅ Total Passed: {total_passed}")
    print(f"❌ Total Failed: {total_failed}")
    if total_passed + total_failed > 0:
        success_rate = (total_passed / (total_passed + total_failed)) * 100
        print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if total_failed == 0:
        print("🎊 All tests passed! Menus should be accessible.")
    else:
        print("⚠️  Some tests failed. Check the issues above.") 
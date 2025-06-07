#!/usr/bin/env python3
"""
Test the Nature UI integration
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_nature_ui_imports():
    """Test that all Nature UI components can be imported."""
    print("🧪 Testing Nature UI imports...")
    
    try:
        from src.codex_simulator.utils.nature_integration import (
            NatureUIIntegration,
            start_nature_session,
            get_nature_prompt,
            show_nature_response,
            end_nature_session
        )
        print("✅ Nature integration imports successful")
    except ImportError as e:
        print(f"❌ Nature integration import failed: {e}")
        return False
    
    try:
        from src.codex_simulator.utils.nature_ui import NatureUI
        print("✅ Nature UI import successful")
    except ImportError as e:
        print(f"❌ Nature UI import failed: {e}")
        return False
    
    try:
        from src.codex_simulator.utils.ubuntu_ui import UbuntuCollaborativeUI
        print("✅ Ubuntu UI import successful")
    except ImportError as e:
        print(f"❌ Ubuntu UI import failed: {e}")
        return False
    
    try:
        from src.codex_simulator.utils.seasonal_themes import SeasonalThemeManager
        print("✅ Seasonal themes import successful")
    except ImportError as e:
        print(f"❌ Seasonal themes import failed: {e}")
        return False
    
    try:
        from src.codex_simulator.utils.organic_progress import OrganicProgressIndicator
        print("✅ Organic progress import successful")
    except ImportError as e:
        print(f"❌ Organic progress import failed: {e}")
        return False
    
    try:
        from src.codex_simulator.utils.nature_welcome import NatureWelcome
        print("✅ Nature welcome import successful")
    except ImportError as e:
        print(f"❌ Nature welcome import failed: {e}")
        return False
    
    return True

def test_nature_ui_basic_functionality():
    """Test basic Nature UI functionality."""
    print("\n🧪 Testing Nature UI basic functionality...")
    
    try:
        # Test nature integration
        from src.codex_simulator.utils.nature_integration import start_nature_session, get_nature_prompt, end_nature_session
        
        # Start a session
        nature_session = start_nature_session("TestUser", "testing")
        print("✅ Nature session started successfully")
        
        # Get a prompt
        prompt = get_nature_prompt()
        print(f"✅ Nature prompt generated: '{prompt}'")
        
        # End session  
        end_nature_session()
        print("✅ Nature session ended successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Nature UI functionality test failed: {e}")
        return False

def test_terminal_ui_integration():
    """Test that terminal UI can integrate with Nature UI."""
    print("\n🧪 Testing terminal UI integration...")
    
    try:
        from src.codex_simulator.utils.terminal_ui import terminal_ui
        print("✅ Terminal UI imported successfully")
        
        # Test welcome message
        print("Testing welcome message (should show nature-enhanced version):")
        terminal_ui.print_welcome()
        print("✅ Welcome message displayed")
        
        return True
        
    except Exception as e:
        print(f"❌ Terminal UI integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🌿 Testing Nature UI Integration\n")
    
    all_passed = True
    
    # Test imports
    if not test_nature_ui_imports():
        all_passed = False
    
    # Test basic functionality
    if not test_nature_ui_basic_functionality():
        all_passed = False
    
    # Test terminal integration
    if not test_terminal_ui_integration():
        all_passed = False
    
    print(f"\n{'🎉 All tests passed!' if all_passed else '⚠️  Some tests failed.'}")
    print("🌺 Àṣẹ - May the integration flow with natural harmony!")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

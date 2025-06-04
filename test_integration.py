#!/usr/bin/env python3
"""
Integration test for the new tools in CodexSimulator.
"""

import os
import sys
import tempfile
import csv
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_csv_reader_tool():
    """Test the CSV Reader Tool functionality."""
    print("Testing CSV Reader Tool...")
    
    try:
        from codex_simulator.tools.csv_reader_tool import CSVReaderTool
        
        # Create a temporary CSV file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Age', 'City'])
            writer.writerow(['Alice', '30', 'New York'])
            writer.writerow(['Bob', '25', 'London'])
            writer.writerow(['Charlie', '35', 'Paris'])
            temp_csv_path = f.name
        
        # Test the tool
        csv_tool = CSVReaderTool()
        result = csv_tool._run(temp_csv_path)
        
        print("✅ CSV Reader Tool test passed")
        print(f"Result preview: {result[:200]}...")
        
        # Cleanup
        os.unlink(temp_csv_path)
        
        return True
        
    except Exception as e:
        print(f"❌ CSV Reader Tool test failed: {e}")
        return False

def test_other_tools():
    """Test other new tools."""
    print("Testing other new tools...")
    
    try:
        from codex_simulator.tools.balance_monitor_tool import BalanceMonitorTool
        from codex_simulator.tools.software_architect_tool import SoftwareArchitectTool
        from codex_simulator.tools.systems_thinking_tool import SystemsThinkingTool
        
        # Just test instantiation
        balance_tool = BalanceMonitorTool()
        architect_tool = SoftwareArchitectTool()
        systems_tool = SystemsThinkingTool()
        
        print("✅ Other tools instantiation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Other tools test failed: {e}")
        return False

def test_crew_integration():
    """Test that the crew can be created with new agents."""
    print("Testing crew integration...")
    
    try:
        from codex_simulator.crew import CodexSimulator
        
        # Create simulator instance
        simulator = CodexSimulator()
        
        # Test that new agents can be created
        csv_agent = simulator.csv_data_analyst()
        balance_agent = simulator.balance_monitor()
        architect_agent = simulator.software_architect()
        systems_agent = simulator.systems_thinker()
        
        print("✅ Crew integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Crew integration test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🧪 Running CodexSimulator Integration Tests")
    print("=" * 50)
    
    tests = [
        test_csv_reader_tool,
        test_other_tools,
        test_crew_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Integration is successful.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

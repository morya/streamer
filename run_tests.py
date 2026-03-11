#!/usr/bin/env python3
"""
Test runner script for Screen Streaming Tool.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def run_unit_tests() -> bool:
    """Run unit tests.
    
    Returns:
        True if all tests pass, False otherwise
    """
    print("=" * 60)
    print("Running unit tests...")
    print("=" * 60)
    
    test_dir = Path("src/tests")
    if not test_dir.exists():
        print(f"Test directory not found: {test_dir}")
        return False
        
    # Find all test files
    test_files = list(test_dir.glob("test_*.py"))
    if not test_files:
        print("No test files found")
        return False
        
    print(f"Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"  - {test_file.name}")
        
    # Run tests
    all_passed = True
    for test_file in test_files:
        print(f"\nRunning {test_file.name}...")
        
        try:
            result = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✅ {test_file.name} passed")
            else:
                print(f"❌ {test_file.name} failed")
                print(f"Error output:\n{result.stderr}")
                all_passed = False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_file.name} timed out")
            all_passed = False
        except Exception as e:
            print(f"⚠️  {test_file.name} error: {e}")
            all_passed = False
            
    return all_passed


def run_integration_tests() -> bool:
    """Run integration tests.
    
    Returns:
        True if integration tests pass, False otherwise
    """
    print("\n" + "=" * 60)
    print("Running integration tests...")
    print("=" * 60)
    
    # Check if main application can be imported
    print("Testing module imports...")
    
    modules_to_test = [
        "src.main",
        "src.ui.main_window",
        "src.core.capture",
        "src.core.encoder",
        "src.core.streamer",
        "src.config.manager",
        "src.config.schema",
        "src.controller",
    ]
    
    all_imported = True
    for module_path in modules_to_test:
        try:
            __import__(module_path)
            print(f"✅ {module_path} imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import {module_path}: {e}")
            all_imported = False
        except Exception as e:
            print(f"⚠️  Error importing {module_path}: {e}")
            all_imported = False
            
    return all_imported


def check_dependencies() -> bool:
    """Check if all dependencies are available.
    
    Returns:
        True if all dependencies are available, False otherwise
    """
    print("\n" + "=" * 60)
    print("Checking dependencies...")
    print("=" * 60)
    
    dependencies = [
        "PySide6",
        "dxcam",
        "vidgear",
        "numpy",
        "cv2",
        "appdirs",
    ]
    
    all_available = True
    for dep in dependencies:
        try:
            if dep == "cv2":
                import cv2
            else:
                __import__(dep)
            print(f"✅ {dep} available")
        except ImportError:
            print(f"❌ {dep} not installed")
            all_available = False
            
    return all_available


def check_project_structure() -> bool:
    """Check project structure.
    
    Returns:
        True if project structure is correct, False otherwise
    """
    print("\n" + "=" * 60)
    print("Checking project structure...")
    print("=" * 60)
    
    required_dirs = [
        "src",
        "src/ui",
        "src/core",
        "src/config",
        "src/tests",
        "src/installer",
        "docs",
    ]
    
    required_files = [
        "src/main.py",
        "src/ui/main_window.py",
        "src/ui/overlay_window.py",
        "src/core/capture.py",
        "src/core/encoder.py",
        "src/core/streamer.py",
        "src/config/manager.py",
        "src/config/models.py",
        "src/controller.py",
        "requirements.txt",
        "README.md",
        "AGENTS.md",
    ]
    
    all_present = True
    
    # Check directories
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ Directory: {dir_path}")
        else:
            print(f"❌ Missing directory: {dir_path}")
            all_present = False
            
    # Check files
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ File: {file_path}")
        else:
            print(f"❌ Missing file: {file_path}")
            all_present = False
            
    return all_present


def generate_test_report() -> None:
    """Generate test report."""
    print("\n" + "=" * 60)
    print("Generating test report...")
    print("=" * 60)
    
    report = {
        "unit_tests": run_unit_tests(),
        "integration_tests": run_integration_tests(),
        "dependencies": check_dependencies(),
        "project_structure": check_project_structure(),
    }
    
    print("\n" + "=" * 60)
    print("TEST REPORT SUMMARY")
    print("=" * 60)
    
    for test_name, result in report.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title():20} {status}")
        
    all_passed = all(report.values())
    
    if all_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
        
    return all_passed


def main() -> None:
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run tests for Screen Streaming Tool")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--deps", action="store_true", help="Check dependencies only")
    parser.add_argument("--structure", action="store_true", help="Check project structure only")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    
    args = parser.parse_args()
    
    # Default to running all tests if no specific option is provided
    if not any([args.unit, args.integration, args.deps, args.structure, args.all]):
        args.all = True
        
    print("Screen Streaming Tool - Test Runner")
    print("=" * 60)
    
    if args.unit or args.all:
        run_unit_tests()
        
    if args.integration or args.all:
        run_integration_tests()
        
    if args.deps or args.all:
        check_dependencies()
        
    if args.structure or args.all:
        check_project_structure()
        
    if args.all:
        generate_test_report()


if __name__ == "__main__":
    main()
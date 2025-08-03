#!/usr/bin/env python3
"""Script to run all tests including those in implementation folders."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} - PASSED")
        if result.stdout:
            print("STDOUT:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main() -> int:
    """Run all test suites."""
    root_dir = Path(__file__).parent.parent
    
    # List of test commands to run
    test_commands = [
        # Main tests folder unit tests
        (["uv", "run", "pytest", "tests/", "-m", "unit", "-v"], "Main unit tests"),
        
        # Implementation-specific tests (run from their directories)
        (["uv", "run", "pytest", "src/gmail_client_impl/tests/", "-v"], "Gmail Client Implementation tests"),
        (["uv", "run", "pytest", "src/gmail_message_impl/tests/", "-v"], "Gmail Message Implementation tests"),
        (["uv", "run", "pytest", "src/mail_client_api/tests/", "-v"], "Mail Client API tests"),
        (["uv", "run", "pytest", "src/message/tests/", "-v"], "Message API tests"),
        
        # Integration tests (allow to fail if no credentials)
        (["uv", "run", "pytest", "tests/", "-m", "integration", "-v"], "Integration tests"),
        
        # E2E tests (allow to fail if no credentials)
        (["uv", "run", "pytest", "tests/", "-m", "e2e", "-v"], "E2E tests"),
    ]
    
    # Change to project root
    original_cwd = Path.cwd()
    try:
        Path.chdir(root_dir)
        
        all_passed = True
        critical_failures = 0
        
        for cmd, description in test_commands:
            success = run_command(cmd, description)
            if not success:
                # Integration and E2E tests are allowed to fail
                if "integration" in description.lower() or "e2e" in description.lower():
                    print(f"⚠️  {description} failed (expected if no credentials)")
                else:
                    all_passed = False
                    critical_failures += 1
            print("-" * 50)
        
        # Run coverage report
        print("Generating coverage report...")
        coverage_cmd = ["uv", "run", "pytest", "tests/", "-m", "unit", 
                       "--cov=src", "--cov-report=term", "--cov-fail-under=55"]
        
        coverage_success = run_command(coverage_cmd, "Coverage report")
        if not coverage_success:
            all_passed = False
            critical_failures += 1
        
        if all_passed:
            print("🎉 All critical tests passed!")
            return 0
        else:
            print(f"💥 {critical_failures} critical test suite(s) failed")
            return 1
            
    finally:
        Path.chdir(original_cwd)


if __name__ == "__main__":
    sys.exit(main())
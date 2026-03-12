"""Verification script for Phase 2 agent implementations.

This script verifies that all agents are properly structured and
can be imported without errors. It does NOT test actual execution
(which would require Azure OpenAI and Bing API credentials).
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def verify_imports():
    """Verify all agent modules can be imported."""
    print("Verifying agent imports...")

    try:
        from src.agents import (
            create_event_agent,
            create_general_agent,
            create_poi_agent,
            create_weather_agent,
            find_events,
            find_points_of_interest,
            get_weather_forecast,
            recommend_destinations,
        )
        from src.agents.tools import search_web

        print("✓ All agent modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def verify_prompts():
    """Verify all system prompts exist."""
    print("\nVerifying system prompts...")

    prompts_dir = Path(__file__).parent.parent / "data" / "prompts"
    expected_prompts = [
        "general-agent/system.md",
        "poi-agent/system.md",
        "event-agent/system.md",
        "weather-agent/system.md",
    ]

    all_exist = True
    for prompt_path in expected_prompts:
        full_path = prompts_dir / prompt_path
        if full_path.exists():
            print(f"✓ {prompt_path}")
        else:
            print(f"✗ {prompt_path} NOT FOUND")
            all_exist = False

    return all_exist


def verify_structure():
    """Verify directory structure."""
    print("\nVerifying directory structure...")

    project_root = Path(__file__).parent.parent
    expected_dirs = [
        "src/agents",
        "src/agents/tools",
        "data/prompts/general-agent",
        "data/prompts/poi-agent",
        "data/prompts/event-agent",
        "data/prompts/weather-agent",
    ]

    all_exist = True
    for dir_path in expected_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"✓ {dir_path}")
        else:
            print(f"✗ {dir_path} NOT FOUND")
            all_exist = False

    return all_exist


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Phase 2 Agent Layer Verification")
    print("=" * 60)

    results = []
    results.append(("Structure", verify_structure()))
    results.append(("Prompts", verify_prompts()))
    results.append(("Imports", verify_imports()))

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n✓ All verification checks passed!")
        print(
            "\nNote: This verifies structure only. Actual agent "
            "execution requires:"
        )
        print("  - AZURE_OPENAI_ENDPOINT")
        print("  - AZURE_OPENAI_API_KEY")
        print("  - AZURE_OPENAI_DEPLOYMENT")
        print("  - BING_SEARCH_API_KEY")
        print("  - BING_SEARCH_ENDPOINT")
        return 0
    else:
        print("\n✗ Some verification checks failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())

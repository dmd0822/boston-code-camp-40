"""Phase 3 verification — orchestrator wiring smoke test.

Tests the orchestrator structure without requiring real Azure
credentials by verifying the wiring is correct.
"""

import asyncio
import sys
from datetime import date
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.api.models.customer import CustomerProfile, TravelDates
from src.config.settings import Settings
from src.orchestrator.travel_orchestrator import (
    TravelOrchestrator,
)


def main() -> None:
    """Run structure verification checks."""
    print("Phase 3 Orchestrator Verification")
    print("=" * 50)

    # Test 1: Orchestrator initialization
    print("\n[1/3] Testing orchestrator initialization...")
    settings = Settings()
    orchestrator = TravelOrchestrator(settings)
    assert orchestrator.settings == settings
    print("✓ Orchestrator initialized with Settings")

    # Test 2: Profile structure
    print("\n[2/3] Testing profile structure...")
    profile = CustomerProfile(
        departure_city="Boston",
        interests=["history", "food"],
        travel_dates=TravelDates(
            start=date(2026, 6, 1), end=date(2026, 6, 15)
        ),
        budget="moderate",
        party_size=2,
    )
    print(f"✓ Valid profile created: {profile.departure_city}")

    # Test 3: Orchestrator callable (structure test, not e2e)
    print("\n[3/3] Testing orchestrator is async callable...")
    assert asyncio.iscoroutinefunction(
        orchestrator.generate_itinerary
    )
    print("✓ generate_itinerary is async and callable")

    # Note: Full e2e test requires Azure credentials
    # and is handled in integration tests
    print("\n" + "=" * 50)
    print("✅ Phase 3 structure verification passed!")
    print("\nNote: Full e2e testing requires Azure credentials")
    print("and should be performed via integration tests.")


if __name__ == "__main__":
    main()

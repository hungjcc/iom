#!/usr/bin/env python3
"""Create a simple item+auction record for testing."""

from __future__ import annotations

from datetime import datetime, timedelta

from db import create_item_and_auction


if __name__ == "__main__":
    auction_id, item_id = create_item_and_auction(
        title="TEST AUCTION",
        description="Manual test",
        seller_id=None,
        starting_price=1.0,
        end_date=datetime.utcnow() + timedelta(days=7),
        duration=7,
        status='A'
    )
    print(f"Created item {item_id} with auction {auction_id}")

import pytest
from fastapi.testclient import TestClient
from unittest.mock import create_autospec

from app.main import app
from app.domain.interfaces import PriceRepository, DeribitPriceClient
from app.application.services import PriceTrackingService
from app.domain.entities import PriceRecord
from decimal import Decimal


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def mock_price_repository():
    return create_autospec(PriceRepository, instance=True)


@pytest.fixture
def mock_deribit_client():
    return create_autospec(DeribitPriceClient, instance=True)


@pytest.fixture
def price_tracking_service(mock_deribit_client, mock_price_repository):
    return PriceTrackingService(mock_deribit_client, mock_price_repository)


@pytest.fixture
def sample_price_record():
    return PriceRecord(
        id=1,
        ticker="btc_usd",
        price=Decimal("50000.50"),
        timestamp=1700000000,
        created_at=None
    )

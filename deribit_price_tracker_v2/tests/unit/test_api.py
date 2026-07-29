import pytest
from unittest.mock import Mock, patch
from decimal import Decimal

from app.domain.entities import PriceRecord


class TestPricesApi:
    def test_get_all_prices(self, test_client):
        mock_record = PriceRecord(
            id=1, ticker="btc_usd", price=Decimal("50000.50"),
            timestamp=1700000000, created_at=None
        )

        with patch("app.presentation.dependencies.get_price_service") as mock_get_service:
            mock_service = Mock()
            mock_service.get_all_records.return_value = [mock_record]
            mock_get_service.return_value = mock_service

            response = test_client.get("/prices/all?ticker=btc_usd")

            assert response.status_code == 200
            data = response.json()
            assert data["ticker"] == "btc_usd"
            assert data["count"] == 1
            assert data["data"][0]["price"] == "50000.50"

    def test_get_last_price_success(self, test_client):
        mock_record = PriceRecord(
            id=1, ticker="btc_usd", price=Decimal("50000.50"),
            timestamp=1700000000, created_at=None
        )

        with patch("app.presentation.dependencies.get_price_service") as mock_get_service:
            mock_service = Mock()
            mock_service.get_last_record.return_value = mock_record
            mock_get_service.return_value = mock_service

            response = test_client.get("/prices/last?ticker=btc_usd")

            assert response.status_code == 200
            assert response.json()["ticker"] == "btc_usd"

    def test_get_last_price_not_found(self, test_client):
        with patch("app.presentation.dependencies.get_price_service") as mock_get_service:
            mock_service = Mock()
            mock_service.get_last_record.return_value = None
            mock_get_service.return_value = mock_service

            response = test_client.get("/prices/last?ticker=xxx_usd")

            assert response.status_code == 404

    def test_get_prices_with_filter(self, test_client):
        mock_record = PriceRecord(
            id=1, ticker="btc_usd", price=Decimal("50000.50"),
            timestamp=1700001000, created_at=None
        )

        with patch("app.presentation.dependencies.get_price_service") as mock_get_service:
            mock_service = Mock()
            mock_service.get_filtered_records.return_value = [mock_record]
            mock_get_service.return_value = mock_service

            response = test_client.get(
                "/prices/filter?ticker=btc_usd&start_date=1700000000&end_date=1700003600"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 1

    def test_missing_ticker_parameter(self, test_client):
        response = test_client.get("/prices/all")
        assert response.status_code == 422

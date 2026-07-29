import pytest
from decimal import Decimal
from unittest.mock import Mock

from app.domain.entities import PriceRecord
from app.application.services import PriceTrackingService


class TestPriceTrackingService:
    def test_fetch_and_save_success(
        self, price_tracking_service, mock_deribit_client,
        mock_price_repository, sample_price_record
    ):
        mock_deribit_client.get_index_price.return_value = Decimal("50000.50")
        mock_price_repository.save.return_value = sample_price_record

        result = price_tracking_service.fetch_and_save("btc_usd")

        assert result == sample_price_record
        mock_deribit_client.get_index_price.assert_called_once_with("btc_usd")
        mock_price_repository.save.assert_called_once()

    def test_fetch_and_save_when_api_returns_none(
        self, price_tracking_service, mock_deribit_client
    ):
        mock_deribit_client.get_index_price.return_value = None

        result = price_tracking_service.fetch_and_save("btc_usd")

        assert result is None
        mock_deribit_client.get_index_price.assert_called_once_with("btc_usd")

    def test_get_all_records(
        self, price_tracking_service, mock_price_repository, sample_price_record
    ):
        mock_price_repository.get_all_by_ticker.return_value = [sample_price_record]

        result = price_tracking_service.get_all_records("btc_usd")

        assert len(result) == 1
        assert result[0] == sample_price_record
        mock_price_repository.get_all_by_ticker.assert_called_once_with("btc_usd")

    def test_get_last_record(
        self, price_tracking_service, mock_price_repository, sample_price_record
    ):
        mock_price_repository.get_last_by_ticker.return_value = sample_price_record

        result = price_tracking_service.get_last_record("btc_usd")

        assert result == sample_price_record
        mock_price_repository.get_last_by_ticker.assert_called_once_with("btc_usd")

    def test_get_filtered_records(
        self, price_tracking_service, mock_price_repository, sample_price_record
    ):
        mock_price_repository.get_by_ticker_and_date_range.return_value = [sample_price_record]

        result = price_tracking_service.get_filtered_records(
            "btc_usd", 1700000000, 1700003600
        )

        assert len(result) == 1
        mock_price_repository.get_by_ticker_and_date_range.assert_called_once_with(
            "btc_usd", 1700000000, 1700003600
        )

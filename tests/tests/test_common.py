from unittest.mock import call as mock_call
from unittest.mock import patch

import pytest

from strawberry_django_dataloaders.dataloaders import BasicPKDataLoader, BasicReverseFKDataLoader
from tests.choices import UrlChoices

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.django_db(transaction=True),
]


@pytest.mark.parametrize("url", UrlChoices.values)
async def test_dataloader_used(baseline_collection, arequest, url):
    """Tests that the dataloaders are actually used."""
    with patch.object(BasicPKDataLoader, "load_fn") as basic_dl_load_fn_mock:
        with patch.object(BasicReverseFKDataLoader, "load_fn") as reverse_dl_load_fn_mock:
            await arequest(baseline_collection.query, url)
            assert basic_dl_load_fn_mock.call_count == 2  # many_to_one (color field) & one_to_one (plant field)
            basic_dl_load_fn_mock.assert_has_calls(
                [
                    mock_call([fruit.color_id for fruit in baseline_collection.db_data.fruits]),
                    mock_call([fruit.plant_id for fruit in baseline_collection.db_data.fruits]),
                ],
                any_order=True,
            )
            reverse_dl_load_fn_mock.assert_called_once_with([fruit.pk for fruit in baseline_collection.db_data.fruits])


@pytest.mark.parametrize("url", UrlChoices.values)
async def test_no_errors_returned(baseline_collection, arequest, url):
    """Test no errors in the response."""
    resp = await arequest(baseline_collection.query, url)
    assert not resp.get("errors")


@pytest.mark.parametrize("url", UrlChoices.values)
async def test_correct_data_returned(baseline_collection, arequest, url):
    """Test returned data is correct."""
    resp = await arequest(baseline_collection.query, url)
    assert resp.json() == baseline_collection.exp_response().data


@pytest.mark.parametrize("url", UrlChoices.values)
async def test_on_empty_db(empty_db_collection, arequest, url):
    """Test returned data is correct."""
    resp = await arequest(empty_db_collection.query, url)
    assert resp.json() == empty_db_collection.exp_response().data

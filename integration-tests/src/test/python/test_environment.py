"""
First-pass integration test: confirm the docker-based CDA + CWMS database
stack (docker-compose.yml) comes up healthy, accepts API-key auth, and has
been seeded by cda-etl.
"""

import pytest

pytestmark = pytest.mark.integration


def test_data_api_is_reachable(cda_client, cda_stack):
    response = cda_client.get(cda_stack["base_url"] + "offices/HQ")
    assert response.status_code == 200, response.text
    assert response.json()["name"] == "HQ"


def test_cda_etl_seeding_completed(cda_stack):
    # The `cda_stack` fixture runs cda-etl (via docker compose run --rm
    # cda-etl) before yielding and raises RuntimeError on a non-zero exit,
    # so getting here at all means seeding succeeded.
    #
    # TODO: once the real cda-etl/data/sample-data/sample-app.yml (copied in
    # from the cwms-data-api repo, see that directory's README.md) is known,
    # extend this to assert on specific seeded offices/locations/timeseries
    # rather than just "the ETL job exited 0".
    assert cda_stack["base_url"]

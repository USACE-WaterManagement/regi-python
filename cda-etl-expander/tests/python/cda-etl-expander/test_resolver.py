#  MIT License
#  Copyright (c) 2026 Hydrologic Engineering Center
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
"""
Rows in these fixtures are taken from real SWT AV_PROPERTY data.
"""
import pytest

from cda_expander import resolver

TS_CATEGORY = "LOCATION TIME SERIES ASSOCIATION"

SPEC = {
    "categoryId": TS_CATEGORY,
    "placeholder": "?GLOBAL?",
    "valuePlaceholder": "?GLOBAL?",
}

# Real shape: a global whose value is itself a template, project-specific
# overrides that point at a *different* location's gauge, a PRIMARY prefix with
# no global of its own, and rows with empty values.
ROWS = [
    {"name": "Regi_project_INPUT.Hourly_wind_speed.?GLOBAL?",
     "value": "?GLOBAL?.Speed-Wind.Inst.1Hour.0.Ccp-Rev"},
    {"name": "Regi_project_INPUT.Inflow_wind_speed_instantaneous.?GLOBAL?",
     "value": "?GLOBAL?.Speed-Wind.Inst.1Hour.0.Decodes-Raw"},
    {"name": "Regi_project_INPUT.Inflow_wind_speed_instantaneous.KEMP",
     "value": "TRUS.Speed-Wind.Inst.1Hour.0.Decodes-Raw"},
    {"name": "Regi_project_PRIMARY.Hourly_wind_direction.EUFA",
     "value": "EUFA.Dir-Wind.Inst.1Hour.0.Ccp-Rev"},
    {"name": "Regi_project_INPUT.Hourly_lake_condition.?GLOBAL?"},
    {"name": "Regi_project_INPUT.Hourly_water_temp.EUFA"},
]


@pytest.fixture(autouse=True)
def clear_cache():
    resolver.reset_cache()
    yield
    resolver.reset_cache()


def _listing(mocker, rows=None):
    return mocker.patch("cwms.api.get", return_value=list(rows if rows is not None else ROWS))


# --- the listing ------------------------------------------------------------


def test_reads_the_whole_category_in_one_request(mocker):
    """
    The list endpoint takes *-mask parameters (PropertyController.getAll uses
    OFFICE_MASK / CATEGORY_ID_MASK / NAME_MASK). Sending the single-property
    GET's "office" / "category-id" instead leaves every mask null and CDA
    returns an empty list rather than an error - so this asserts the exact
    parameter names. Getting them wrong is invisible except as "Read 0 rows".
    """
    mock_get = _listing(mocker)

    resolver.resolve_ids("SWT", "EUFA", SPEC)

    mock_get.assert_called_once_with(
        endpoint="properties",
        params={"office-mask": "SWT", "category-id-mask": TS_CATEGORY},
        api_version=1,
    )


def test_does_not_use_the_single_property_parameters(mocker):
    mock_get = _listing(mocker)

    resolver.resolve_ids("SWT", "EUFA", SPEC)

    params = mock_get.call_args.kwargs["params"]
    assert "office" not in params
    assert "category-id" not in params


def test_many_projects_still_cost_one_request(mocker):
    mock_get = _listing(mocker)

    for project in ("EUFA", "KEMP", "BEND", "ALTU2", "TENK"):
        resolver.resolve_ids("SWT", project, SPEC)

    assert mock_get.call_count == 1


def test_reset_cache_forces_a_fresh_listing(mocker):
    mock_get = _listing(mocker)

    resolver.resolve_ids("SWT", "EUFA", SPEC)
    resolver.reset_cache()
    resolver.resolve_ids("SWT", "EUFA", SPEC)

    assert mock_get.call_count == 2


def test_a_second_office_is_a_second_request(mocker):
    mock_get = _listing(mocker)

    resolver.resolve_ids("SWT", "EUFA", SPEC)
    resolver.resolve_ids("SWL", "EUFA", SPEC)

    assert mock_get.call_count == 2


@pytest.mark.parametrize(
    "response",
    [
        ROWS,
        {"properties": ROWS},
        {"entries": ROWS},
        {"items": ROWS},
    ],
)
def test_tolerates_how_the_listing_is_wrapped(mocker, response):
    mocker.patch("cwms.api.get", return_value=response)

    assert resolver.resolve_ids("SWT", "EUFA", SPEC)


# --- resolution ------------------------------------------------------------


def test_global_value_is_substituted_with_the_project_id(mocker):
    _listing(mocker)

    ids = resolver.resolve_ids("SWT", "ALTU2", SPEC)

    assert "ALTU2.Speed-Wind.Inst.1Hour.0.Ccp-Rev" in ids
    assert "ALTU2.Speed-Wind.Inst.1Hour.0.Decodes-Raw" in ids


def test_project_specific_row_wins_over_the_global(mocker):
    _listing(mocker)

    ids = resolver.resolve_ids("SWT", "KEMP", SPEC)

    # KEMP's wind comes from the TRUS gauge, not from KEMP.
    assert "TRUS.Speed-Wind.Inst.1Hour.0.Decodes-Raw" in ids
    assert "KEMP.Speed-Wind.Inst.1Hour.0.Decodes-Raw" not in ids
    # The other family has no KEMP row, so its global still applies.
    assert "KEMP.Speed-Wind.Inst.1Hour.0.Ccp-Rev" in ids


def test_specific_row_with_no_global_is_still_picked_up(mocker):
    """
    SWT has Regi_project_PRIMARY.Hourly_wind_direction.EUFA with no matching
    PRIMARY ?GLOBAL? row. Iterating only over globals would drop it.
    """
    _listing(mocker)

    assert "EUFA.Dir-Wind.Inst.1Hour.0.Ccp-Rev" in resolver.resolve_ids("SWT", "EUFA", SPEC)


def test_row_with_an_empty_value_contributes_nothing(mocker):
    _listing(mocker)

    ids = resolver.resolve_ids("SWT", "EUFA", SPEC)

    assert not any("Lake Condition" in i or "lake_condition" in i for i in ids)
    assert not any("water_temp" in i for i in ids)


def test_ids_are_distinct(mocker):
    _listing(mocker, ROWS + [
        {"name": "Regi_project_OUTPUT.Hourly_wind_speed.?GLOBAL?",
         "value": "?GLOBAL?.Speed-Wind.Inst.1Hour.0.Ccp-Rev"},
    ])

    ids = resolver.resolve_ids("SWT", "ALTU2", SPEC)

    assert len(ids) == len(set(ids))
    assert ids.count("ALTU2.Speed-Wind.Inst.1Hour.0.Ccp-Rev") == 1


def test_order_is_stable_across_runs(mocker):
    _listing(mocker)
    first = resolver.resolve_ids("SWT", "EUFA", SPEC)

    resolver.reset_cache()
    _listing(mocker, list(reversed(ROWS)))
    second = resolver.resolve_ids("SWT", "EUFA", SPEC)

    assert first == second


def test_a_project_with_no_matching_rows_gets_nothing(mocker):
    mocker.patch("cwms.api.get", return_value=[
        {"name": "Regi_project_INPUT.Hourly_wind_speed.KEMP",
         "value": "TRUS.Speed-Wind.Inst.1Hour.0.Ccp-Rev"},
    ])

    assert resolver.resolve_ids("SWT", "EUFA", SPEC) == []


def test_empty_category_yields_nothing(mocker):
    mocker.patch("cwms.api.get", return_value=[])

    assert resolver.resolve_ids("SWT", "EUFA", SPEC) == []


# --- names ------------------------------------------------------------------


def test_family_containing_spaces_is_handled(mocker):
    mocker.patch("cwms.api.get", return_value=[
        {"name": "Regi_project_INPUT.Hourly Inflow and Weather Project Notes.?GLOBAL?",
         "value": "?GLOBAL?.Text.Inst.~1Day.0.Wcds-Rev"},
    ])

    assert resolver.resolve_ids("SWT", "EUFA", SPEC) == ["EUFA.Text.Inst.~1Day.0.Wcds-Rev"]


def test_malformed_names_are_ignored(mocker):
    mocker.patch("cwms.api.get", return_value=[
        {"name": "NoDotsAtAll", "value": "x"},
        {"name": "Only.Two", "value": "y"},
        {"name": "Regi_project_INPUT.Hourly_wind_speed.?GLOBAL?",
         "value": "?GLOBAL?.Speed-Wind.Inst.1Hour.0.Ccp-Rev"},
    ])

    assert resolver.resolve_ids("SWT", "EUFA", SPEC) == ["EUFA.Speed-Wind.Inst.1Hour.0.Ccp-Rev"]


def test_rows_without_a_name_are_skipped(mocker):
    mocker.patch("cwms.api.get", return_value=[
        {"value": "orphaned"},
        {"name": "Regi_project_INPUT.Hourly_wind_speed.?GLOBAL?",
         "value": "?GLOBAL?.Speed-Wind.Inst.1Hour.0.Ccp-Rev"},
    ])

    assert resolver.resolve_ids("SWT", "EUFA", SPEC) == ["EUFA.Speed-Wind.Inst.1Hour.0.Ccp-Rev"]


# --- guards -----------------------------------------------------------------


def test_raises_when_a_global_value_lacks_the_value_placeholder(mocker):
    mocker.patch("cwms.api.get", return_value=[
        {"name": "Regi_project_INPUT.Hourly_seepage.?GLOBAL?",
         "value": "SOMEPROJ.Flow-Seepage.Inst.1Hour.0.Ccp-Rev"},
    ])

    with pytest.raises(ValueError, match="does not contain the configured valuePlaceholder"):
        resolver.resolve_ids("SWT", "EUFA", SPEC)


def test_requires_category_id(mocker):
    with pytest.raises(ValueError, match="must define categoryId"):
        resolver.resolve_ids("SWT", "EUFA", {"placeholder": "?GLOBAL?"})


def test_requires_placeholder(mocker):
    with pytest.raises(ValueError, match="must define placeholder"):
        resolver.resolve_ids("SWT", "EUFA", {"categoryId": TS_CATEGORY})


def test_rejects_unsupported_type(mocker):
    with pytest.raises(ValueError, match="Unsupported source type"):
        resolver.resolve_ids("SWT", "EUFA", {**SPEC, "type": "publishedTimeSeries"})


def test_globals_are_skipped_without_a_value_placeholder(mocker):
    """
    Without valuePlaceholder a global's value cannot be made project-specific,
    so it is skipped rather than emitted verbatim. Specific rows still apply.
    """
    _listing(mocker)
    spec = {"categoryId": TS_CATEGORY, "placeholder": "?GLOBAL?"}

    assert resolver.resolve_ids("SWT", "EUFA", spec) == ["EUFA.Dir-Wind.Inst.1Hour.0.Ccp-Rev"]


# --- flow group clobs --------------------------------------------------------
#
# Fixtures mirror the real <flow_group> XML shape built/read by
# JDomFlowGroupImpl/FlowGroupTimeSeries/FlowGroupIncomingTimeSeries on the
# Java side (see compose_files/regi-data/SWT/Clobs/*.json for real examples).

FLOW_GROUP_SPEC = {"type": "flowGroupClob"}


def _simple_output(parameter="Flow-Res Out", interval="~1Day", duration="1Day",
                    version="Rev-Regi-Flowgroup", location="EUFA", sub_location="",
                    save_to_database="true", extra=""):
    return (
        f'<time_series_id save_to_database="{save_to_database}" attribute="0">'
        f'<loc_ref base_location_id="{location}" sub_location_id="{sub_location}"/>'
        f'<parameter>{parameter}</parameter><parameter_type>Ave</parameter_type>'
        f'<interval>{interval}</interval><duration>{duration}</duration>'
        f'<version>{version}</version>{extra}</time_series_id>'
    )


def _flow_group_clob(clob_id, *time_series_ids, office_id="SWT"):
    return {
        "office-id": office_id,
        "id": clob_id,
        "value": f"<flow_group>{''.join(time_series_ids)}</flow_group>",
    }


def _clob_listing(mocker, clobs):
    return mocker.patch("cwms.api.get", return_value=list(clobs))


def test_flow_group_output_id_is_reconstructed_from_its_parts(mocker):
    """The XML has parameter/interval/duration/version deconstructed; the id
    is the standard 6-part join of location.parameter.parameter_type.
    interval.duration.version."""
    _clob_listing(mocker, [
        _flow_group_clob("FLOW.EUFA.PROJECT_TOTAL", f"<time_series_set>{_simple_output()}</time_series_set>"),
    ])

    assert resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_SPEC) == [
        "EUFA.Flow-Res Out.Ave.~1Day.1Day.Rev-Regi-Flowgroup"
    ]


def test_sub_location_is_appended_with_a_dash(mocker):
    _clob_listing(mocker, [
        _flow_group_clob(
            "FLOW.EUFA.PROJECT_TOTAL",
            f"<time_series_set>{_simple_output(location='EUFA', sub_location='Dam')}</time_series_set>",
        ),
    ])

    ids = resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_SPEC)

    assert ids == ["EUFA-Dam.Flow-Res Out.Ave.~1Day.1Day.Rev-Regi-Flowgroup"]


def test_nested_aggregate_time_series_is_found(mocker):
    """A <time_series_id> can carry its own nested <time_series_set> of
    further <time_series_id> elements (REGI's "aggregate" time series) --
    these must be found no matter how deep, not just direct children of the
    flow group's own top-level <time_series_set>."""
    aggregate = _simple_output(interval="1Hour", duration="1Hour")
    outer = _simple_output(extra=f"<time_series_set>{aggregate}</time_series_set>")
    _clob_listing(mocker, [
        _flow_group_clob("FLOW.EUFA.PROJECT_TOTAL", f"<time_series_set>{outer}</time_series_set>"),
    ])

    ids = resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_SPEC)

    assert "EUFA.Flow-Res Out.Ave.~1Day.1Day.Rev-Regi-Flowgroup" in ids
    assert "EUFA.Flow-Res Out.Ave.1Hour.1Hour.Rev-Regi-Flowgroup" in ids


def test_incoming_time_series_id_is_read_as_literal_text(mocker):
    """Unlike outputs/aggregates, an <incoming_ts>'s <TSID> is already a
    complete 6-part id -- no reconstruction from parts."""
    incoming = (
        '<incoming_time_series_ids><incoming_ts Order="1" ACTIVE="true">'
        "<TSID>EUFA.Flow-Res In.Ave.~1Day.1Day.Ccp-Rev</TSID>"
        "</incoming_ts></incoming_time_series_ids>"
    )
    output = _simple_output(extra=incoming)
    _clob_listing(mocker, [
        _flow_group_clob("FLOW.EUFA.PROJECT_TOTAL", f"<time_series_set>{output}</time_series_set>"),
    ])

    ids = resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_SPEC)

    assert "EUFA.Flow-Res In.Ave.~1Day.1Day.Ccp-Rev" in ids
    assert "EUFA.Flow-Res Out.Ave.~1Day.1Day.Rev-Regi-Flowgroup" in ids


def test_inactive_incoming_time_series_is_skipped(mocker):
    incoming = (
        '<incoming_time_series_ids><incoming_ts Order="1" ACTIVE="false">'
        "<TSID>EUFA.Flow-Net Pumpage.Ave.1Day.1Day.Regi-Rev-Flowgroup</TSID>"
        "</incoming_ts></incoming_time_series_ids>"
    )
    output = _simple_output(extra=incoming)
    _clob_listing(mocker, [
        _flow_group_clob("FLOW.EUFA.PROJECT_TOTAL", f"<time_series_set>{output}</time_series_set>"),
    ])

    ids = resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_SPEC)

    assert "EUFA.Flow-Net Pumpage.Ave.1Day.1Day.Regi-Rev-Flowgroup" not in ids


def test_output_not_saved_to_database_is_skipped(mocker):
    _clob_listing(mocker, [
        _flow_group_clob(
            "FLOW.EUFA.PROJECT_TOTAL",
            f"<time_series_set>{_simple_output(save_to_database='false')}</time_series_set>",
        ),
    ])

    assert resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_SPEC) == []


def test_only_clobs_matching_the_project_prefix_are_used(mocker):
    """FLOW.EUFA.* belongs to EUFA; FLOW.KEYS.* must not leak into it even
    though both come back from the same office-wide listing."""
    _clob_listing(mocker, [
        _flow_group_clob("FLOW.EUFA.PROJECT_TOTAL", f"<time_series_set>{_simple_output(location='EUFA')}</time_series_set>"),
        _flow_group_clob("FLOW.KEYS.PROJECT_TOTAL", f"<time_series_set>{_simple_output(location='KEYS')}</time_series_set>"),
    ])

    ids = resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_SPEC)

    assert ids == ["EUFA.Flow-Res Out.Ave.~1Day.1Day.Rev-Regi-Flowgroup"]


def test_multiple_flow_groups_for_one_project_are_combined(mocker):
    _clob_listing(mocker, [
        _flow_group_clob(
            "FLOW.EUFA.PROJECT_TOTAL",
            f"<time_series_set>{_simple_output(parameter='Flow-Res Out')}</time_series_set>",
        ),
        _flow_group_clob(
            "FLOW.EUFA.TURBINE_TOTAL",
            f"<time_series_set>{_simple_output(parameter='Flow-Power', interval='1Hour', duration='1Hour')}</time_series_set>",
        ),
    ])

    ids = resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_SPEC)

    assert "EUFA.Flow-Res Out.Ave.~1Day.1Day.Rev-Regi-Flowgroup" in ids
    assert "EUFA.Flow-Power.Ave.1Hour.1Hour.Rev-Regi-Flowgroup" in ids


def test_a_project_with_no_matching_clobs_gets_nothing(mocker):
    _clob_listing(mocker, [
        _flow_group_clob("FLOW.KEYS.PROJECT_TOTAL", f"<time_series_set>{_simple_output(location='KEYS')}</time_series_set>"),
    ])

    assert resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_SPEC) == []


def test_empty_clob_listing_yields_nothing(mocker):
    _clob_listing(mocker, [])

    assert resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_SPEC) == []


def test_non_flow_group_root_is_skipped(mocker):
    _clob_listing(mocker, [{"office-id": "SWT", "id": "FLOW.EUFA.PROJECT_TOTAL", "value": "<not_a_flow_group/>"}])

    assert resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_SPEC) == []


def test_malformed_xml_is_skipped_not_raised(mocker):
    _clob_listing(mocker, [{"office-id": "SWT", "id": "FLOW.EUFA.PROJECT_TOTAL", "value": "<flow_group><unclosed>"}])

    assert resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_SPEC) == []


def test_time_series_id_missing_a_required_field_is_skipped(mocker):
    incomplete = (
        '<time_series_id save_to_database="true" attribute="0">'
        '<loc_ref base_location_id="EUFA" sub_location_id=""/>'
        "<parameter>Flow-Res Out</parameter>"
        # parameter_type/interval/duration/version all missing.
        "</time_series_id>"
    )
    _clob_listing(mocker, [
        _flow_group_clob("FLOW.EUFA.PROJECT_TOTAL", f"<time_series_set>{incomplete}</time_series_set>"),
    ])

    assert resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_SPEC) == []


def test_ids_are_distinct_across_flow_groups(mocker):
    """The same output/incoming id showing up in two flow groups' clobs (e.g.
    a shared incoming ts) is only returned once."""
    shared_incoming = (
        '<incoming_time_series_ids><incoming_ts Order="1" ACTIVE="true">'
        "<TSID>EUFA.Elev.Inst.1Hour.0.Ccp-Rev</TSID>"
        "</incoming_ts></incoming_time_series_ids>"
    )
    output_a = _simple_output(parameter="Flow-Res Out", extra=shared_incoming)
    output_b = _simple_output(parameter="Flow-Power", extra=shared_incoming)
    _clob_listing(mocker, [
        _flow_group_clob("FLOW.EUFA.PROJECT_TOTAL", f"<time_series_set>{output_a}</time_series_set>"),
        _flow_group_clob("FLOW.EUFA.TURBINE_TOTAL", f"<time_series_set>{output_b}</time_series_set>"),
    ])

    ids = resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_SPEC)

    assert ids.count("EUFA.Elev.Inst.1Hour.0.Ccp-Rev") == 1


def test_flow_group_clobs_are_read_once_per_project(mocker):
    mock_get = _clob_listing(mocker, [
        _flow_group_clob("FLOW.EUFA.PROJECT_TOTAL", f"<time_series_set>{_simple_output(location='EUFA')}</time_series_set>"),
    ])

    resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_SPEC)
    resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_SPEC)

    mock_get.assert_called_once()


def test_flow_group_clobs_are_a_separate_request_per_project(mocker):
    """
    Unlike the property resolver's one-request-per-office, flow-group clobs
    are read one project at a time (FLOW.EUFA.*, then a separate FLOW.KEYS.*
    for KEYS) rather than a single office-wide FLOW.* sweep -- so a second
    project costs a second request.
    """
    mock_get = _clob_listing(mocker, [
        _flow_group_clob("FLOW.EUFA.PROJECT_TOTAL", f"<time_series_set>{_simple_output(location='EUFA')}</time_series_set>"),
    ])

    resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_SPEC)
    resolver.resolve_ids("SWT", "KEYS", FLOW_GROUP_SPEC)

    assert mock_get.call_count == 2


def test_flow_group_clob_listing_is_scoped_to_office_and_project(mocker):
    mock_get = _clob_listing(mocker, [])

    resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_SPEC)

    params = mock_get.call_args.kwargs["params"]
    assert params["office"] == "SWT"
    # Not a regex-escaped "FLOW\.EUFA\..*" -- against a real CDA that form
    # times out, while this plain form comes back fast.
    assert params["like"] == "FLOW.EUFA.*"


def test_flow_group_clob_listing_uses_the_configured_id_prefix(mocker):
    mock_get = _clob_listing(mocker, [])

    resolver.resolve_ids("SWT", "EUFA", {"type": "flowGroupClob", "idPrefix": "CUSTOM"})

    params = mock_get.call_args.kwargs["params"]
    assert params["like"] == "CUSTOM.EUFA.*"


def test_flow_group_clob_response_wrapped_in_clobs_key_is_tolerated(mocker):
    mocker.patch("cwms.api.get", return_value={"clobs": [
        _flow_group_clob("FLOW.EUFA.PROJECT_TOTAL", f"<time_series_set>{_simple_output()}</time_series_set>"),
    ]})

    assert resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_SPEC) == [
        "EUFA.Flow-Res Out.Ave.~1Day.1Day.Rev-Regi-Flowgroup"
    ]


# --- flow group clob ids (type: flowGroupClobIds) ----------------------------
#
# Same underlying read as "flowGroupClob" above, but returns the clob ids
# themselves rather than the ts ids inside them.

FLOW_GROUP_CLOB_IDS_SPEC = {"type": "flowGroupClobIds"}


def test_flow_group_clob_ids_returns_the_clob_ids_not_their_contents(mocker):
    _clob_listing(mocker, [
        _flow_group_clob("FLOW.EUFA.PROJECT_TOTAL", f"<time_series_set>{_simple_output()}</time_series_set>"),
        _flow_group_clob(
            "FLOW.EUFA.TURBINE_TOTAL",
            f"<time_series_set>{_simple_output(parameter='Flow-Power', interval='1Hour', duration='1Hour')}</time_series_set>",
        ),
    ])

    ids = resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_CLOB_IDS_SPEC)

    assert ids == ["FLOW.EUFA.PROJECT_TOTAL", "FLOW.EUFA.TURBINE_TOTAL"]


def test_flow_group_clob_ids_only_include_the_project_prefix(mocker):
    _clob_listing(mocker, [
        _flow_group_clob("FLOW.EUFA.PROJECT_TOTAL", f"<time_series_set>{_simple_output(location='EUFA')}</time_series_set>"),
        _flow_group_clob("FLOW.KEYS.PROJECT_TOTAL", f"<time_series_set>{_simple_output(location='KEYS')}</time_series_set>"),
    ])

    ids = resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_CLOB_IDS_SPEC)

    assert ids == ["FLOW.EUFA.PROJECT_TOTAL"]


def test_flow_group_clob_ids_are_returned_even_without_a_value(mocker):
    """Unlike "flowGroupClob" (which has nothing to extract from an empty
    clob), "flowGroupClobIds" only needs the id -- a clob with no value is
    still a clob that exists and belongs in "clobs"."""
    _clob_listing(mocker, [{"office-id": "SWT", "id": "FLOW.EUFA.PROJECT_TOTAL", "value": None}])

    assert resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_CLOB_IDS_SPEC) == ["FLOW.EUFA.PROJECT_TOTAL"]


def test_flow_group_clob_ids_are_distinct(mocker):
    _clob_listing(mocker, [
        _flow_group_clob("FLOW.EUFA.PROJECT_TOTAL", f"<time_series_set>{_simple_output()}</time_series_set>"),
    ])

    resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_CLOB_IDS_SPEC)
    ids = resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_CLOB_IDS_SPEC)

    assert ids.count("FLOW.EUFA.PROJECT_TOTAL") == 1


def test_flow_group_clob_and_clob_ids_share_one_request_per_project(mocker):
    """Declaring both "flowGroupOutputs" (flowGroupClob) and "flowGroupClobs"
    (flowGroupClobIds) templates for the same project must not double the
    number of clob listing requests -- they share _load_flow_group_clobs's
    cache."""
    mock_get = _clob_listing(mocker, [
        _flow_group_clob("FLOW.EUFA.PROJECT_TOTAL", f"<time_series_set>{_simple_output()}</time_series_set>"),
    ])

    resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_SPEC)
    resolver.resolve_ids("SWT", "EUFA", FLOW_GROUP_CLOB_IDS_SPEC)

    mock_get.assert_called_once()

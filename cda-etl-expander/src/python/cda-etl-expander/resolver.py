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
Resolves every id a configured source has to offer, per project.

Two sources, dispatched by a spec's ``type``
---------------------------------------------
``property`` (the default) resolves every id an association property
category has to offer. A category is read once per office with a single
request::

    GET properties?office=SWT&category-id=LOCATION TIME SERIES ASSOCIATION

REGI's naming convention: rows in a category are named
``{prefix}.{family}.{scope}`` where ``scope`` is either a project id or the
literal placeholder token REGI uses for "applies to every project"
(``?GLOBAL?``)::

    Regi_project_INPUT.Hourly_wind_speed.?GLOBAL?  -> ?GLOBAL?.Speed-Wind.Inst.1Hour.0.Ccp-Rev
    Regi_project_INPUT.Hourly_wind_speed.EUFA      -> EUFA.Speed-Wind.Inst.1Hour.0.Ccp-Rev

``flowGroupClob``/``flowGroupClobIds`` both read a project's flow-group clobs
(``{idPrefix}.{project_id}.{flow-group-name}``, one request per project --
see ``_load_flow_group_clobs``) but return different things from the same
read: ``flowGroupClob`` extracts the ts ids referenced inside each clob's XML
(``_resolve_from_flow_group_clobs``), while ``flowGroupClobIds`` returns the
clob ids themselves (``_resolve_flow_group_clob_ids``), so a project's own
``clobs:`` list can be auto-discovered too rather than hand-listed.
"""
from __future__ import annotations

import logging
import xml.etree.ElementTree as ElementTree
from typing import Any, Callable, Iterable

import cwms

logger = logging.getLogger(__name__)

Resolver = Callable[[str, str, dict[str, Any]], "list[str]"]

_CATEGORY_CACHE: dict[tuple[str, str], dict[str, str | None]] = {}
_CLOB_CACHE: dict[tuple[str, str], list[dict[str, Any]]] = {}


def reset_cache() -> None:
    """
    Clears the per-run category/clob caches. Called at the start of each
    expansion; tests call it between cases so one case's rows cannot satisfy
    another.
    """
    _CATEGORY_CACHE.clear()
    _CLOB_CACHE.clear()


def resolve_ids(office_id: str, project_id: str, spec: dict[str, Any]) -> list[str]:
    """
    Returns every distinct id this category yields for one project.
    """
    source_type = spec.get("type", "property")
    resolver = _RESOLVERS.get(source_type)

    if resolver is None:
        raise ValueError(
            f"Unsupported source type '{source_type}'. Supported types: {sorted(_RESOLVERS)}."
        )

    return resolver(office_id, project_id, spec)


def _resolve_from_property_category(
    office_id: str, project_id: str, spec: dict[str, Any]
) -> list[str]:
    category_id = spec.get("categoryId")
    placeholder = spec.get("placeholder")
    value_placeholder = spec.get("valuePlaceholder")

    if not category_id:
        raise ValueError("A property-category template must define categoryId.")

    if not placeholder:
        raise ValueError(
            "A property-category template must define placeholder - the token a property "
            "name uses in place of a project id (REGI uses '?GLOBAL?')."
        )

    rows = _load_category(office_id, category_id)

    specific: dict[tuple[str, str], str] = {}
    globals_: dict[tuple[str, str], str] = {}

    for name, value in rows.items():
        parts = _split_name(name)
        if parts is None:
            logger.debug("Ignoring property %s in %s: not prefix.family.scope.", name, category_id)
            continue

        prefix, family, scope = parts

        if scope == project_id:
            if value:
                specific[(prefix, family)] = value
        elif scope == placeholder:
            if value:
                globals_[(prefix, family)] = value

    resolved: list[str] = []
    seen: set[str] = set()

    def add(candidate: str) -> None:
        if candidate and candidate not in seen:
            seen.add(candidate)
            resolved.append(candidate)

    # 1. Project-specific rows win outright.
    for key in sorted(specific):
        value = specific[key]
        if value_placeholder and value_placeholder in value:
            value = value.replace(value_placeholder, project_id)
        add(value)

    # 2. Globals fill in the families this project has no specific row for.
    for key in sorted(globals_):
        if key in specific:
            continue

        template = globals_[key]

        if not value_placeholder:
            logger.debug(
                "Skipping global %s.%s in %s for %s: no valuePlaceholder configured, so its "
                "value cannot be made project-specific.",
                key[0], key[1], category_id, project_id,
            )
            continue

        if value_placeholder not in template:
            raise ValueError(
                f"Global property {key[0]}.{key[1]}.{placeholder} in category {category_id} "
                f"for office {office_id} has value {template!r}, which does not contain the "
                f"configured valuePlaceholder {value_placeholder!r}. Nothing would be "
                "substituted and the template would be used as a literal id."
            )

        add(template.replace(value_placeholder, project_id))

    logger.debug(
        "Resolved %d id(s) for %s.%s from %s (%d specific, %d global)",
        len(resolved), office_id, project_id, category_id, len(specific), len(globals_),
    )

    return resolved


def _split_name(name: str) -> tuple[str, str, str] | None:
    """
    Splits ``{prefix}.{family}.{scope}`` on the first and last dots, so a family
    containing dots or spaces survives (SWT has "Hourly Inflow and Weather
    Project Notes").
    """
    first = name.find(".")
    last = name.rfind(".")

    if first <= 0 or last <= first or last == len(name) - 1:
        return None

    return name[:first], name[first + 1 : last], name[last + 1 :]


def _load_category(office_id: str, category_id: str) -> dict[str, str | None]:
    key = (office_id, category_id)

    if key in _CATEGORY_CACHE:
        return _CATEGORY_CACHE[key]

    logger.info("Reading property category %s for office %s", category_id, office_id)
    response = cwms.api.get(
        endpoint="properties",
        params={
            "office-mask": office_id,
            "category-id-mask": category_id,
        },
        api_version=1,
    )

    rows: dict[str, str | None] = {}
    for entry in _iter_property_entries(response):
        name = _extract_property_name(entry)
        if not name:
            logger.warning(
                "Skipping a property in category %s for office %s: no name found.",
                category_id,
                office_id,
            )
            continue

        rows[name] = entry.get("value")

    if rows:
        logger.info(
            "Read %d property row(s) from category %s for office %s",
            len(rows),
            category_id,
            office_id,
        )
    else:
        logger.warning(
            "Read no properties from category %s for office %s. Nothing will be appended for "
            "this category. Check the categoryId spelling and that the office has association "
            "properties - the listing endpoint returns an empty list rather than an error.",
            category_id,
            office_id,
        )

    _CATEGORY_CACHE[key] = rows

    return rows


def _iter_property_entries(response: object) -> Iterable[dict]:
    """
    Mirrors cda_etl.property's tolerance for how the listing is wrapped.
    Duplicated rather than imported - the two tools stay independent.
    """
    if isinstance(response, list):
        return [item for item in response if isinstance(item, dict)]

    if isinstance(response, dict):
        for key in ("properties", "entries", "items", "value"):
            nested = response.get(key)
            if isinstance(nested, list):
                return [item for item in nested if isinstance(item, dict)]

        if "name" in response or "property-name" in response:
            return [response]

    return []


def _extract_property_name(entry: dict) -> str | None:
    name = entry.get("name") or entry.get("property-name")
    if isinstance(name, str) and name.strip():
        return name

    property_id = entry.get("id")
    if isinstance(property_id, str) and property_id.strip():
        return property_id

    return None


def _resolve_from_flow_group_clobs(
    office_id: str, project_id: str, spec: dict[str, Any]
) -> list[str]:
    """
    Reads every clob whose id matches ``{idPrefix}.{project_id}.{flow-group-name}``
    -- one project at a time, e.g. a request scoped to ``FLOW.EUFA.*`` for
    EUFA and a separate one scoped to ``FLOW.KEYS.*`` for KEYS, never a single
    office-wide ``FLOW.*`` sweep -- and pulls every ts id referenced anywhere
    in each matching clob's ``<flow_group>`` XML: the flow group's own
    output(s), any aggregate time series nested under them, and any incoming
    (input) time series they're built from. See ``_extract_flow_group_ts_ids``
    for exactly how each of those is found and, for outputs/aggregates,
    reconstructed from their deconstructed parameter/interval/duration/version
    fields (mirroring ``FlowGroupTimeSeries``/``FlowGroupIncomingTimeSeries``
    on the Java side that builds/reads this same XML).
    """
    resolved: list[str] = []
    seen: set[str] = set()

    for clob_id, value in _matching_flow_group_clobs(office_id, project_id, spec):
        if not value:
            logger.debug("Clob %s for %s.%s has no value; skipping.", clob_id, office_id, project_id)
            continue

        for ts_id in _extract_flow_group_ts_ids(clob_id, value):
            if ts_id not in seen:
                seen.add(ts_id)
                resolved.append(ts_id)

    logger.debug(
        "Resolved %d flow-group output id(s) for %s.%s from %s.%s.* clobs",
        len(resolved), office_id, project_id, spec.get("idPrefix", "FLOW"), project_id,
    )

    return resolved


def _resolve_flow_group_clob_ids(
    office_id: str, project_id: str, spec: dict[str, Any]
) -> list[str]:
    """
    Returns the id of every flow-group clob found for this project -- not the
    ts ids inside them (see ``_resolve_from_flow_group_clobs`` for that) --
    so a project's ``clobs:`` list can be auto-discovered the same way its
    ``timeseries:`` list is, rather than needing every
    ``{idPrefix}.{project_id}.*`` id hand-listed. Shares
    ``_load_flow_group_clobs``'s cache with ``_resolve_from_flow_group_clobs``,
    so declaring both "flowGroupOutputs" and "flowGroupClobs" templates for
    the same project still costs only one request per project.
    """
    resolved: list[str] = []
    seen: set[str] = set()

    for clob_id, _value in _matching_flow_group_clobs(office_id, project_id, spec):
        if clob_id not in seen:
            seen.add(clob_id)
            resolved.append(clob_id)

    return resolved


def _matching_flow_group_clobs(
    office_id: str, project_id: str, spec: dict[str, Any]
) -> list[tuple[str, str | None]]:
    """Yields (clob_id, value) for every flow-group clob belonging to this project."""
    id_prefix = spec.get("idPrefix", "FLOW")
    project_prefix = f"{id_prefix}.{project_id}."

    matches: list[tuple[str, str | None]] = []

    for clob in _load_flow_group_clobs(office_id, id_prefix, project_id):
        clob_id = clob.get("id")
        # Defensive re-check: the listing is already scoped to this project's
        # prefix server-side, but a clob matching the "like" pattern on some
        # other basis (case, a looser server-side match, ...) must not leak in.
        if not clob_id or not clob_id.startswith(project_prefix):
            continue

        matches.append((clob_id, clob.get("value")))

    return matches


def _load_flow_group_clobs(office_id: str, id_prefix: str, project_id: str) -> list[dict[str, Any]]:
    key = (office_id, id_prefix, project_id)

    if key in _CLOB_CACHE:
        return _CLOB_CACHE[key]

    logger.info("Reading %s.%s.* clobs for office %s", id_prefix, project_id, office_id)
    response = cwms.api.get(
        endpoint="clobs",
        params={
            "office": office_id,
            # Not a regex-escaped "FLOW\.EUFA\..*" -- against a real CDA that
            # form times out, while this plain "FLOW.EUFA.*" comes back fast.
            "like": f"{id_prefix}.{project_id}.*",
            "include-values": True,
            "page-size": 5000,
        },
    )

    # Sorted once here so repeated calls for this project see the same order,
    # matching the property resolver's stability.
    clobs = sorted(_iter_clob_entries(response), key=lambda entry: entry.get("id") or "")

    if clobs:
        logger.info("Read %d %s.%s.* clob(s) for office %s", len(clobs), id_prefix, project_id, office_id)
    else:
        logger.warning(
            "Read no %s.%s.* clobs for office %s. Nothing will be appended for this project's "
            "flow-group outputs. Check idPrefix and that this project has flow-group clobs - "
            "the listing endpoint returns an empty list rather than an error.",
            id_prefix,
            project_id,
            office_id,
        )

    _CLOB_CACHE[key] = clobs

    return clobs


def _iter_clob_entries(response: object) -> list[dict[str, Any]]:
    """Mirrors _iter_property_entries's tolerance for how the listing is wrapped."""
    if isinstance(response, list):
        return [item for item in response if isinstance(item, dict)]

    if isinstance(response, dict):
        nested = response.get("clobs")
        if isinstance(nested, list):
            return [item for item in nested if isinstance(item, dict)]

        if "id" in response or "value" in response:
            return [response]

    return []


def _extract_flow_group_ts_ids(clob_id: str, xml_text: str) -> list[str]:
    """
    Returns every ts id referenced anywhere in one flow group's XML.

    Two different kinds of reference, found two different ways:

    * Output/aggregate ``<time_series_id>`` elements: the id is
      *deconstructed* into ``loc_ref``/``parameter``/``parameter_type``/
      ``interval``/``duration``/``version`` children and has to be rebuilt
      (see ``_flow_group_time_series_id``, mirroring
      ``TimeSeriesIdentifierFactory`` on the Java side). A ``<time_series_id>``
      can itself carry a *nested* ``<time_series_set>`` of further
      ``<time_series_id>`` elements -- REGI's "aggregate" time series, one
      output built up from others (``FlowGroupTimeSeries._aggregateTimeSeries``)
      -- so this searches the whole tree (``.//``), not just the flow group's
      direct children, to reach every nesting depth in one pass.
    * Incoming (input) ``<incoming_ts>`` elements, under a ``<time_series_id>``'s
      ``<incoming_time_series_ids>``: these carry an already-complete 6-part
      id as plain text in a ``<TSID>`` child (``FlowGroupIncomingTimeSeries``),
      so no reconstruction is needed -- just read it.

    Either kind is skipped if explicitly marked inactive
    (``save_to_database="false"`` / ``ACTIVE="false"``), since that means the
    calculation doesn't actually write/use it.
    """
    try:
        root = ElementTree.fromstring(xml_text)
    except ElementTree.ParseError as exc:
        logger.warning("Clob %s is not valid XML; skipping (%s).", clob_id, exc)
        return []

    if root.tag != "flow_group":
        logger.debug("Clob %s root is <%s>, not <flow_group>; skipping.", clob_id, root.tag)
        return []

    ids: list[str] = []

    for ts_elem in root.findall(".//time_series_id"):
        if ts_elem.get("save_to_database", "true").lower() == "false":
            continue

        ts_id = _flow_group_time_series_id(ts_elem)
        if ts_id is None:
            logger.warning(
                "Clob %s has a <time_series_id> missing a required field (loc_ref/"
                "base_location_id, parameter, parameter_type, interval, duration or "
                "version); skipping it.",
                clob_id,
            )
            continue

        ids.append(ts_id)

    for incoming_elem in root.findall(".//incoming_ts"):
        if incoming_elem.get("ACTIVE", "true").lower() == "false":
            continue

        tsid_elem = incoming_elem.find("TSID")
        tsid = tsid_elem.text.strip() if tsid_elem is not None and tsid_elem.text else ""
        if not tsid:
            logger.warning("Clob %s has an <incoming_ts> with no TSID; skipping it.", clob_id)
            continue

        ids.append(tsid)

    return ids


def _flow_group_time_series_id(ts_elem: ElementTree.Element) -> str | None:
    """
    Reconstructs a 6-part ts id -- ``location.parameter.parameter_type.
    interval.duration.version`` -- from one output/aggregate
    ``<time_series_id>`` element's deconstructed fields
    """
    loc_ref = ts_elem.find("loc_ref")
    if loc_ref is None:
        return None

    base_location_id = loc_ref.get("base_location_id")
    if not base_location_id:
        return None

    sub_location_id = loc_ref.get("sub_location_id") or ""
    location_id = f"{base_location_id}-{sub_location_id}" if sub_location_id else base_location_id

    parts = [location_id]
    for tag in ("parameter", "parameter_type", "interval", "duration", "version"):
        child = ts_elem.find(tag)
        text = child.text.strip() if child is not None and child.text else ""
        if not text:
            return None
        parts.append(text)

    return ".".join(parts)


_RESOLVERS: dict[str, Resolver] = {
    "property": _resolve_from_property_category,
    "flowGroupClob": _resolve_from_flow_group_clobs,
    "flowGroupClobIds": _resolve_flow_group_clob_ids,
}


__all__ = ["resolve_ids", "reset_cache"]

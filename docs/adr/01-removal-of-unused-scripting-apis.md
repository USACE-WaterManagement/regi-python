# ADR: Remove Client-Approved Scriptable Public APIs Designated for Retirement

## Status

Accepted during meeting with USACE on 2026-06-29

## Context

During a dedicated scripting meeting, USACE approved removing several public scriptable API implementation classes 
that had previously been identified as candidates for removal.

The approved removals are class-level API removals only. 
At this time, no method-level APIs listed in the API recommendations document will be removed.

The APIs approved for removal are:

- `ScriptableExportTSAssociationsImpl`
- `ScriptableExportSigStagesImpl`
- `ScriptableImportSigStagesImpl`
- `RetrieveSigStagesImpl`
- `ScriptablePoolPercentImpl`
- `ScriptableStatusGraphicImpl`

These APIs were reviewed based on current usage in recent examples, district scripts, and older examples. 
The approved removals are not currently used by district scripts. 
Some may still appear in examples, but they are associated with unused, obsolete, or replacement functionality.

## Decision

We will remove the following public scriptable API implementation classes:

- `ScriptableExportTSAssociationsImpl`
- `ScriptableExportSigStagesImpl`
- `ScriptableImportSigStagesImpl`
- `RetrieveSigStagesImpl`
- `ScriptablePoolPercentImpl`
- `ScriptableStatusGraphicImpl`

We will not remove any method-level APIs at this time, including method-level APIs that may have been separately 
identified as unused, unsupported, or possible removal candidates.

## Consequences

### Positive Consequences

- Reduces the supported public API surface area.
- Removes obsolete or unused scriptable APIs.
- Simplifies future maintenance.
- Allows replacement or consolidated functionality to become the supported path where applicable.

### Negative Consequences

- Recent examples that reference any of these APIs will need to be reviewed and updated.
- Documentation referencing these APIs must be updated to avoid advertising removed functionality.

## Alternatives Considered

### Keep All APIs

Rejected. This would preserve backward compatibility, but updates for CWBI Cloud support will not be backwards compatible to begin with.

### Remove Both Class-Level and Method-Level APIs

Rejected for now. The client approved the listed class-level removals only. Method-level removals remain out of scope for this change.

### Deprecate Before Removal

Rejected or deferred. The client approved removal of the listed APIs. 

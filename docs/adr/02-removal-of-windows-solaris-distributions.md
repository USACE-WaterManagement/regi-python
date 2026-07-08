# ADR: Remove Windows and Solaris REGI Headless Distribution Support from This Repository

## Status

Accepted

## Context

The project previously included support for Windows and Solaris distributions of REGI Headless, which
will no longer be maintained in this GitHub repository as the HEC DevNet-hosted fork will be archived. 
If additional maintenance for Windows and Solaris distributions is required, the HEC DevNet fork will be unarchived 
and updates will be made accordingly.

This repository will be the source of truth for future REGI Headless development targeting CWBI Cloud compatibility,
with commit history preserved from the HEC DevNet fork.

## Decision

Remove Windows and Solaris REGI Headless distribution support from this GitHub repository.

Distribution-specific updates for Windows and Solaris will be made in the HEC DevNet-hosted fork.
Future cloud-compatible development and will be made in this repository.

## Consequences

### Positive Consequences

- Clarifies repository ownership and purpose.
- Reduces maintenance burden for legacy distribution support.
- Focuses this repository on CWBI Cloud compatibility.
- Separates cloud-targeted development from Windows and Solaris distribution maintenance.

### Negative Consequences

- Windows and Solaris distribution maintainers will need to use the HEC DevNet-hosted fork.
- Documentation, build scripts, examples, packaging, release processes, and CI/CD automation may need to be updated or removed.

## Alternatives Considered

### Continue Supporting All Distributions in This Repository

Rejected. Supporting Windows, Solaris, and CWBI Cloud targets in the same repository would increase the
maintenance burden and make the repository direction less clear.

### Remove Windows and Solaris Distribution Support Entirely

Rejected. The distributions may still need maintenance, and the archived HEC DevNet-hosted fork will
remain available for that work.

### Move CWBI Cloud Work to a Separate Repository

Rejected. This GitHub repository will be the source of truth for future CWBI Cloud compatibility work,
with commit history preserved from the HEC DevNet fork. This repository will produce a python wheel distribution
that can be pulled into CWBI Cloud scripting deployments. See [cwbi-wm-images](https://github.com/USACE/cwbi-wm-images).
Keeping the commit history intact preserves the historical context of the codebase. The design of the Python 3 supported
implementation will require minimal updates to the Java codebase.
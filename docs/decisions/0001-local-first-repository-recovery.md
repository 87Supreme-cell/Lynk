# ADR 0001: Local-first repository recovery

**Status:** accepted

## Context

Lynk needs an auditable, recoverable build process. A remote push can fail due
to network, authentication, service, or branch-protection issues. The project
must remain reproducible without relying on a successful push as the sole
record of work.

## Decision

The local Git working tree and local committed history are the immediate system
of record for source code, tests, configuration, and documentation. GitHub is a
synchronized remote replica.

Each meaningful change uses a named branch and a local commit before pushing.
Normal work uses additive commits; it does not use force pushes or destructive
resets. Build-log entries and ADRs link the human rationale to the commit
history.

Private document originals, local databases, secrets, and model weights remain
outside Git. They require a separate encrypted backup and recovery design.

## Alternatives considered

### Rely on GitHub as the only source of truth

Rejected because a failed or unavailable remote would interrupt recovery and
auditability.

### Store all local runtime data in Git

Rejected because it risks exposing private documents and creates an unsuitable
repository for large, changing runtime artifacts.

### Permit history rewrites for routine cleanup

Rejected because it weakens the audit trail and makes recovery harder.

## Consequences

- A failed push leaves a complete local commit available to retry or restore.
- Git history, the build log, and ADRs provide layered evidence of how the
  project evolved.
- Local runtime data needs its own encrypted backup plan before the system is
  used with personal documents.

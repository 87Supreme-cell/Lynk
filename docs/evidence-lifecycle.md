# Evidence lifecycle

```text
ingested document -> candidate -> human review -> approved | rejected
                                      |
                                      +-> decision trace and audit event

private document -> private context (requires explicit collection grant)
```

Chunks inherit the parent document's lifecycle state, collection scope, content
hash, version, and page/span provenance. Retrieval must enforce this lifecycle
in SQL and again in the service policy check before a model receives context.

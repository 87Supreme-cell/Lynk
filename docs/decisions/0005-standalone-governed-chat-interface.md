# ADR 0005: Standalone governed chat interface

**Status:** accepted

## Context

Lynk needs a user-facing chat experience, but its value is governed evidence:
principal-scoped retrieval, reviewable citations, privacy controls, and audit
events. Open WebUI is useful as an optional local model runtime, but making it
the product interface would couple Lynk's user experience and authority model
to a third-party application.

## Decision

Lynk will develop a standalone browser interface in five stages:

1. Design the Lynk chat, evidence drawer, review queue, upload flow, and model
   settings independently of any model-host UI.
2. Implement the design as a React and TypeScript frontend.
3. Connect it first to a mocked Lynk API using a structured answer contract:
   answer text, citations, policy result, and safe user-facing status.
4. Replace mocks with a local FastAPI API that calls the governed retrieval,
   citation-validation, and audit services.
5. Package the same interface as a desktop application only after the browser
   contract, accessibility, and local workflow are validated.

The frontend does not directly call a model runtime, execute retrieval, select
an evidence resource, or supply an authoritative principal ID. Lynk's backend
owns those decisions. Open WebUI, Ollama, and other local model servers remain
replaceable adapters behind the backend model interface.

## Alternatives considered

### Use Open WebUI as Lynk's product frontend

Rejected because it makes the governed retrieval and review experience depend
on another application's UX and permission model.

### Build a desktop shell before a browser interface

Rejected because packaging, native integration, and distribution would delay
validation of the more important API and evidence-review contract.

### Let the browser call model runtimes directly

Rejected because it can bypass policy enforcement, evidence authorization,
citation validation, and audit logging.

## Consequences

- Lynk gains a model-provider-independent product interface.
- The first API work must return structured, citation-rich responses rather
  than raw model text.
- Browser identity is mapped to a backend-controlled principal; a client field
  is never treated as authority.
- Desktop packaging is an additive distribution decision, not a rewrite.

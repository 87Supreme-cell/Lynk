# Policy contract

Lynk treats policy as the authority for evidence access and promotion. A model
may summarize retrieved evidence, but it cannot retrieve arbitrary rows,
approve a candidate, alter permissions, or promote evidence.

## Answer eligibility

- `approved` evidence in a `curated` collection is eligible for grounding.
- `private` evidence is eligible only when the requesting principal has an
  explicit `retrieve` grant on its collection.
- `candidate` evidence is visible only to review workflows.
- `rejected` evidence is never retrievable for answers.

Every promotion must have a human reviewer, reason, and policy version. The
promotion write and its audit event must occur in one transaction.

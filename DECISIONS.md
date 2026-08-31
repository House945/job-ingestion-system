# Design Decisions

Interpretation and design choices made while implementing this system, with the alternatives that were considered and rejected. Where the brief was ambiguous, the ambiguity is named rather than resolved silently.

---

## 1. Two job models, not one

**Decision.** `RawJob` and `CanonicalJob` are separate types. `RawJob` has every field optional and mirrors what arrived from the feed. `CanonicalJob` has a guaranteed structure and proper types, and is the only thing the approval rules ever see.

**Rationale.** The brief asks for models that prevent invalid states. A single model with every field optional satisfies that only on paper: each rule then has to defend itself with `if x is not None`, and the guarantee lives in the rules rather than the type. Splitting the models moves the uncertainty to a boundary that is crossed exactly once, in normalization.

**Rejected alternative.** One model with optional fields and validation helpers. Simpler to write, but it pushes null-handling into every consumer and makes it impossible to tell, from a type signature, whether a value has been normalized.

---

## 2. `CanonicalJob` permits an empty title

**Decision.** The canonical model does not reject an empty title, even though an empty title is disqualifying.

**Rationale.** "Canonical" means parseable, not compliant. Structural validity and business validity are different concerns evaluated at different stages. If the model rejected empty titles, `TitleRule` could never fire and the offending record would vanish from the rejection log instead of appearing there with a reason — which is exactly the information the brief asks to be captured.

**Consequence.** Every disqualifying condition is expressed as a rule, never as a model constraint. The rules are the single place where publication criteria live.

---

## 3. Monetary amounts use `Decimal`

**Decision.** Salaries and converted values are `Decimal`, never `float`.

**Rationale.** Binary floating point cannot represent common decimal fractions exactly. With currency conversion applied before a threshold comparison, rounding error accumulates in ways that are hard to predict and impossible to reason about at the boundary — and boundary behaviour is precisely what a 100,000 threshold tests.

---

## 4. Hourly rates are not converted to annual for threshold checks

**Decision.** The salary rule branches on unit and applies a separate threshold to each: 100,000/year or 45/hour.

**Rationale.** The two thresholds in the brief are not equivalent. At 2,080 billable hours, 45/hour is 93,600 — below the annual threshold. Normalizing hourly to annual and comparing against 100,000 would therefore reject postings the brief intends to approve. The non-equivalence is treated as deliberate.

**Rejected alternative.** Normalize everything to an annual figure and use one threshold. Simpler rule, wrong results.

---

## 5. A separate field exists for sort ordering

**Decision.** `CanonicalJob.comparable_annual_usd` is computed during normalization and used **only** for sorting. It is never read by the salary rule.

**Rationale.** Sorting and deciding need different numbers. Sorting a list that mixes annual and hourly figures by raw amount is meaningless — an hourly rate of 62.50 would sort below every annual salary. But the comparable figure cannot drive the approval decision without reintroducing the error described in decision 4.

**Consequence.** The distinction between "a value used to compare" and "a value used to decide" is explicit in the model rather than implicit in usage.

---

## 6. Missing currency defaults to USD; currency is never inferred from location

**Decision.** A salary with no currency field is treated as USD, configured as an explicit constant. The posting's country is not used to guess.

**Rationale.** The thresholds in the brief are denominated in USD, so USD is the natural default. Inferring currency from country would be a silent heuristic that changes verdicts with no trace in the data: the London posting at 80,000 with no currency would clear the threshold as GBP (~101k) and fail it as USD. A rule that flips a decision deserves to be visible in configuration, not buried in a parser.

**Consequence.** That posting is rejected for both location and salary. Under the alternative it would be rejected for location alone. Both are defensible; this one is auditable.

---

## 7. A salary with no unit is inferred from its magnitude

**Decision.** A bare number below a configured ceiling (1,000) is treated as an hourly rate; at or above it, as an annual figure. The inference is recorded as a warning on the record.

**Rationale.** The feed contains a posting with `"salary": 62.5` and no unit. Rejecting it as unparseable would discard a posting that plainly qualifies. The sample data has no values between 65 and 20,000, so the margin around the ceiling is large.

**Known limitation.** The heuristic would misread a day rate — 1,200/day would be read as an annual salary. The ceiling is a configured constant so that the assumption is visible and adjustable rather than embedded in parsing logic.

**Rejected alternative.** Reject any salary without an explicit unit. Safer, but loses a posting the brief clearly expects to be approved.

---

## 8. Remote postings are scoped to their stated country

**Decision.** `remote: true` combined with a known country outside the US and Canada is treated as remote **within that country's market**, and rejected. Only a posting with no resolvable location (`null`, or the literal text `Remote`) is treated as remote-anywhere and passes the geography criterion.

**Rationale.** This is the most consequential interpretive choice in the system. The criterion reads "remote (anywhere) **or** in-person within the US or Canada", and the brief's forward-looking example — a remote UK posting becoming acceptable at 90k USD — only makes sense if remote UK postings are currently rejected.

**Consequence.** The two UK postings marked remote are rejected on geography. The staffing-firm posting with `location: null` passes geography despite being remote, which is counterintuitive but consistent with the same reading.

---

## 9. "Consulting Agency" is not a staffing firm

**Decision.** The company-type criterion is read literally. Only `Staffing Firm` disqualifies.

**Rationale.** The brief names staffing firms specifically. Consulting agencies are a distinct category in the feed and widening the criterion would be an unstated assumption.

**Consequence.** None, in practice — both consulting-agency postings in the sample are rejected on employment type regardless. The decision is recorded because it would matter on a different feed.

---

## 10. A missing posting date is not disqualifying

**Decision.** `posting_date` may be absent on an approved posting. It is not an approval criterion.

**Rationale.** The criteria list in the brief does not mention posting date. One sample posting has an empty date and otherwise qualifies.

**Consequence.** Sorting by date must handle absence. Postings with no date sort last regardless of sort direction, so that toggling the direction never surfaces a block of undated records at the top.

---

## 11. Rule evaluation is not fail-fast

**Decision.** Every rule runs against every posting. A rejected posting carries all violated criteria, not the first one encountered.

**Rationale.** The rejection log's value is diagnostic. Knowing that a posting failed on salary, geography and language at once tells you something about the feed that "failed on salary" does not.

---

## 12. Rejections are both logged and exposed

**Decision.** `RejectionLog` writes structured entries through the standard logging system and retains them in memory, where the API can read them. The UI shows approved and rejected postings as two tabs over the same data.

**Rationale.** The brief requires rejected postings to be logged with reasons. The log satisfies that requirement and remains the machine-readable contract. The UI tab is an addition, not a substitute: the reasons a feed fails are the most useful thing this system produces, and burying them in stdout wastes them.

**Consequence.** Rejected postings render with a different column set from approved ones, because a rejected posting may have no title, no location and no parseable salary.

---

## 13. Exchange rates sit behind a protocol

**Decision.** `CurrencyConverter` is a protocol. The implementation used here holds static rates in configuration (GBP 1.27, EUR 1.08, CAD 0.74).

**Rationale.** Rates are external data with a refresh cadence and a failure mode. Mocking them is permitted by the brief; hiding that they are mocked is not. The protocol marks the seam where a rate service would attach, and the static implementation is named for what it is.

**Note on verification.** The UK posting at 85,000 GBP converts to roughly 108k USD and therefore clears the salary threshold, failing only on geography. That posting is the acceptance test for conversion actually running: if it is rejected for salary as well, conversion is not being applied.

---

## 14. Unknown enum values degrade rather than raise

**Decision.** Employment type, company type, language, currency and unit all normalize casing and separators, and fall back to `UNKNOWN` for unrecognized input instead of raising.

**Rationale.** The feed is scraped, so unrecognized values are expected rather than exceptional. A parse failure on one field of one record must not abort a batch. Whether `UNKNOWN` is acceptable is a question for the rules — an unknown employment type is not full-time and is therefore rejected, with a reason.

---

## 15. Storage is in-memory behind a repository protocol

**Decision.** `JobRepository` is a protocol; the implementation holds postings in memory. Search, filter and sort are repository operations, not HTTP-layer logic.

**Rationale.** The brief permits mocked persistence but asks for production-ready structure. Keeping query operations in the repository means the API layer contains no domain logic and a database-backed implementation can be substituted without touching the pipeline, the rules or the routes.

---

## 16. Ingestion runs at application startup

**Decision.** The feed is read and processed during FastAPI's lifespan startup, from a path supplied by environment variable.

**Rationale.** Adequate for a system whose input is a static file, and it keeps the demo to one command. In production, ingestion would be a scheduled or event-driven job writing to a persistent store, decoupled from the API process lifecycle — the pipeline is already a standalone component with no dependency on FastAPI, so that change requires no restructuring.
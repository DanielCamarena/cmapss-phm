# 02_slide_content.md — 4-minute version

## Slide 1 — Title
Traceable Predictive Maintenance for NASA C-MAPSS

---

## Slide 2 — Problem (KEY SLIDE)
Benchmark RUL models produce point predictions.

But real PHM systems need:
- Uncertainty
- Decision logic
- Traceability

→ Prediction alone is NOT sufficient for deployment.

---

## Slide 3 — Task Context (FAST)
NASA C-MAPSS:
- Run-to-failure engine trajectories
- Multivariate sensor + operational data
- Goal: predict Remaining Useful Life

---

## Slide 4 — System Idea (CORE)
We build not just a model, but a system:

Predictive → Agent → Dashboard

- Predictive: RUL + confidence
- Agent: risk + recommendation
- Dashboard: user + audit

---

## Slide 5 — Predictive Layer (KEY INSIGHT)
Multiple models tested:
- GRU best RMSE
- RF deployed

Why?

→ Deployment requires stability, latency, and robustness  
→ not only best benchmark score

---

## Slide 6 — Agent Layer (DIFFERENTIATOR)
Transforms prediction into decision:

Inputs:
- RUL
- confidence
- service status

Outputs:
- risk level
- risk score
- recommendation

Deterministic and auditable

LLM: optional, never controls decisions

---

## Slide 7 — Dashboard (SYSTEM VIEW)
User interacts through:

- Summary → decision
- Analysis → uncertainty
- Scenarios → what-if comparison
- Audit → traceability

---

## Slide 8 — Results (KEY MESSAGE)
Best model ≠ deployed model

Tradeoff:
- GRU → best accuracy
- RF → best system behavior

→ Engineering constraints matter

---

## Slide 9 — Scenarios (INSIGHT)
What-if analysis:

Example:
- ΔRUL ≈ 0
- Risk unchanged

Meaning:
→ Not all changes matter  
→ System reveals sensitivity, not just prediction

---

## Slide 10 — Conclusion
This is not just a model.

It is a deployable PHM system with:
- calibrated prediction
- deterministic decisions
- traceability

Main lesson:
→ PHM quality ≠ RMSE alone
# Residual Risks

- Sequence challengers were trained on CPU with a lightweight configuration; they may improve with longer tuning cycles.
- The current inference path is optimized for single-record tabular integration; sequence-serving would need explicit history payload support.
- Condition-aware normalization remains a future enhancement for the most complex subsets.

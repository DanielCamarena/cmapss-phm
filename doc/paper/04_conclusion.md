# Conclusion

This project demonstrates that a PHM application for NASA C-MAPSS can be built as an integrated and traceable AI system rather than only as an isolated benchmark model.

The main scientific result is that a stable tabular champion (`rf`) was selected over a slightly better raw sequence model because the deployed application required not only predictive quality, but also:
- calibration
- deterministic fallback
- low serving complexity
- stable cross-subset behavior

The main engineering result is the integration of:
- predictive inference
- deterministic risk and recommendation logic
- scenario comparison
- interactive dashboard-based explanation
- technical auditability

This combination turns the project into a reproducible decision-support artifact that can be studied both as a predictive-maintenance system and as a trustworthy AI application.

Future work should deepen:
- local explanation quality
- scenario realism
- fleet-scale experimentation
- deployment-oriented evaluation beyond local execution

# Speaker Notes - 4-minute Presentation

## Slide 1 - Traceable Predictive Maintenance for NASA C-MAPSS
- This talk presents the project as a complete PHM application, not just a benchmark model.
- The key idea is to connect prediction, decision logic, and user-facing traceability in one system.

## Slide 2 - Problem
- This is the core motivation slide.
- A low error score is useful, but it still does not tell an operator how confident the system is, what action to take, or how to audit the decision.
- That gap is what this project addresses.

## Slide 3 - Task Context
- C-MAPSS gives us degradation trajectories at the engine-unit level.
- Each row combines cycle context, operational settings, and sensors, and the task is to estimate remaining useful life before failure.

## Slide 4 - System Idea
- This is the system-level contribution in one line.
- The predictive layer estimates RUL, the agent layer turns that into deterministic decision support, and the dashboard exposes both operator and audit views.

## Slide 5 - Predictive Layer
- This is the main predictive insight of the project.
- Even though GRU had the best benchmark score, RF was the better deployed choice because the system also had to satisfy stability and operational constraints.

## Slide 6 - Agent Layer
- The agent layer is what turns model output into something operationally meaningful.
- Importantly, the logic is deterministic, and the LLM is only optional support for interpretation rather than the source of truth.

## Slide 7 - Dashboard
- The dashboard is where the three-layer architecture becomes visible to users.
- It exposes a fast decision view, a deeper explanation layer, deterministic scenario comparisons, and a technical audit path.

## Slide 8 - Results
- This slide reinforces the central result from a system perspective.
- A deployable PHM system has to optimize for more than leaderboard performance, and that is why the final model choice differs from the best raw benchmark model.

## Slide 9 - Scenarios
- Scenario analysis is useful because it shows how the deployed model responds to controlled changes.
- In some cases the effect is very small, which tells us that the edited variables are locally insensitive or not central to the deployed model behavior.

## Slide 10 - Conclusion
- The final takeaway is that this project combines scientific modeling with engineering deployment discipline.
- What matters is not only predicting RUL, but making that prediction usable, explainable, and auditable in a real PHM workflow.

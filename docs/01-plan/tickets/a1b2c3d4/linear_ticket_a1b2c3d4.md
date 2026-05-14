---
id: a1b2c3d4
title: "EDA and Leakage-Safe Feature Engineering"
status: Ready for Dev
priority: High
order: 10
created: 2026-05-13
updated: 2026-05-13
links:
  - url: research/research_2026-05-13.md
    title: Research Document
  - url: plan/plan_2026-05-13.md
    title: Implementation Plan
  - url: ../linear_ticket_parent.md
    title: Parent Ticket
---

# Description

## Problem to solve
Understand the S6E5 dataset distributions, target relationships, and identify the most predictive features without introducing leakage.

## Solution
Perform automated EDA. Create features related to Race Progress, Position Changes, and Cumulative Degradation. Ensure no future information is used for predictions.

## Implementation Details
- Analyze `train.csv` and `test.csv`.
- Create a feature engineering pipeline.
- Validate feature importance using a fast baseline (LGBM).
- Export processed data artifacts.

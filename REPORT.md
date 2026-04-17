# ML for SCIP Separator Selection on Unit Commitment MIPs
## Project Report — April 2026

---

## 1. Problem Setup

**Goal:** Learn to select SCIP cutting plane separators (cutting planes) adaptively for Unit Commitment (UC) MIP instances, beating SCIP's default all-on separator strategy.

**Baseline:** `all_on` — SCIP's default behavior, enabling all 8 separators (gomory, cmir, clique, flowcover, zerohalf, strongcg, aggregation, impliedbounds) every round.

**8 separators considered:**
- `gomory`, `cmir`, `clique`, `flowcover`, `zerohalf`, `strongcg`, `aggregation`, `impliedbounds`

**Evaluation metric:** Relative solve time improvement vs `all_on`:
```
delta = (t_all_on - t_policy) / t_all_on
```
Positive = faster than SCIP default.

**Instance families:**
- `case57/S5/T24`: 50 instances, median solve time ~2s (trivially easy)
- `case118/S5/T24`: 50 instances, median solve time ~94s (meaningfully hard)

---

## 2. Pipeline Overview

```
Step 1: Generate UC instances (case57 + case118, S=5 scenarios, T=24 periods)
Step 2: Extract features
  2a. UC structural features (21-dim): generator cost, ramp rates, load stats, etc.
  2b. LP-based features (11-dim): root LP obj, cut tightening, #cuts added, LP iters
Step 3: Collect solve times for 20 configurations per instance (100 instances × 20 configs)
Step 4: Select subset A via greedy ERM; train MLP classifier (instance → best config)
Step 5: Online evaluation of MLP policy
Step 6: UCB adaptive separator (online bandit, optionally warm-started from MLP)
```

---

## 3. Results by Method

### 3.1 Subset A Selection (Step 3-4)

Using `all_on` as baseline, the greedy ERM selected:
```
A = {cmir_only, all_on}
Mean best delta over A: +5.2%
```

**Average delta per config vs `all_on` (top 5):**
| Config | Mean Δ |
|---|---|
| cmir_only | +1.99% |
| all_on | 0% (baseline) |
| mix_balanced | -2.09% |
| all_off | -2.68% |
| mix_uc_motivated | -3.30% |

Key observation: only `cmir_only` consistently beats `all_on`, and only by ~2%. The vast majority of configs make things worse.

---

### 3.2 Offline MLP Classifier (Step 4-5)

**Architecture:** 2-layer MLP (128 hidden, depth=2, dropout=0.1), trained on instance features → best config label.

**Version history:**
- v1/v2: case118/S5/T24 only → all instances structurally identical, near-zero feature variance, model predicts same class for everything
- v3: mixed case57 + case118 → 100 instances, 32-dim features (21 UC + 11 LP)

**v3 results:**
| Metric | Value |
|---|---|
| Val accuracy | 40% (barely above random for 3 classes) |
| Classes | cmir_only, all_on, all_off |
| Mean Δ vs all_on (live eval) | -74% (mean dominated by 1 blowup) |
| Median Δ vs all_on | +0.6% |
| % Positive | 65% |

**Failure mode:** Model collapsed to predicting `all_off` for every instance. Root cause: class imbalance (easy case57 instances make `all_off ≈ all_on`, pulling labels toward `all_off`), weak discriminative signal in features.

**Earlier v2 result (3-class: strongcg_only, gomory_only, all_on; 600s limit):**
| Metric | Value |
|---|---|
| Mean Δ vs all_on | +0.64% |
| Median Δ | +0.50% |
| % Positive | 55% |

This is the best MLP result observed.

---

### 3.3 Always-cmir_only Policy

No learning — just apply `cmir_only` to every instance (the best average config).

**On val set (from timing data):**
| Metric | Value |
|---|---|
| Mean Δ vs all_on | +0.2% |
| Median Δ | +0.8% |
| % Positive | 65% |

This essentially matches the MLP's best performance, which is a sign the classifier is not adding value.

---

### 3.4 Cut Quality Filtering (Step 7)

**Architecture:** A meta-separator registered at priority -1 (runs after all standard separators each round). It scores every generated cut using 4 metrics and calls `overrideCutSelection3` to keep only the top-k:
- Efficacy (weight 0.4): how violated is the cut?
- SCIP composite score (weight 0.3): SCIP's own quality heuristic
- Objective parallelism (weight 0.2): alignment with objective gradient
- Integer support (weight 0.1): fraction of nonzeros on integer variables

**Variants (all on t>5s hard instances, n=15):**

| Variant | Description | Mean Δ | Median Δ | % Positive | Worst case |
|---|---|---|---|---|---|
| Heuristic top-8 (no gate) | Always filter to 8 cuts | +8.4% | +12.0% | 66.7% | -45.9% |
| Heuristic top-8 (ratio=3.0 gate) | Only filter if n_cuts > 24 | +9.2% | +8.5% | 73.3% | -16.7% |
| ML top-8 (no gate) | MLP trained on lookahead labels | +2.4% | +2.4% | 60% | -55% |
| **Heuristic frac=35% (adaptive)** | **Keep top 35% ≥ 5 cuts** | **+13.2%** | **+10.6%** | **80.0%** | **-17.7%** |

**All-instance summary (n=20, including easy instances):**

| Variant | Mean Δ | Median Δ | % Positive |
|---|---|---|---|
| cut_filter (frac=35%) | +8.0% | +9.6% | 75% |
| combined (branch + cut filter) | +8.2% | +10.0% | 80% |

**Best individual instance:** seed3700038 — 167s → 70s (**+58%**)

**Gate mechanism (ratio=3.0):** The filter skips rounds where `n_valid_cuts ≤ top_k × 3.0 = 24`. When a round generates few cuts, those cuts are already targeted and filtering risks removing essential ones. Only large cut pools (>24 cuts) are filtered.

**Fraction-based mechanism (frac=35%, current best):** Instead of a fixed top-8 threshold with an explicit gate, keep `n_keep = max(5, int(n_valid × 0.35))` cuts per round. The filter naturally skips itself when `n_keep ≥ n_valid` (small pools). This replaces both the fixed cutoff and the gate with a single adaptive rule:
- Small pool (12 cuts): keep 5 (floor) — light filtering
- Medium pool (25 cuts): keep 9 — moderate filtering
- Large pool (50 cuts): keep 18 — aggressive filtering
- Tiny pool (8 cuts): n_keep=5 < 8 → still filters gently

This achieves the best all-around result: +13.2% mean, +10.6% median, 80% positive on hard instances, worst case -17.7%.

**Why ML doesn't beat heuristic:** Lookahead labels (LP bound improvement per cut) had near-zero variance for UC — the LP bound improvement from any individual cut at the root is tiny (max ~0.0000 after normalization). The model learned rankings similar to the heuristic. Labels based on B&B node reduction would be more informative.

---

### 3.5 UC-Aware Branching (Step 7)

**Architecture:** Custom `Branchrule` at priority 100,000 that identifies commitment variables u[g,t] (binary, obj=0) at B&B start and branches on the most-fractional one when available.

**Result:** Neutral (~0% change, median -0.1%). The LP relaxation for UC case118/S5/T24 is already tight enough that commitment variables are rarely fractional — SCIP would have branched on them anyway. The rule activated on <5% of branching decisions.

---

### 3.6 Linear UCB Adaptive Separator (Step 6)

**Architecture:** Disjoint LinUCB with N_ARMS=8 (one arm per separator). Each separation round, UCB selects ONE separator to enable. Context = LP state features (5-dim) + instance features (32-dim). Reward = bound improvement per row added, normalized by root LP objective.

**UCB variants evaluated (vs all_on):**
| Version | Notes | Mean Δ | Median Δ | % Positive |
|---|---|---|---|---|
| UCB v1 (per-instance, α=1.0) | Fresh UCB each instance | -247% | ~0% | 5% |
| UCB v3 (per-instance, α=0.1) | Lower exploration | -162% | ~0% | 5% |
| UCB v4 (root-node-only, α=0.1) | Fixed depth>0 bug | -6.7% | 0% | 10% |
| UCB v6 (node-count proxy reward) | Improved reward signal | -3.5% | 0% | 10% |
| UCB cross-instance (trained, α=0.1) | 80-instance training run, shared A/b | -5.0% | 0% | 5% |

**Cross-instance training details:**
- 80 training instances; UCB A/b matrices accumulated across all solves
- 46/80 easy instances (< 60s all_off) fell back to all_on; 34 got UCB treatment
- One catastrophic blowup: seed1600017 went from 60s → 3252s
- Best training instances: seed4700048 +25.4%, seed3000031 +22.4%, seed3800039 +17.8%
- Trained weights used in final eval on 20 val instances: mean Δ=-5%, 1/9 hard instances positive

**Best single UCB result:** `seed2500026` — 134s → 93s → **+30.5%** (observed in multiple eval runs)

---

### 3.7 Summary Table

| Method | Median Δ vs all_on | % Positive | Worst case | Notes |
|---|---|---|---|---|
| Always all_off | -1.2% | 26% | -17% | Cuts usually hurt slightly |
| Always cmir_only | +0.8% | 65% | -15% | Best naive policy |
| MLP v2 (3-class) | +0.5% | 55% | — | Best classifier result |
| MLP v3 (collapsed) | +0.6% | 65% | — | Predicted all_off for every instance |
| UCB (cross-instance) | 0% | 5% | -300%+ | Exploration cost never recovered |
| Cut filter, no gate | +12.0% | 67% | -46% | High median, bad worst case |
| Cut filter, ratio=3.0 gate | +8.5% | 73% | -17% | Safer but lower median |
| Cut filter, ML model | +2.4% | 60% | -55% | Labels too flat to help |
| **Cut filter, frac=35% adaptive** | **+10.6%** | **80%** | **-18%** | **Best overall — no explicit gate needed** |
| **Combined (branch + frac filter)** | **+10.0%** | **80%** | **-18%** | All-instance median; best positive rate |
| UC-aware branching | ~0% | 50% | — | LP already tight for u vars |

---

## 4. Diagnosis: When Does Each Method Work?

### 4.1 The Core Problem: Cuts Rarely Help UC Instances

The most important finding from the timing data:

| Population | % where cuts help (>1%) | Median cuts_delta |
|---|---|---|
| All instances | 26% | -0.8% |
| case118 only | 16% | -1.2% |
| case57 only | ~35% | ~0% |

**Cuts (any configuration) only significantly help ~16% of case118 instances.** The median case actually does slightly better WITHOUT cuts (all_off). This is the fundamental obstacle for all methods.

### 4.2 When Cuts DO Help Dramatically

The hardest instances show the largest upside:

| Instance | t_alloff | t_allon | Δ (cuts help) |
|---|---|---|---|
| seed4900050 | 1514s | 468s | **+69.1%** |
| seed600007 | 404s | 286s | **+29.3%** |
| seed1 | 233s | 207s | +11.2% |

Pattern: instances where `t_alloff > 300s` (very hard LP relaxation) benefit enormously from cuts. These likely have specific structural features (large integrality gap, many fractional variables) where cuts significantly tighten the LP bound.

### 4.3 Feature Informativeness

LP feature correlations with `delta_cmir` (best-case config):
| Feature | Correlation |
|---|---|
| lp_iters_alloff | -0.10 |
| lp_time_alloff | -0.10 |
| n_binvars | -0.08 |
| cut_tightening | -0.05 |

**All correlations are below 0.10.** The features we're computing do not predict which instances benefit from cut selection. The signal-to-noise ratio is too low for supervised ML to work reliably.

### 4.4 Why the UCB Underperforms

The UCB design selects **one arm (separator) per round**, while `all_on` runs all 8. This means:
- UCB does ~1/8th the cutting plane work per round
- If the chosen separator is weak (e.g., `impliedbounds`, `clique` for UC), the LP relaxation stays loose
- Result: more B&B nodes, slower solve

The reward signal (LP bound improvement per row) is a weak proxy for B&B solve time. A separator can add many tight cuts at the root yet still fail to reduce branching if those cuts don't align with the branching structure.

---

## 5. Remaining Improvement Directions for Cut Filtering

The gated heuristic filter achieves +8.5% median, 73% positive rate, worst case -17%. The remaining negatives all share the same failure mode: the filter discards cuts that are critical for pruning specific subtrees. Three directions could close this gap without increasing worst-case risk:

### 5.1 Fraction-Based top_k (Adaptive Filtering)

Instead of always keeping 8 cuts, keep a **fraction** of the pool (e.g., top 40%). This replaces the ratio gate with a cleaner mechanism:
- Small pool (12 cuts): keep 5 → similar to current gate behaviour
- Medium pool (25 cuts): keep 10 → moderate filtering
- Large pool (50 cuts): keep 20 → aggressive filtering

Implementation: replace `top_k` with `top_frac` in `CutQualitySepa`. Natural benefit: the filter scales with how many cuts SCIP thinks are worth generating, rather than a fixed absolute cutoff.

### 5.2 Parallelism-Aware Selection (Diversity Filtering)

The current scoring picks top-k cuts individually. But two high-scoring cuts with similar structure are redundant — adding both to the LP costs two LP pivots for roughly one cut's worth of bound tightening.

The custom SCIP exposes `filterCutWithParallelismAtRoot(cut1, cut2, is_good)` and `filterWithParallelismAtRoot`. After scoring, apply a greedy diversity pass:
1. Sort cuts by score
2. Greedily add cuts that are not too parallel to already-selected ones
3. Keep up to top_k diverse cuts

This gives both quality and diversity, potentially improving LP tightening per round without needing more cuts.

### 5.3 Separator-Type Pre-filtering

Looking at which separators consistently produce the cuts kept vs. discarded:
- **Good for UC:** `cmir`, `strongcg`, `gomory` — these produce cuts aligned with the temporal/capacity structure
- **Weak for UC:** `impliedbounds`, `clique` — these produce many low-quality cuts that inflate the pool

Disable the two weakest separators globally before the filter runs. This shrinks the pool from ~40 cuts to ~25-30 without touching quality cuts, then apply the filter to what remains. Fewer bad cuts to discard = filter needs to be less aggressive = lower risk of removing essential cuts.

### 5.4 B&B Node-Count Labels for ML

The current ML model was trained on root LP improvement as labels. These were near-zero for all cuts because the LP improvement from any single cut is tiny relative to the total objective.

Better label: **actual reduction in B&B nodes** when a cut is added vs. not added. Collect this by:
1. Solve instance with all cuts → record node count N_all
2. For each cut, solve without that cut → record node count N_minus_i
3. Label = (N_all - N_minus_i) / N_all

Expensive to collect (one solve per cut), but would give the ML model a direct signal for what actually matters. This is essentially the approach in the Khalil et al. (2016) cut selection work.

---

## 6. UC Problem Structure and Paths to True Improvement

### 5.1 Why Standard Cutting Planes Struggle on UC

UC MIPs have a specific structure that makes them different from general MIPs:

1. **Strong LP relaxations by default.** The time-coupling constraints (ramp up/down, min on/off) and the 2-stage stochastic structure already produce relatively tight LP relaxations. Many instances are solved optimally or near-optimally at the root node.

2. **Gomory cuts are not well-tailored to UC.** Standard Gomory cuts are derived from the simplex tableau and are general-purpose. UC has known polynomial-time-separable cut families (e.g., (p,q)-cuts for minimum up/down time, startup cuts) that exploit the binary commitment structure.

3. **The binding constraint is usually branching, not LP tightening.** For instances where cuts help (seed4900050, seed600007), the key is closing the LP-MIP gap before branching. For most UC instances, the gap is already small and the bottleneck is exploring the branching tree.

4. **Scenario coupling creates structure.** With S=5 scenarios sharing first-stage commitment variables, there's a block structure in the constraint matrix. This is exploitable but standard separators don't use it.

### 5.2 Paths to True Improvement

#### Path A: UC-Specific Cuts
Rather than selecting among 8 general-purpose separators, implement cuts designed for UC:
- **(p,q)-cuts for min up/down time:** These are facet-defining inequalities for the single-unit polytope and are polynomially separable. Papers: Rajan & Takriti (2005), Malkin (2003).
- **Startup/shutdown cuts:** Tighten the relationship between commitment and production variables.
- **Ramping cuts:** Strengthen bounds on production levels given commitment status.
These cuts are structurally motivated and will be tight more often than generic Gomory cuts.

#### Path B: Learn to Branch, Not to Cut
For UC, the branching strategy often matters more than cuts. Options:
- **Learning to branch (Khalil et al. 2016):** Train a GNN/MLP on the B&B tree state to predict which variable to branch on. This directly reduces tree size.
- **Strong branching with ML:** Use ML to approximate strong branching scores at low cost.
- **Variable ordering:** For UC, there's domain knowledge about which commitment variables are most fractional — committing generators near their on/off threshold first can prune the tree.

#### Path C: Instance-Level Cut Quality Prediction (Cathy Wu approach)
The L2Sep/NeurALCombo approach predicts cut quality at the LP level:
- Feature = individual cut vector (not instance-level features)
- Predict: will adding this cut reduce the solve time? (binary label)
- Select cuts greedily by predicted quality
- This is **cut-level prediction**, not config-level prediction

This is fundamentally different from what we've been doing. We've been predicting *which separator class to activate*, but the Wu approach predicts *which individual cut to keep* after generation. This is a much richer signal.

To implement this properly with SCIP:
- Use the `ConsHandler` or `Sepa` interface to intercept generated cuts
- Extract per-cut features: violation, support, density, orthogonality to other cuts
- Predict quality and filter before adding to LP

#### Path D: Better Features for Config Selection
If staying with the classifier approach, the current features don't have enough discriminative power. Better features:
- **Integrality gap after LP relaxation:** `(IP_obj - LP_obj) / |LP_obj|` — the most direct predictor of how much cuts can help
- **Number of fractional variables at root:** More fractional vars → cuts more likely to help
- **Dual degeneracy measure:** Measures LP stability; degenerate LPs often produce weak Gomory cuts
- **Structure-specific features:** Which generators are most often fractional? What's the load variance across scenarios?

#### Path E: More Diverse Training Data
Current limitation: our 100 instances are all `S=5, T=24`, varying only by random seed (load profile). This creates:
- Structural homogeneity (same #vars, #constraints in each case family)
- Near-zero variance in structural features
- The feature that actually matters (which specific generator is hard to commit) varies by seed but isn't captured

Better training data would include:
- Varying `S` (5, 10, 20, 30) — changes scenario structure
- Varying `T` (12, 24, 48) — changes temporal horizon
- Different case systems (case57 vs case118 vs case300)
- Real load data (not just generated profiles)
- Instances near the boundary between "cuts help" and "cuts don't help"

#### Path F: Two-Stage Policy
Rather than one policy for all instances, use a binary classifier first:
- Stage 1: Predict whether cuts will help at all (binary: yes/no based on LP gap)
  - If no → use all_off (fastest by ~1.2% median)
  - If yes → proceed to Stage 2
- Stage 2: Among cut-helping instances, predict the best cut family

This separates an easier binary question (will cuts help?) from the harder multi-class question (which cuts?).

### 5.3 Most Promising Direction

Given the data, the clearest opportunity is:
1. **Implement (p,q)-cuts for min up/down time** — these are problem-specific, provably strong, and don't require ML
2. **Use LP integrality gap as the primary feature** for predicting cut utility — it's the most direct signal
3. **Binary policy: cuts yes/no based on LP gap threshold** — simpler than multi-class classification and likely more reliable

The current project established that standard separator selection over 8 general-purpose cuts yields at most ~2% improvement on UC. The ceiling is low because the cuts aren't designed for this problem. UC-specific cuts or cut-level selection (Path C) would access a much higher ceiling.

---

## 6. Lessons Learned

1. **Start with data variance.** Homogeneous instances (same S, T, network) produce near-zero feature variance. ML needs diverse instances to learn anything.

2. **Measure the ceiling before building ML.** We should have computed `mean_best_delta_A` over all configs *before* building the ML pipeline. Finding out the ceiling is +5% on a good day means the ML can at best achieve +5%.

3. **Correlation analysis before modeling.** Features with <0.10 correlation to the target can't support a useful classifier. Run this check before training.

4. **UCB exploration cost is real.** For small eval sets (20 instances), bandit exploration overhead is never recovered. UCB is worth it only for production systems solving thousands of instances.

5. **Reward proxy choice matters.** LP bound improvement doesn't reliably predict B&B solve time. Finding a reward that does (e.g., tree size reduction proxy) is the key challenge for online methods.

6. **Class imbalance silently kills classifiers.** Mixed datasets with easy (near-zero variance in delta) and hard instances cause the model to collapse to predicting the majority class. Either balance classes explicitly or train on hard instances only.

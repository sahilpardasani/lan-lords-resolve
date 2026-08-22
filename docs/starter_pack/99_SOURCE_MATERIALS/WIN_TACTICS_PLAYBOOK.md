# WIN TACTICS — LAN LORDS / Resolve

Drop this in the kit as `14_WIN_TACTICS/WIN_TACTICS.md`. It assumes everything in the existing kit still happens; these are additions and edits ranked by win-probability-per-minute.

**How hackathons are actually won, in order:** (1) the demo works live, (2) every rubric line gets explicit points, (3) judges remember you over the next 12 teams, (4) you survive Q&A without a wound. Each tactic below names which lever it pulls.

---

## Summary table

| # | Tactic | Cost | Timeline slot | Owner | Win lever |
|---|--------|------|---------------|-------|-----------|
| 1 | Live counterfactual run | ~30 min | P05 build, P09 rehearse | Both | Q&A survival + memorability |
| 2 | Judge presses APPROVE | ~5 min | Pitch choreography | Product | Memorability |
| 3 | GB10 telemetry strip | ~30 min | P08 (timeboxed) | Tech | Rubric: sponsor hardware |
| 4 | Dollars on the primary case | ~30 min | Her first 90 min + P05 | Product | Rubric: business value |
| 5 | RUBRIC_MAP.md | ~20 min | 09:00–09:30 | Product | Rubric coverage |
| 6 | Pre-built UI/API scaffolds | Pre-event | Before the day | Tech | Demo works live |
| 7 | Fill hollow artifacts | Pre-event + P04 | Before + day-of | Both | Q&A survival |
| 8 | Morning stack verification | 10 min | 09:00 | Tech | Demo works live |

---

## 1. The counterfactual run — kill "isn't this hardcoded?" before it's asked

**The problem.** Your demo has `golden_facts.json`, a scripted event sequence, and a known ending. The single most likely fatal judge question is: *"How do I know the model decided anything? This looks like a movie."* JUDGE_QA.md currently has no answer to it.

**Exactly what to build:**

1. During P05 (12:00–12:45), your teammate creates a second evidence pack, `cases/market_access_variant_B/`, by copying pack A and changing **only two files**:
   - `deployment/deployment_receipts.jsonl` — node 08 now has a valid, confirmed receipt for `RLP-v2`.
   - `operations/premarket_events.jsonl` — the 97 anomaly messages are gone (or reduced to normal background noise).
2. Add an evidence-pack parameter to the case adapter (`case_adapter.py` already isolates this — it's a path swap, not new logic).
3. Expected behavior with pack B: Falsifier finds no unverified node, Judge returns `ADMISSIBLE` on a proceed-class candidate. Record this as a second golden expectation.
4. During P09 freeze (16:00–16:30), run pack B once and store its replay alongside pack A's.
5. In the pitch, after `OUTCOME VERIFIED` (~3:50), say one sentence: *"Same runtime, same prompts — we swap one evidence file and run it again."* Show pack B reaching a different disposition, live if time allows, replay if not.
6. Add to JUDGE_QA.md: **"Isn't this scripted?"** → *"The sequence you saw is one evidence pack. Here's the same code with one file changed reaching the opposite disposition. Decisions come from evidence, not from the script."*

**Why this wins.** Every judge has seen a rigged agent demo and is primed to discount yours. A live A/B on evidence is the cheapest possible proof of genuine model reasoning, and it flips the skeptical moment into your strongest one. It converts a point-losing question into a point-scoring answer, and it's the thing judges retell each other during deliberation ("they changed one file and it decided differently"). Cost: ~30 minutes of data editing, zero new architecture.

---

## 2. A judge's finger on the APPROVE button

**The problem.** In the current 5-minute run, judges watch for five minutes and touch nothing. The only click (`APPROVE HOLD`) is performed by you.

**Exactly what to do:**

1. Your `approval.py` / approval grant schema already carries an `approved_by` label. At 3:25 in the run of show, hand a judge the mouse (or a phone pointed at the UI if you serve it on the LAN) and ask them to approve the HOLD **by name**.
2. Their name goes into the approval grant, appears in the canonical journal, and shows on the `OUTCOME VERIFIED` screen: `Approved by: <Judge name> — 17:42:03`.
3. If tactic 1 is in play, offer the choice too: *"Which world do you want to see — the broken deployment or the clean one?"* Judge picks pack A or B.
4. Rehearse the handoff during P12 pitch prep so it costs under 10 seconds. Fallback if a judge declines: your teammate approves, no dead air.

**Why this wins.** People remember what they did far better than what they watched, and judges score from memory hours later. This also transforms "human-in-the-loop" from a claim on a slide into something a judge personally experienced — *their* name is in your audit journal. Zero code (the field exists), five minutes of choreography, and it's the kind of moment that decides ties.

---

## 3. Live GB10 telemetry in the header — make the sponsor hardware visibly work

**The problem.** This is an NVIDIA/Dell hardware event and every rubric will have a "use of platform" line, but all your performance work is parked in P1/P10 and produces no on-screen evidence. `External calls 0` proves what you're *not* using; nothing proves what you *are*.

**Exactly what to build:**

1. In the backend, a 2-second async loop that shells out to `nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits`, parses three numbers, and emits a `RUNTIME_STATS` SSE event (you already have the SSE channel — this is one more event type).
2. In `model_runtime.py`, wrap each model call with wall-clock timing and token counting from the server response; add tok/s and last-TTFT to the same event.
3. Render in the existing header bar: `GPU 87% | 41/128 GB | 62 tok/s | TTFT 0.4s`. Numbers move during the agent fan-out.
4. Timebox: 30 minutes inside P08 (15:15–16:00). If `nvidia-smi` parsing fights you, ship tok/s and per-role wall time only and drop GPU util — a moving number is the point.
5. In the pitch at 3:50 (architecture reveal), gesture at it once: *"Five roles, 128 GB unified memory, everything you're watching is computed on this box."*

**Why this wins.** It collects the sponsor-platform rubric points explicitly instead of by implication, it's live proof the demo isn't a video (a needle judges watch move can't be pre-recorded), and it pre-loads your Q&A: when someone asks about performance, the answer has been on screen the whole time. Hardware-company judges in particular reward teams that treat the hardware as a character in the story.

---

## 4. Put dollars on the primary case

**The problem.** The backup case has `$2.4M / $180K/day / $42K / $540K` — real stakes a nontechnical judge can score. The primary case says "opening delay has a business cost" with no number. The Business Impact Analyst role has nothing visible to compute, and your central thesis — the downside is *asymmetric* — is stated, never shown.

**Exactly what to do:**

1. In her first-90-minutes deliverable (TEAM_SPLIT already asks her for "five numbers that matter"), have her fix three synthetic figures and write them into `business/opening_constraints.md`:
   - cost of delayed open: e.g. `$85K per minute of held market access` (synthetic, labeled);
   - modeled exposure if the faulty node trades: anchored to the historical record — the real incident realized **~$10M per minute** ($460M over ~45 min), labeled `historical anchor`;
   - the candidate HOLD duration: 15 minutes.
2. `calculate_business_impact` (already in TOOL_CONTRACTS.md, already deterministic) computes: `HOLD cost ≈ $1.3M` vs `modeled exposure ≈ $150M+`. The Business Impact Analyst cites both with evidence IDs.
3. UI: two bars, wildly different lengths, in the OBJECTIVE panel. That picture *is* the asymmetry argument.
4. One pitch line at ~1:10: *"Waiting costs about a million. Being wrong costs about a hundred and fifty. That asymmetry is the whole case."*

**Why this wins.** Business-value rubric lines are usually scored by the judges least equipped to evaluate your state machine — numbers are how they vote. It also gives your strongest historical asset ($460M) a live counterpart inside the demo instead of only in the opening hook, and it makes the deterministic-calculator invariant ("business numbers are never hallucinated") demonstrable rather than asserted.

---

## 5. RUBRIC_MAP.md — engineer to the scoresheet

**The problem.** The timeline has "confirm rules/submission fields" as a 30-minute task, but no artifact forces every judging criterion to be explicitly answered. Teams reliably forfeit points on rubric lines they satisfied but never *showed*.

**Exactly what to build:**

1. Pre-event, add a template `01_STRATEGY/RUBRIC_MAP.md`:

   | Criterion | Weight | Where we score it (demo timestamp or artifact) | Proof | Owner | Status |
   |---|---|---|---|---|---|

2. At 09:00–09:30 she fills it from the published rubric. Every criterion must have a demo-timestamp or an artifact in the submission. Any row she can't fill becomes a named gap by 10:00, not a discovery at 17:00.
3. Re-sequence the 5-minute run so the **two highest-weighted criteria are hit inside the first two minutes** (judges' attention decays; late brilliance scores less).
4. Re-check the map at the 16:30 freeze — it becomes the submission-form checklist.

**Why this wins.** Hackathons are decided on scoresheets, not impressions. This converts pitch-editing debates into arithmetic ("innovation is weighted 30%, it currently appears at 4:25 — move it"), guarantees no forfeited lines, and takes 20 minutes from the person whose time is least contended at 09:00.

---

## 6. Pre-build the UI shell and API skeleton — buy back the two riskiest phases

**The problem.** P06 (agent loop, 105 min) and P08 (UI, 45 min) are your two most failure-prone integrations, and either failing drops you from demo level A/B (live) to C/D (replay/video). Your own RULES_AND_PROVENANCE.md explicitly permits pre-event *wireframes, schemas, interface contracts, and generic scaffolds* — you're not using that allowance where it matters most.

**Exactly what to build pre-event (into `EMPTY_REPO_SCAFFOLD/`):**

1. **Static UI shell**: one `index.html` implementing the full UI_SPEC layout and Refiant/ADMIT visual language, wired via `EventSource` to a tiny `fake_feed.py` that replays a hand-written `sample_events.jsonl` through the real event schema. No product logic — it renders events. Day-of P08 becomes "point it at the real backend," ~15 minutes instead of 45.
2. **FastAPI skeleton**: every route from API_CONTRACT.md returning `501`, plus the SSE plumbing, plus `scripts/smoke.py` (start server → `GET /api/health` → open SSE → assert one event). This file is referenced by your Makefile and currently doesn't exist.
3. **State-machine tests implemented, not skipped**: the legal/illegal transitions in RUNTIME_STATE_MACHINE.md are pure logic — write those ~8 tests against the spec now. P04 then starts with red tests to turn green instead of a blank file of `@skip`s.
4. Disclose all of it under `PRE_EVENT_ALLOWED_MATERIALS/` exactly as your provenance policy prescribes, and confirm the allowance with organizers in the kickoff conversation.
5. While you're in there: `13_REFERENCE_ONLY/PRE_EVENT_UI_MOCKUP...html` is **2.9 MB** — almost certainly embedded images/fonts. Extract the ~5 KB of CSS tokens you actually want and delete the rest from the working drive.

**Why this wins.** This is the single biggest mover of P(live demo), and live vs. replay is worth points on nearly every rubric line simultaneously — polish, technical execution, credibility in Q&A. It reclaims 30–40 minutes of the day for P06, the phase your kill-switch table already identifies as the most likely to slip, and it halves the risk concentrated in your one technical person.

---

## 7. Fill the hollow artifacts — your provenance pitch invites inspection, so survive it

**The problem.** You *market* auditability: SHAs, manifests, journals, "show the kickoff commit." A judge who takes the invitation will find `SOURCE_MANIFEST.csv` with every version/SHA/license cell empty, a test file that is 100% `@pytest.mark.skip`, and a Makefile target pointing at a script that doesn't exist. Hollow rigor reads worse than no rigor.

**Exactly what to do:**

1. Pre-event: fill every row of `SOURCE_MANIFEST.csv` (version/SHA, source URL, local path, sha256, license checked) as you load the SSD, then regenerate `CHECKSUMS/SHA256SUMS`. This is 30 minutes during downloads you're doing anyway.
2. `scripts/smoke.py` — created in tactic 6.
3. Extend JUDGE_QA.md with the four hard questions currently missing:
   - **"How is this different from a rules engine / workflow orchestrator?"** → *A rules engine can't read 97 unstructured emails, form a hypothesis, or attack its own answer. Resolve is LLM cognition doing evidence work inside a deterministic governance shell — the shell is the workflow engine part, and it's the part that never trusts the model.*
   - **"What happens on a case you didn't prepare?"** → point at Layer 3: a case adapter is evidence namespaces + tools + a simulator; the backup order case is the existence proof that the core generalizes.
   - **"Which parts did the model author vs. the harness?"** → open the journal live; model-authored content is evidence-ID-tagged agent output, everything else is deterministic.
   - **"Why not fine-tune?"** → 12 hours, and the thesis is governance around a stock model — the contract must hold even for a model you didn't train.
4. Make the one missing asset for the 3:50–4:25 architecture reveal: your teammate turns the SYSTEM_ARCHITECTURE ASCII into a single clean diagram (PNG/SVG) pre-event — diagrams are explicitly allowed materials. Right now that 35-second slot has nothing to show.

**Why this wins.** Q&A is where deliberation ties break, and these are the four questions most likely to be asked by the most senior judge in the room. Consistency between what you claim (auditable, rigorous) and what inspection finds is itself a scored impression — and the architecture diagram fills the only dead air in an otherwise tight run of show.

---

## 8. Ten-minute morning stack verification — protect every kill switch downstream

**The problem.** The entire P0 chain assumes the pinned stack, doc URLs, model IDs, and the validated serving profile match what's actually on the event box. All of these drift; a mismatch discovered at 10:30 burns the exact 90 minutes your kill-switch table can't spare.

**Exactly what to do:**

1. Extend the 0–5 minute block of GB10_FIRST_45_MINUTES.md: after `nvidia-smi`, run `--version` on every required stack component and diff against SOURCE_MANIFEST.csv expectations. Log to `evidence/preflight.txt`.
2. Query the box for its actual validated model profile name; if it differs from the one in MODEL_STRATEGY.md, **adopt the box's profile immediately** (your strategy doc already says this — make it a checklist line, not a principle).
3. Spot-check that two of your pinned offline docs match the installed versions' CLI flags (the env-var and command names are your most likely silent breakage).
4. Hard rule: any mismatch found at 09:05 triggers the fallback *now*, not at the 10:45 kill switch.

**Why this wins.** This buys nothing visible and prevents the most common way strong teams lose: a stack surprise at hour two that cascades through every gate. Ten minutes at 09:00 is the cheapest insurance in the whole plan — it protects the probability of *everything else on this list happening at all*.

---

## The one-line version

The existing kit maximizes P(don't fail). These eight moves add P(win): **6 & 8** protect the live demo, **3, 4, 5** collect rubric points explicitly, **1, 2** make you the team judges remember and can't dismiss as scripted, **7** wins the Q&A that breaks ties.

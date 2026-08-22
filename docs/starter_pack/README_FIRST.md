# HACK NYC Starter Pack — MongoDB + Team-5 Live Update

> **Archive.** Original starter packet that seeded the empty repo. Current product documentation is [../../README.md](../../README.md). Event file map: [../HACKATHON.md](../HACKATHON.md).

**Team:** LAN LORDS  
**Product:** Resolve  
**Status:** hackathon build is live

This pack patches the previous Resolve architecture lock with the **organizer-confirmed on-site rules**, the **required MongoDB integration**, the **3-coder + 2-business execution split**, and the **payment-outage primary demo**.

## Read now

1. `00_START_HERE_NOW.md`
2. `HACK_NYC_MASTER_PLAN.md`
3. `01_KICKOFF/ORGANIZER_RULES_CONFIRMED_2026-08-22.md`
4. `01_KICKOFF/GITHUB_BOOTSTRAP.md`
5. `07_TEAM/TEAM_SPLIT.md`
6. `02_BUILD_SPECS/ARCHITECTURE.md`
7. `02_BUILD_SPECS/MONGODB_P0.md`
8. `03_QA/PHASE_GATES.md`
9. `03_QA/P0_TEST_PLAN.md`
10. `CODEX_START_HACK_NYC.md` or `CURSOR_START_HACK_NYC.md`

## Organizer-confirmed changes

- at least **1 of NemoClaw/OpenClaw/OpenShell**, not all three;
- **MongoDB required**;
- inference runs locally on GB10;
- submission before 18:00;
- **no coding or prompting after 18:00**;
- slides due 19:00;
- pitch begins 19:30.

## P0

`local Qwen -> five reasoning roles -> deterministic permission -> exact approval -> bounded local action -> independent verify -> MongoDB audit/replay`

P0 sponsor component: **OpenShell**.

MongoDB: **audit substrate, not authority**.

## Primary demo

Payment success: **98.6% -> 79%**.

Bad candidate:
`GLOBAL 100% failover to Processor B`

Safe bounded candidate:
`US 40% failover`

Memorable proof:
approve `US 40%`, mutate to `GLOBAL`, old approval becomes invalid.

## Critical ownership

- Coder 1 = machine/model/OpenShell/Mongo availability
- Coder 2 = pure contract/approval/journal integrity
- Coder 3 = integration/MongoStore/simulator/API/UI
- Business 1 = primary case facts
- Business 2 = judge story/submission

No dual-writing on critical core files or primary facts.

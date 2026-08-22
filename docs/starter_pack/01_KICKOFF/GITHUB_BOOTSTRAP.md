# GitHub Bootstrap — Do This Once

The hackathon has started. Create a clean day-of repository now.

## 1. New repo

Create a new GitHub repository, e.g. `lan-lords-resolve-hacknyc`.

Do not import an existing Autonomous Labs or prior Resolve implementation.

## 2. Local initialization

From a clean new directory on the GB10 or the chosen shared development machine:

```bash
git init -b main
git config user.name "<your name>"
git config user.email "<your email>"

printf "# LAN LORDS / Resolve\n\nBuilt during Dell x NVIDIA HackNYC, Aug 22 2026.\n" > README.md
mkdir -p docs evidence cases resolve tests scripts static simulator

git add README.md
git commit -m "kickoff: initialize Resolve hackathon repo"
git tag kickoff-20260822
git rev-parse HEAD
```

Record that SHA in `evidence/kickoff_sha.txt`.

## 3. Remote

```bash
git remote add origin <GITHUB_REPO_URL>
git push -u origin main
git push origin kickoff-20260822
```

If GitHub/network is flaky, continue locally. GitHub is not the survival mechanism; the WD Git bundle is.

## 4. Engineering branches

Create only these three engineering branches from the kickoff SHA:

```bash
git switch main
git switch -c packet/runtime
git push -u origin packet/runtime

git switch main
git switch -c packet/core
git push -u origin packet/core

git switch main
git switch -c packet/integration
git push -u origin packet/integration

git switch main
```

Recommended ownership:
- `packet/runtime` -> Coder 1
- `packet/core` -> Coder 2
- `packet/integration` -> Coder 3

Business files should arrive as small reviewed commits to non-overlapping files. Do not create overlapping engineering branches.

## 5. Protected single-writer files

Only Coder 2 writes:
- `resolve/case.py`
- `resolve/contract.py`
- `resolve/approval.py`
- `resolve/journal.py`

Only Coder 3 writes:
- `resolve/mongo_store.py`
- `resolve/runtime.py`
- `resolve/context.py`
- `resolve/tools.py`
- `simulator/`
- `static/`
- `tests/test_end_to_end.py`

Business 1 owns facts:
- `cases/primary/case.yaml`
- `cases/primary/evidence/**`
- `cases/primary/EXPECTED.md`

Coder 3 consumes these facts but must not silently rewrite them to make integration pass.

## 6. Merge rule

Main receives small reviewed merges only.

Before merging:
```bash
pytest -q
git status --short
```

After merging:
```bash
git rev-parse HEAD
```

Save important working SHAs in `evidence/`.

## 7. Gate-E survival bundle

After the first successful end-to-end run:

```bash
git bundle create resolve-success.bundle --all
git bundle verify resolve-success.bundle
```

Copy the verified bundle and evidence directory to the WD immediately.

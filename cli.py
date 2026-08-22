"""
cli.py  --  Resolve live narrator (Coder 3, demo flow)

Runs a full incident and narrates each transition in the terminal, reading
REAL data from mongo_store. A projector-friendly backup to the web dashboard,
and a fast way to rehearse the demo story.

Usage:
    python cli.py            # run one incident, narrated
    python cli.py --audit    # show MongoDB aggregation views
    python cli.py --replay RUN_ID
    python cli.py --tamper RUN_ID
"""

import sys
import time

from resolve import runtime, mongo_store

# ANSI colors (works in any terminal / projector)
C = {"dim": "\033[2m", "b": "\033[1m", "red": "\033[91m", "grn": "\033[92m",
     "ylw": "\033[93m", "blu": "\033[94m", "cyn": "\033[96m", "x": "\033[0m"}


def c(txt, col):
    return f"{C[col]}{txt}{C['x']}"


def line(txt="", pause=0.0):
    print(txt)
    if pause:
        time.sleep(pause)


def bar():
    line(c("─" * 60, "dim"))


def narrate_run():
    mongo_store.connect()
    mongo_store.ensure_indexes()

    bar()
    line(c("  RESOLVE", "b") + c("  ·  deterministic permission around cognition", "dim"))
    bar()

    h = mongo_store.health()
    line(f"  MongoDB: {c(h['mongodb'] if 'mongodb' in h else ('ONLINE' if h.get('online') else 'OFFLINE'),'grn')}"
         f"   contract core: {c('OPERATIONAL','grn')}", pause=0.4)

    line("\n  " + c("▶ incident detected", "cyn") +
         "  payment success 98.6% → 79%", pause=0.6)

    # execute the real run
    result = runtime.run()
    run_id = result["run_id"]

    # narrate from the recorded journal
    rep = mongo_store.replay_run(run_id)
    for step in rep["timeline"]:
        et = step["event_type"]
        sm = step["summary"]
        seq = step["sequence"]
        if et == "AI_PROPOSAL":
            line(f"   {c('· AI proposes','blu')}   {sm}", pause=0.5)
        elif et == "CONTRACT_EVALUATED":
            if "BLOCKED" in sm:
                line(f"   {c('✗ CONTRACT: BLOCKED','red')}   {sm}", pause=0.7)
            elif "WAITING_HUMAN" in sm:
                line(f"   {c('⏸ CONTRACT: needs human','ylw')}   all gates pass", pause=0.6)
            else:
                line(f"   · contract   {sm}", pause=0.4)
        elif et == "APPROVAL_ISSUED":
            line(f"   {c('✓ human approves','grn')}   {sm}", pause=0.5)
        elif et == "ACTION_COMMITTED":
            line(f"   {c('· action committed','blu')}   bounded failover", pause=0.5)
        elif et == "VERIFIED":
            line(f"   {c('✓ verified','grn')}   {sm}", pause=0.5)
        elif et == "INCIDENT_DETECTED":
            pass  # already narrated above

    # chain + persistence proof
    chain = rep["chain"]
    line()
    line(f"   journal chain: "
         f"{c('intact','grn') if chain['intact'] else c('BROKEN','red')}"
         f"  ({chain['events']} events)")
    line(f"   " + c(f"MongoDB LOCAL | journal events: {result['journal_events']} | replay: ready", "cyn"))
    bar()
    line(f"  run_id: {c(run_id,'dim')}")
    line(f"  {c('BLOCKED','red')} → {c('WAITING_HUMAN','ylw')} → "
         f"{c('committed','grn')} → {c('verified','grn')}")
    bar()
    return run_id


def show_audit():
    mongo_store.connect()
    a = mongo_store.audit_views()
    bar(); line(c("  MongoDB audit views (aggregation)", "b")); bar()
    for k, v in a.items():
        line(f"   {k:<28} {c(str(v),'cyn')}")
    bar()


def show_replay(run_id):
    mongo_store.connect()
    rep = mongo_store.replay_run(run_id)
    bar(); line(c(f"  Replay: {run_id}", "b")); bar()
    for s in rep["timeline"]:
        line(f"   seq {s['sequence']:>2}  {c(s['event_type'],'blu'):<28} {s['summary']}")
    bar()


def show_tamper(run_id):
    mongo_store.connect()
    mongo_store.connect().journal_events.update_one(
        {"run_id": run_id, "sequence": 2},
        {"$set": {"payload": {"tampered": True}}})
    r = mongo_store.verify_journal_chain(run_id)
    bar()
    if r["intact"]:
        line(c("   chain still intact (unexpected)", "ylw"))
    else:
        line(c(f"   ✗ TAMPER DETECTED at seq {r['broken_at_sequence']}  ({r['reason']})", "red"))
    bar()


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        narrate_run()
    elif args[0] == "--audit":
        show_audit()
    elif args[0] == "--replay" and len(args) > 1:
        show_replay(args[1])
    elif args[0] == "--tamper" and len(args) > 1:
        show_tamper(args[1])
    else:
        print(__doc__)

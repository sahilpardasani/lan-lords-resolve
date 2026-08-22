# Resolve — State Machine Reference

Recommended P0 states:
`NEW -> INVESTIGATING -> CANDIDATE -> CHALLENGED -> CONTRACTED -> MORE_EVIDENCE | BLOCKED | WAITING_HUMAN | ADMISSIBLE -> COMMITTING -> VERIFYING -> CLOSED | RECONCILE | WATCHING`

## Rules
- illegal transitions fail closed;
- `BLOCKED` and `MORE_EVIDENCE` cannot commit;
- `WAITING_HUMAN` cannot commit without a valid exact ApprovalGrant;
- candidate mutation after approval returns to `CONTRACTED` and invalidates approval;
- cancellation blocks later model/tool/action admission;
- unknown commit outcome enters `RECONCILE`, never blind auto-retry;
- `COMMITTING` is not success;
- `CLOSED` requires verification success;
- `WATCHING` may reopen only on a configured material condition.

The canonical journal is the source of run truth; UI state is projected from events.

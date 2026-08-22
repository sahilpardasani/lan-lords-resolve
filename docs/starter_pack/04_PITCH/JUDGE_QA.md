# Resolve — Judge Q&A

## Isn't this scripted?
“The demo uses one evidence pack. We keep the same core and role logic, change one material fact, and the disposition changes. We also run invariance tests where irrelevant wording changes do *not* change the result.”

## Isn't this just five analysts?
“No. Four specialist reasoning roles investigate/propose/challenge and `main` orchestrates. The decisive difference is that none can authorize the action. A deterministic contract checks intent, evidence, constraints, consequence, reversibility, rehearsal, authority and verification before anything can proceed.”

## Why no LLM Judge?
“Because agents voting on whether agents should act is still self-authorization. We use the model for ambiguous cognition and deterministic code for permission consequences once the relevant facts are explicit.”

## How is it different from a rules engine?
“The permission shell intentionally behaves like a strict rules engine. The LLM layer does the part fixed rules are poor at: reading messy local evidence, forming competing hypotheses, finding discriminating evidence, and proposing bounded alternatives.”

## How do you know it doesn't always block?
“We have positive, negative and genuinely ambiguous controls. We measure false permissive decisions and over-conservative decisions separately.”

## How do you know it isn't tuned to this one case?
“The same `contract.py` consumes different `case.yaml` contracts. The loss-leader objective test changes the authorized objective and tests INTENT without changing the permission kernel; the other synthetic packs test different domains.”

## What happens if a local document tells the agent to ignore the rules?
“Retrieved text is evidence, not runtime instruction. It can be quoted/cited but cannot change capabilities, contract logic or authorization.”

## What if a judge approves and the action changes afterward?
“Approval is bound to the exact action/parameters and evidence-state fingerprint. Material mutation invalidates it immediately.”

## What if commit timing is uncertain?
“Unknown side-effect outcomes reconcile; we do not blindly retry and risk a duplicate effect.”

## Why five roles if one model?
“They are capability/context envelopes over one weight set, which reduces memory/serving risk. The architecture depends on one endpoint, not five model copies.”

## Why local?
“These workflows include contracts, source, logs, SOPs and operational state. Local inference keeps them on the GB10 and lets us prove the agent has no cloud-model runtime dependency.”

## Is the whole system deterministic?
“No. The LLM remains nondeterministic. Our claim is deterministic permission/control around nondeterministic cognition.”

## Why not fine-tune?
“The hackathon thesis is a replaceable stock local model behind a stable permission contract. We want the safety property to survive model replacement rather than depend on one tuned checkpoint.”

## What does `doctor.py` do?
“It diagnoses the failing layer and can perform narrow operational repairs such as restarting a known process or resetting disposable simulator state. It is explicitly forbidden from weakening contract logic, tests, evidence or expected outcomes.”

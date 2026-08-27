/*
 * Zero-cost showcase adapter.
 *
 * The original Resolve_Showcase.html talks to the GB10 FastAPI runtime. This
 * adapter preserves that frontend and replays the repository's canonical,
 * verified 500-record workflow entirely in the browser. It does not claim to
 * run Qwen, MongoDB, or OpenShell on the hosted page.
 */
(() => {
  const nativeFetch = window.fetch.bind(window);
  const gates = {
    blocked: {
      intent: "PASS", evidence: "PASS", constraints: "FAIL", consequence: "FAIL",
      reversibility: "UNKNOWN", rehearsal: "UNKNOWN", authority: "FAIL", verification: "PASS"
    },
    evidence: {
      intent: "PASS", evidence: "UNKNOWN", constraints: "PASS", consequence: "PASS",
      reversibility: "PASS", rehearsal: "UNKNOWN", authority: "UNKNOWN", verification: "PASS"
    },
    human: {
      intent: "PASS", evidence: "PASS", constraints: "PASS", consequence: "PASS",
      reversibility: "PASS", rehearsal: "PASS", authority: "PASS", verification: "PASS"
    }
  };

  const bounded = {
    action_type: "payments.failover",
    target: "processor_b",
    parameters: {
      country: "US",
      networks: ["visa", "mastercard"],
      maximum_transaction_value_usd: 5000,
      traffic_share: 0.174
    }
  };

  const state = {
    runId: null,
    phase: "IDLE",
    qwenCalls: 0,
    candidate: structuredClone(bounded),
    approval: null,
    events: [],
    commitId: null,
    effectCount: 0
  };

  const clone = value => structuredClone(value);
  const json = (payload, status = 200) => new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": "application/json" }
  });
  const hash = value => {
    let n = 2166136261;
    for (const ch of value) n = Math.imul(n ^ ch.charCodeAt(0), 16777619);
    return (n >>> 0).toString(16).padStart(8, "0").repeat(8);
  };
  const addEvent = (eventType, payload) => {
    const sequence = state.events.length + 1;
    const previous = state.events.at(-1)?.event_hash_or_mac || "0".repeat(64);
    const event = {
      event_id: `evt_showcase_${sequence}`,
      case_id: "payment_failover_001",
      run_id: state.runId,
      sequence,
      timestamp: new Date().toISOString(),
      event_type: eventType,
      payload,
      prev_hash: previous,
      event_hash_or_mac: hash(`${previous}:${sequence}:${eventType}:${JSON.stringify(payload)}`)
    };
    state.events.push(event);
  };
  const evaluation = (kind, disposition, reasons = []) => ({
    candidate_fingerprint: hash(JSON.stringify(state.candidate)),
    case_fingerprint: hash("payment_failover_001"),
    evidence_fingerprint: hash(kind === "evidence" ? "stage_1" : "stage_2"),
    state_fingerprint: hash(state.phase),
    decision_fingerprint: hash(`${kind}:${disposition}`),
    required_authority: "payments_operations_lead",
    consequence_class: "material_payment_routing_change",
    human_approval_required: true,
    contract_result: {
      gates: clone(gates[kind]),
      disposition,
      reason_codes: reasons,
      policy_reason_codes: reasons
    }
  });
  const publicState = () => ({
    run_id: state.runId,
    case_id: "payment_failover_001",
    phase: state.phase,
    qwen_call_count: state.qwenCalls,
    current_candidate: clone(state.candidate),
    current_evaluation: state.currentEvaluation,
    blocked_evaluation: state.blockedEvaluation,
    roles: clone(state.roles || []),
    approval: state.approval && clone(state.approval)
  });
  const replay = () => ({
    run_id: state.runId,
    events: clone(state.events),
    integrity: { valid: true, status: "VALID", failed_sequence: null },
    state: publicState()
  });

  const start = () => {
    state.runId = `showcase_${Date.now().toString(36)}`;
    state.phase = "MORE_EVIDENCE_REQUIRED";
    state.qwenCalls = 5;
    state.candidate = clone(bounded);
    state.approval = null;
    state.events = [];
    state.commitId = null;
    state.effectCount = 0;
    state.roles = [
      { role: "main", summary: "Coordinated a bounded incident-response loop over the canonical local evidence." },
      { role: "scout", summary: "Found Processor A degradation and identified stale Processor B capacity evidence." },
      { role: "investigator", summary: "Supported processor degradation as the strongest explanation for the authorization drop." },
      { role: "planner", summary: "Proposed a bounded US Visa/Mastercard reroute covering 17.4% of total traffic." },
      { role: "challenger", summary: "Rejected the unsafe GLOBAL 100% failover against typed policy constraints." }
    ];
    state.blockedEvaluation = evaluation("blocked", "BLOCKED", ["COUNTRY_NOT_ALLOWED", "TRAFFIC_CAP_EXCEEDED"]);
    state.currentEvaluation = evaluation("evidence", "MORE_EVIDENCE_REQUIRED", ["CURRENT_PROCESSOR_B_CAPACITY_REQUIRED"]);
    addEvent("CASE_LOADED", { case_id: "payment_failover_001", cohort_records: 500 });
    addEvent("EVIDENCE_READ", { stage: 1, status: "STALE_CAPACITY" });
    state.roles.forEach(role => addEvent("ROLE_COMPLETED", role));
    addEvent("CANDIDATE_PROPOSED", { country: "GLOBAL", traffic_share: 1 });
    addEvent("CONTRACT_EVALUATED", { disposition: "BLOCKED", reason_codes: ["COUNTRY_NOT_ALLOWED", "TRAFFIC_CAP_EXCEEDED"] });
    addEvent("CANDIDATE_PROPOSED", { country: "US", traffic_share: 0.174 });
    addEvent("EVIDENCE_REQUESTED", { reason: "CURRENT_PROCESSOR_B_CAPACITY_REQUIRED" });
    return publicState();
  };

  const addEvidence = () => {
    state.phase = "WAITING_HUMAN";
    state.currentEvaluation = evaluation("human", "WAITING_HUMAN");
    addEvent("EVIDENCE_ADDED", { capacity: "CURRENT", policy_version: 14 });
    addEvent("REHEARSAL_COMPLETED", { status: "PASS", recoveries: 87, modeled_success_rate: 0.964 });
    addEvent("CONTRACT_EVALUATED", { disposition: "WAITING_HUMAN", technical_gates: "PASS" });
    return publicState();
  };

  const approve = body => {
    state.phase = "APPROVED";
    state.approval = {
      approval_id: `approval_${Date.now().toString(36)}`,
      status: "VALID",
      approver: body.approver,
      candidate_fingerprint: hash(JSON.stringify(bounded)),
      used: false
    };
    addEvent("APPROVAL_GRANTED", {
      approver: body.approver,
      candidate_fingerprint: state.approval.candidate_fingerprint,
      ttl_minutes: 10
    });
    return publicState();
  };

  const mutate = body => {
    state.phase = "APPROVAL_INVALIDATED";
    state.candidate = clone(bounded);
    state.candidate.parameters.traffic_share = Number(body.traffic_share);
    addEvent("APPROVAL_INVALIDATED", { from_traffic_share: 0.174, to_traffic_share: Number(body.traffic_share), model_invoked: false });
    return publicState();
  };

  const restore = () => {
    state.phase = "APPROVED_RESTORED";
    state.candidate = clone(bounded);
    state.currentEvaluation = evaluation("human", "WAITING_HUMAN");
    addEvent("CANDIDATE_RESTORED", { candidate_fingerprint: hash(JSON.stringify(bounded)), approval_status: "VALID" });
    return publicState();
  };

  const execute = body => {
    const duplicate = state.commitId === body.commit_id;
    if (!duplicate) {
      state.commitId = body.commit_id;
      state.effectCount = 1;
      state.phase = "COMMITTED_UNVERIFIED";
      if (state.approval) { state.approval.status = "CONSUMED"; state.approval.used = true; }
      addEvent("COMMIT_ADMITTED", { commit_id: body.commit_id, approval_consumed: true });
      addEvent("COMMIT_SENT", { commit_id: body.commit_id, effect_applied: true, verification: "NOT_PERFORMED" });
    }
    return { run_id: state.runId, commit_id: body.commit_id, effect_count: 1, status: "EFFECT_APPLIED", idempotent_replay: duplicate };
  };

  const verify = () => {
    state.phase = "VERIFIED";
    const observed = {
      total: 500,
      successful: 482,
      success_rate: 0.964,
      processor_b_routed: 87,
      processor_b_route_share: 0.174,
      unauthorized_processor_b_routes: 0,
      policy_violations: 0
    };
    addEvent("VERIFICATION_OBSERVED", { status: "VERIFIED", observed, separate_state_read: true });
    addEvent("RUN_VERIFIED", { status: "VERIFIED" });
    return { status: "VERIFIED", observed, separate_state_read: true };
  };

  const parseBody = init => {
    try { return init.body ? JSON.parse(init.body) : {}; }
    catch { return {}; }
  };

  window.fetch = async (input, init = {}) => {
    const url = new URL(typeof input === "string" ? input : input.url, location.href);
    if (url.origin !== location.origin) return nativeFetch(input, init);
    const path = url.pathname;
    const method = (init.method || "GET").toUpperCase();
    const body = parseBody(init);

    if (method === "POST" && path === "/run") return json(start());
    if (method === "POST" && /\/runs\/[^/]+\/evidence$/.test(path)) return json(addEvidence());
    if (method === "POST" && /\/runs\/[^/]+\/approve$/.test(path)) return json(approve(body));
    if (method === "POST" && /\/runs\/[^/]+\/mutate$/.test(path)) return json(mutate(body));
    if (method === "POST" && /\/runs\/[^/]+\/restore$/.test(path)) return json(restore());
    if (method === "POST" && /\/runs\/[^/]+\/execute$/.test(path)) return json(execute(body));
    if (method === "POST" && /\/runs\/[^/]+\/verify$/.test(path)) return json(verify());
    if (method === "GET" && /\/runs\/[^/]+\/replay$/.test(path)) return json(replay());
    if (method === "GET" && path === "/containment") return json({
      status: "PASS",
      public_external_http: "BLOCKED",
      local_qwen: "PASS",
      local_resolve: "PASS"
    });
    return nativeFetch(input, init);
  };
})();

# FX notification operational research log

## 2026-10-01

### USDCAD alert lifecycle
- Completed signal candle: 2026-09-30 16:00 UTC
- Entry candidate: next H4 open, 2026-09-30 20:00 UTC
- The live state report at the next completed H4 showed the signal as TRIGGERED even though the one-candle entry window had already passed.
- Root cause: the replay branch intentionally recognized that a post-signal candle should expire the trigger, but stopped at the final candle instead of resetting the state.
- Fix: stale TRIGGERED states now expire immediately when any completed candle exists after the signal. A trigger is considered an active entry candidate only when the signal candle is the latest completed H4 candle.

### Durable alert duplication
- The same USDCAD signal was present as GitHub issues #1, #2, and #3.
- Root cause: notification publishing retried non-idempotent POST requests after uncertain network/API responses. A POST may have created the issue even when the client did not receive the response, so a blind retry could create another identical issue.
- Fix: publisher now checks all existing issues by exact title before publishing and re-checks existence after any uncertain POST failure before attempting another POST.
- Issues #2 and #3 were closed with reason duplicate; issue #1 remains the durable alert record.

### Research interpretation
- This is an operational integrity correction, not a change to the frozen H4 entry rule.
- The USDCAD signal itself remains a historical notification event; the entry window is the next H4 open only.
- No claim is made here about subsequent profitability.

### Next research branch
- Continue the isolated causal price-structure study on H4/H1.
- Quantify notification lateness/entry quality separately from signal validity, especially signal-candle extension, ATR-normalized extension, distance from EMA20, and post-entry MFE/MAE.
- Do not modify the frozen H4 notification rule until those tests pass Discovery -> Validation -> OOS and pair-robustness checks.

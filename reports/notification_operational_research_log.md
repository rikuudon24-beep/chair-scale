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

## Entry-quality audit result (2026-10-01)

The first OOS pass used 52 frozen-rule signals (29 long, 23 short) and next-H4-open entry replay.

- LONG, all signals: +50 reached before stop in 44.83%; mean realized outcome +50-target/stop-first ledger = -2.44 pips.
- LONG, signal candle range 0.75-1.25 ATR: 15 trades; +50 hit 60.00%; mean +16.53 pips.
- LONG, signal candle range >1.25 ATR: 10 trades; +50 hit 40.00%; mean +6.33 pips.
- SHORT, all signals: +50 hit 43.48%; mean -10.74 pips.
- SHORT, signal candle range 0.75-1.25 ATR: 9 trades; +50 hit 44.44%; mean +8.83 pips.
- SHORT, signal candle range >1.25 ATR: 10 trades; +50 hit 60.00%; mean +12.95 pips.
- For SHORT, touch-to-signal movement >1 ATR was materially worse than <=1 ATR in this OOS sample; for LONG the same split was less decisive.
- Very small buckets (n=1 to 4) are not treated as evidence.

Interpretation: the USDCAD-style concern cannot be solved by simply rejecting every large signal candle. The first OOS evidence is direction-dependent and suggests that signal-candle size, touch-to-signal extension, and EMA20 distance should be tested jointly rather than used as a blanket late-entry filter. The frozen notification rule remains unchanged.

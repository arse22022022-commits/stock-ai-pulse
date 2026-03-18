import json

for label, path in [("LOCALHOST", "bc_mi_response.json"), ("CLOUD", "bc_mi_cloud.json")]:
    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"{'='*50}")
    try:
        with open(path, "r") as f:
            d = json.load(f)
    except Exception as e:
        print(f"  ERROR: {e}")
        continue

    cr = d["current_regime_ret"]
    rr = d["risk_reward_ratio"]
    stats = d["state_stats_ret"]
    verdict = d["recommendation"]["verdict"]
    score = d["recommendation"]["score"]

    print(f"  Current regime_ret: {cr}")
    print(f"  API risk_reward_ratio: {rr:.6f}")
    print(f"  Verdict: {verdict} (score: {score})")
    print()
    for s in stats:
        tag = " <<< CURRENT" if s["regime"] == cr else ""
        print(f"    R{s['regime']}: mean={s['mean']:.6f}% std={s['std']:.6f}% rr={s['ratio_rr']:.6f}{tag}")

    cs = [s for s in stats if s["regime"] == cr][0]
    print()
    print(f"  SIGN CHECK: mean={cs['mean']:.6f}, rr={cs['ratio_rr']:.6f}")
    if cs["mean"] > 0 and cs["ratio_rr"] < 0:
        print("  !!! BUG: positive mean but negative R/R !!!")
    else:
        print("  OK: signs consistent")

# Cloud Migration — Service Dependency & Latency Toolkit

Purpose: before moving these services to a new cloud, know **exactly what each
service talks to over the network**, and **measure the latency to each
dependency** so it can be compared before vs. after the move.

## Contents

| File | What it is |
|------|------------|
| `oms-services-order-dependencies.md` | Order service — full dependency inventory |
| `oms-services-product-dependencies.md` | Product service |
| `oms-services-content-dependencies.md` | Content service |
| `oms-service-payment-dependencies.md` | Payment service |
| `oms-services-dependencies.md` | oms-services (mono workers + HTTP) |
| `endpoints.tsv` | Machine-readable manifest the script consumes (all services) |
| `check-latency.py` | Latency probe + before/after compare (Python 3, stdlib only) |

Dependencies were extracted **from configuration** (`.env`, `config.yaml`,
`config/config.go`) — env vars are the source of truth for what a service
connects to. Each file marks every dependency **CRITICAL** (synchronous, on the
request path) or **BACKGROUND** (Kafka consumers, cron, workers, alerting).

## How to measure latency

> Run the probe **from where the service actually runs** — `kubectl exec` into
> the pod, or a host in the same VPC/region. Latency is measured relative to
> where the script executes.

It measures, per endpoint: DNS resolution, TCP connect RTT (×N samples →
min/avg/p95/max), and optionally a TLS handshake. TCP connect time is the metric
that actually changes when you move cloud region/provider.

```bash
cd docs/ai/migration

# 1) Baseline in the CURRENT cloud (one service, or omit --service for all)
python3 check-latency.py --service oms-services-order --label old --out baseline.csv

# 2) After cutover, from the NEW cloud
python3 check-latency.py --service oms-services-order --label new --out new.csv

# 3) Diff — regressions flagged ⚠ (>+5ms or >+25%), improvements ✓
python3 check-latency.py --compare baseline.csv new.csv
```

Useful flags: `--samples 20` (more stable averages), `--timeout 2`,
`--tls` (also time the TLS handshake on :443 endpoints).

## Important caveats before you trust the numbers

1. **Targets in `endpoints.tsv` are SIT-inferred from config (June 2026).**
   Verify and replace the `target` column with the real host:port for the
   environment you are testing. The order service's config used placeholders
   (`product-service-host`), so its targets were inferred from sibling services.
2. **MongoDB Atlas & some hosts use SRV / VPC-endpoint names** that don't accept
   a TCP connection on the bootstrap name directly (you'll see `0/N` for mongo).
   Point the target at a resolved shard host, or treat DNS time as the signal.
3. **Kafka `KAFKA_BROKERS`** is a bootstrap host; real traffic also hits the
   per-partition brokers it returns. The bootstrap RTT is a good proxy.
4. **Run from inside the VPC.** Internal hosts (`*-internal-api`, RDS,
   ElastiCache, OpenSearch) are not reachable from the public internet — a
   laptop run will show timeouts for those; that's expected.
5. The probe only measures **reachability + latency**, not auth/throughput.
   It opens and closes a socket; it does not send app-level requests.

## What moves vs. what stays

When planning the cutover, classify each dependency:
- **Moving with the service** (e.g. its own MySQL) → latency should stay low (same new region).
- **Staying put** (e.g. Confluent Cloud Kafka, Algolia, Omise, MongoDB Atlas, Braze) → latency depends on the new cloud's distance to those providers; these are the rows to watch in the compare.
- **Shared internal services** (product, customer, promotion…) → depends on whether they migrate in the same wave. Cross-cloud calls during a phased migration are the biggest latency risk.

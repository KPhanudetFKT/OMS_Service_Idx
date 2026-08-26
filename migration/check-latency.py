#!/usr/bin/env python3
"""
check-latency.py — measure network latency from THIS host to each dependency
of a Freshket service, so a baseline can be captured before a cloud migration
and compared against the new environment afterwards.

It reads a tab-separated manifest (endpoints.tsv) listing every dependency
(host:port) per service, then measures, per endpoint:
  - DNS resolution time
  - TCP connect time (the handshake RTT — the metric that actually moves when
    you change cloud region/provider), sampled N times → min/avg/p95/max

Results print as a table and append to a timestamped CSV. Run it once in the
OLD environment (--label old) and once in the NEW (--label new), then diff:

    # baseline, from a pod/host in the current cloud
    ./check-latency.py --service oms-services-order --label old --out baseline.csv

    # after migration, from a pod/host in the new cloud
    ./check-latency.py --service oms-services-order --label new --out new.csv

    # compare
    ./check-latency.py --compare baseline.csv new.csv

Pure Python 3 standard library — no pip installs. Works on macOS and Linux.

IMPORTANT: run this FROM the environment the service runs in (e.g. `kubectl
exec` into the pod, or a host in the same VPC/region). Latency is relative to
where the script executes, not where you read the results.
"""

import argparse
import csv
import socket
import ssl
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

# Default ports per dependency kind, used when the manifest target omits one.
DEFAULT_PORTS = {
    "http-service": 443, "external-api": 443, "search": 443,
    "payment-gateway": 443, "mysql": 3306, "mssql": 1433,
    "mongo": 27017, "redis": 6379, "kafka": 9092,
}


def parse_target(target, kind):
    """Resolve a manifest target into (host, port). Accepts a URL, host:port,
    or bare host. Returns (None, None) for empty / placeholder targets."""
    target = (target or "").strip()
    if not target or target.startswith("<") or target.upper() == "TODO":
        return None, None
    if "://" in target:
        u = urlparse(target)
        host = u.hostname
        port = u.port or (443 if u.scheme == "https" else 80)
        return host, port
    if target.count(":") == 1:
        host, _, port = target.partition(":")
        return host, int(port)
    return target, DEFAULT_PORTS.get(kind, 443)


def measure_dns(host):
    """Time a DNS resolution. Returns ms or None on failure."""
    try:
        t0 = time.perf_counter()
        socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
        return (time.perf_counter() - t0) * 1000.0
    except socket.gaierror:
        return None


def measure_tcp(host, port, samples, timeout):
    """Open and close a TCP connection `samples` times. Returns the list of
    successful connect times (ms). A TCP handshake is the cleanest proxy for
    network RTT and works for every dependency kind (DB, cache, broker, HTTP)."""
    times = []
    for _ in range(samples):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            t0 = time.perf_counter()
            s.connect((host, port))
            times.append((time.perf_counter() - t0) * 1000.0)
        except (socket.timeout, OSError):
            pass
        finally:
            s.close()
    return times


def measure_tls(host, port, timeout):
    """Optional: time a full TLS handshake for HTTPS endpoints (ms or None)."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        t0 = time.perf_counter()
        with socket.create_connection((host, port), timeout=timeout) as raw:
            with ctx.wrap_socket(raw, server_hostname=host):
                return (time.perf_counter() - t0) * 1000.0
    except (socket.timeout, OSError, ssl.SSLError):
        return None


def pct(values, p):
    if not values:
        return None
    s = sorted(values)
    k = max(0, min(len(s) - 1, int(round((p / 100.0) * (len(s) - 1)))))
    return s[k]


def load_manifest(path, service_filter):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if row.get("service", "").startswith("#"):
                continue
            if service_filter and row["service"] != service_filter:
                continue
            rows.append(row)
    return rows


def fmt(v):
    return f"{v:7.1f}" if isinstance(v, (int, float)) else f"{'--':>7}"


def run(args):
    rows = load_manifest(args.manifest, args.service)
    if not rows:
        print(f"No endpoints for service={args.service!r} in {args.manifest}", file=sys.stderr)
        return 1

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"\n  Latency probe · label={args.label} · {stamp} · {args.samples} samples · timeout {args.timeout}s")
    print(f"  manifest={args.manifest}  service={args.service or 'ALL'}\n")
    header = f"  {'SERVICE':<22} {'DEPENDENCY':<22} {'KIND':<14} {'HOST:PORT':<46} {'DNS':>7} {'TCPavg':>7} {'p95':>7} {'TLS':>7}  OK"
    print(header)
    print("  " + "-" * (len(header) - 2))

    out_rows = []
    for r in rows:
        host, port = parse_target(r.get("target", ""), r.get("kind", ""))
        name, kind, svc = r["dep_name"], r.get("kind", ""), r["service"]
        if not host:
            print(f"  {svc:<22} {name:<22} {kind:<14} {'<no target — fill in manifest>':<46} {'skip':>7}")
            continue
        dns = measure_dns(host)
        tcp = measure_tcp(host, port, args.samples, args.timeout)
        tls = measure_tls(host, port, args.timeout) if (args.tls and port == 443) else None
        ok = f"{len(tcp)}/{args.samples}"
        avg = sum(tcp) / len(tcp) if tcp else None
        hp = f"{host}:{port}"
        if len(hp) > 45:
            hp = hp[:42] + "..."
        print(f"  {svc:<22} {name:<22} {kind:<14} {hp:<46} {fmt(dns)} {fmt(avg)} {fmt(pct(tcp,95))} {fmt(tls)}  {ok}")
        out_rows.append({
            "timestamp": stamp, "label": args.label, "service": svc,
            "dep_name": name, "kind": kind, "host": host, "port": port,
            "dns_ms": round(dns, 2) if dns else "",
            "tcp_min_ms": round(min(tcp), 2) if tcp else "",
            "tcp_avg_ms": round(avg, 2) if avg else "",
            "tcp_p95_ms": round(pct(tcp, 95), 2) if tcp else "",
            "tcp_max_ms": round(max(tcp), 2) if tcp else "",
            "tls_ms": round(tls, 2) if tls else "",
            "ok": len(tcp), "samples": args.samples,
        })

    if args.out and out_rows:
        write_header = True
        try:
            with open(args.out, "r"):
                write_header = False
        except FileNotFoundError:
            pass
        with open(args.out, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
            if write_header:
                w.writeheader()
            w.writerows(out_rows)
        print(f"\n  → appended {len(out_rows)} rows to {args.out}")
    print()
    return 0


def compare(baseline_path, current_path):
    def index(path):
        idx = {}
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                idx[(row["service"], row["dep_name"])] = row
        return idx

    base, cur = index(baseline_path), index(current_path)
    keys = sorted(set(base) | set(cur))
    print(f"\n  Compare  baseline={baseline_path}  current={current_path}")
    print(f"  (TCP avg ms; Δ>+5ms or >+25% flagged ⚠, big improvement ✓)\n")
    head = f"  {'SERVICE':<22} {'DEPENDENCY':<22} {'BASE':>9} {'CURRENT':>9} {'Δ ms':>9} {'Δ %':>8}"
    print(head)
    print("  " + "-" * (len(head) - 2))
    for k in keys:
        b, c = base.get(k), cur.get(k)
        bv = float(b["tcp_avg_ms"]) if b and b.get("tcp_avg_ms") else None
        cv = float(c["tcp_avg_ms"]) if c and c.get("tcp_avg_ms") else None
        flag = ""
        if bv is not None and cv is not None:
            d = cv - bv
            pctd = (d / bv * 100.0) if bv else 0.0
            if d > 5 or pctd > 25:
                flag = " ⚠"
            elif d < -5 or pctd < -25:
                flag = " ✓"
            dstr, pstr = f"{d:+.1f}", f"{pctd:+.0f}%"
        else:
            dstr = pstr = "n/a"
        print(f"  {k[0]:<22} {k[1]:<22} {fmt(bv).strip():>9} {fmt(cv).strip():>9} {dstr:>9} {pstr:>8}{flag}")
    print()
    return 0


def main():
    p = argparse.ArgumentParser(description="Measure dependency latency for a Freshket service (pre/post cloud migration).")
    p.add_argument("--manifest", default="endpoints.tsv", help="TSV manifest of dependencies (default: endpoints.tsv)")
    p.add_argument("--service", help="filter to one service (e.g. oms-services-order); default: all")
    p.add_argument("--samples", type=int, default=10, help="TCP connect samples per endpoint (default 10)")
    p.add_argument("--timeout", type=float, default=3.0, help="per-connection timeout seconds (default 3)")
    p.add_argument("--label", default="run", help="label stored in CSV (e.g. old / new / aws-sit)")
    p.add_argument("--out", help="append results to this CSV file")
    p.add_argument("--tls", action="store_true", help="also time TLS handshake for :443 endpoints")
    p.add_argument("--compare", nargs=2, metavar=("BASELINE", "CURRENT"), help="diff two result CSVs and exit")
    args = p.parse_args()
    if args.compare:
        return compare(*args.compare)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Proxy Tester & IP Info Scanner
------------------------------
Tests proxies for:
  1. HTTP/HTTPS response latency (ms)
  2. Download speed (Mbps & KB/s)
  3. Comprehensive IP information (geolocation, ISP, ASN, timezone, anonymity level)

Usage:
  python3 proxy_tester.py [proxy_url_1] [proxy_url_2] ...
  python3 proxy_tester.py --file proxies.txt
  python3 proxy_tester.py --fetch-free --count 5
  python3 proxy_tester.py  (runs default test list including user proxy)
"""

import sys
import time
import json
import socket
import argparse
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# IP-API comprehensive fields parameter
IP_API_FIELDS = 66846719
# Speed test URL (500 KB chunk from Cloudflare speed test)
SPEEDTEST_URL = "https://speed.cloudflare.com/__down?bytes=500000"
SPEEDTEST_BYTES = 500000
FALLBACK_SPEEDTEST_URL = "http://httpbin.org/bytes/200000"
FALLBACK_SPEEDTEST_BYTES = 200000

DEFAULT_PROXIES = [
    "http://103.74.144.5:83",        # User-provided proxy (New Delhi, India - Airmax Internet)
    "http://135.87.39.23:80",        # Reference working proxy (Finland - Nokia Solutions)
    "http://185.161.251.195:3128",   # Reference working proxy (Germany - Global Connectivity)
    "http://2.59.43.253:22222",      # Reference working proxy (Russia - JSC TIMEWEB)
]


def parse_proxy(proxy_str: str) -> dict:
    """Parse a proxy string into its components."""
    proxy_str = proxy_str.strip()
    if not proxy_str.startswith(("http://", "https://", "socks4://", "socks5://")):
        proxy_str = "http://" + proxy_str

    parsed = urllib.parse.urlsplit(proxy_str)
    scheme = parsed.scheme.lower()
    host = parsed.hostname or ""
    port = parsed.port or (1080 if "socks" in scheme else 80)
    user = parsed.username
    password = parsed.password

    return {
        "raw": proxy_str,
        "scheme": scheme,
        "host": host,
        "port": port,
        "user": user,
        "password": password,
    }


def fetch_direct_ip_info(ip: str) -> dict:
    """Fetch direct IP information for an IP address without using a proxy."""
    try:
        url = f"http://ip-api.com/json/{ip}?fields={IP_API_FIELDS}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "success":
                return data
    except Exception as e:
        pass
    return {}


def test_download_speed(proxies_dict: dict) -> dict:
    """Test download speed through the given proxy dict."""
    try:
        t0 = time.time()
        res = requests.get(SPEEDTEST_URL, proxies=proxies_dict, timeout=10)
        duration = time.time() - t0
        if res.status_code == 200:
            size_bytes = len(res.content)
            speed_mbps = (size_bytes * 8) / (duration * 1000000)
            speed_kbs = size_bytes / (duration * 1024)
            return {
                "success": True,
                "bytes_downloaded": size_bytes,
                "duration_seconds": round(duration, 3),
                "speed_mbps": round(speed_mbps, 2),
                "speed_kbs": round(speed_kbs, 2),
                "test_url": SPEEDTEST_URL,
            }
    except Exception:
        # Try fallback url
        try:
            t0 = time.time()
            res = requests.get(FALLBACK_SPEEDTEST_URL, proxies=proxies_dict, timeout=8)
            duration = time.time() - t0
            if res.status_code == 200:
                size_bytes = len(res.content)
                speed_mbps = (size_bytes * 8) / (duration * 1000000)
                speed_kbs = size_bytes / (duration * 1024)
                return {
                    "success": True,
                    "bytes_downloaded": size_bytes,
                    "duration_seconds": round(duration, 3),
                    "speed_mbps": round(speed_mbps, 2),
                    "speed_kbs": round(speed_kbs, 2),
                    "test_url": FALLBACK_SPEEDTEST_URL,
                }
        except Exception:
            pass

    return {
        "success": False,
        "bytes_downloaded": 0,
        "duration_seconds": 0.0,
        "speed_mbps": 0.0,
        "speed_kbs": 0.0,
        "test_url": None,
    }


def determine_anonymity_level(my_ip: str, proxy_ip_info: dict, is_proxy_online: bool) -> str:
    """Determine proxy anonymity level."""
    if not is_proxy_online:
        return "Offline / Direct Info"

    seen_ip = proxy_ip_info.get("query", "")
    if seen_ip == my_ip:
        return "Transparent (Real IP Exposed)"
    elif proxy_ip_info.get("proxy", False):
        return "Anonymous (Known Proxy IP)"
    else:
        return "Elite (High Anonymity / No Proxy Flags)"


def test_proxy(proxy_str: str, my_ip: str = "") -> dict:
    """Comprehensive test for a single proxy."""
    parsed = parse_proxy(proxy_str)
    proxy_url = parsed["raw"]
    host = parsed["host"]

    proxies_dict = {
        "http": proxy_url,
        "https": proxy_url,
    }

    result = {
        "proxy": proxy_url,
        "scheme": parsed["scheme"],
        "host": host,
        "port": parsed["port"],
        "status": "offline",
        "error": None,
        "latency_ms": None,
        "download_speed": {
            "speed_mbps": 0.0,
            "speed_kbs": 0.0,
            "bytes_downloaded": 0,
            "duration_seconds": 0.0,
            "success": False,
        },
        "anonymity_level": "Offline / Direct Info",
        "ip_info": {},
        "ip_info_source": "none",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime()),
    }

    # First attempt: test via proxy
    try:
        t0 = time.time()
        res = requests.get(
            f"http://ip-api.com/json/?fields={IP_API_FIELDS}",
            proxies=proxies_dict,
            timeout=8,
        )
        latency_ms = (time.time() - t0) * 1000

        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "success":
                result["status"] = "online"
                result["latency_ms"] = round(latency_ms, 2)
                result["ip_info"] = data
                result["ip_info_source"] = "via_proxy"
                result["anonymity_level"] = determine_anonymity_level(my_ip, data, True)

                # Measure download speed only if online
                dl_result = test_download_speed(proxies_dict)
                result["download_speed"] = dl_result
                return result
    except Exception as e:
        result["error"] = str(e).split("(")[0].strip()

    # If proxy is offline or failed, fetch direct IP info of the proxy host
    if host:
        direct_info = fetch_direct_ip_info(host)
        if direct_info:
            result["ip_info"] = direct_info
            result["ip_info_source"] = "direct_lookup"
            result["anonymity_level"] = "Offline (Direct Host IP Info)"

    return result


def fetch_free_proxies(count: int = 5) -> list:
    """Scrape working public HTTP proxies."""
    print("Fetching free public proxy list...")
    url = "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"
    try:
        res = requests.get(url, timeout=10)
        lines = [line.strip() for line in res.text.splitlines() if line.strip()]
        return ["http://" + line for line in lines[:count]]
    except Exception as e:
        print(f"Failed to fetch public proxies: {e}")
        return []


def print_summary_table(results: list):
    """Print an ASCII summary table of test results."""
    headers = [
        "Proxy",
        "Status",
        "Latency",
        "DL Speed",
        "Country",
        "City",
        "ISP / AS",
        "Anonymity",
    ]
    rows = []

    for r in results:
        proxy_name = r["proxy"]
        status = r["status"].upper()
        lat = f"{r['latency_ms']} ms" if r["latency_ms"] is not None else "N/A"
        dl = f"{r['download_speed']['speed_mbps']} Mbps" if r["status"] == "online" else "N/A"

        info = r["ip_info"]
        country = info.get("countryCode") or info.get("country", "Unknown")
        city = info.get("city", "Unknown")
        isp = info.get("isp", info.get("org", "Unknown"))
        if len(isp) > 25:
            isp = isp[:22] + "..."
        anon = r["anonymity_level"]

        rows.append([proxy_name, status, lat, dl, country, city, isp, anon])

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(str(val)))

    # Formatting helper
    def fmt_row(row_items):
        return " | ".join(f"{str(item):<{col_widths[idx]}}" for idx, item in enumerate(row_items))

    separator = "-+-".join("-" * w for w in col_widths)

    print("\n" + "=" * 100)
    print("PROXY PERFORMANCE & IP INFORMATION REPORT")
    print("=" * 100)
    print(fmt_row(headers))
    print(separator)
    for row in rows:
        print(fmt_row(row))
    print("=" * 100 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Test proxies latency, DL speed, and all IP info.")
    parser.add_argument("proxies", nargs="*", help="Proxy URLs to test (e.g. http://ip:port)")
    parser.add_argument("-f", "--file", help="File containing list of proxies (one per line)")
    parser.add_argument("--fetch-free", action="store_true", help="Fetch and test free public proxies")
    parser.add_argument("--count", type=int, default=5, help="Number of free proxies to fetch")
    parser.add_argument("-o", "--output", default="proxy_test_results.json", help="Output JSON filename")
    parser.add_argument("-w", "--workers", type=int, default=10, help="Max concurrent test threads")

    args = parser.parse_args()

    proxy_list = []
    if args.file:
        try:
            with open(args.file, "r") as f:
                proxy_list = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        except Exception as e:
            print(f"Error reading file {args.file}: {e}")
            sys.exit(1)
    elif args.fetch_free:
        proxy_list = fetch_free_proxies(args.count)
    elif args.proxies:
        proxy_list = args.proxies
    else:
        proxy_list = DEFAULT_PROXIES

    print(f"Starting tests for {len(proxy_list)} proxies (using {args.workers} threads)...")

    # Determine our own external IP for anonymity comparison
    my_ip = ""
    try:
        my_ip_info = requests.get("http://ip-api.com/json/?fields=query", timeout=3).json()
        my_ip = my_ip_info.get("query", "")
    except Exception:
        pass

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_proxy = {executor.submit(test_proxy, p, my_ip): p for p in proxy_list}
        for future in as_completed(future_to_proxy):
            p = future_to_proxy[future]
            try:
                res = future.result()
                results.append(res)
                status_symbol = "✓ ONLINE " if res["status"] == "online" else "✗ OFFLINE"
                lat_str = f"({res['latency_ms']}ms)" if res["latency_ms"] else ""
                print(f"  [{status_symbol}] {p} {lat_str}")
            except Exception as e:
                print(f"  [✗ ERROR] {p}: {e}")

    # Sort results: online proxies first (sorted by latency), then offline proxies
    results.sort(
        key=lambda x: (
            0 if x["status"] == "online" else 1,
            x["latency_ms"] if x["latency_ms"] is not None else float("inf"),
        )
    )

    # Output to JSON
    report_data = {
        "metadata": {
            "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime()),
            "total_tested": len(results),
            "online_count": sum(1 for r in results if r["status"] == "online"),
            "offline_count": sum(1 for r in results if r["status"] == "offline"),
            "tester_version": "1.0.0",
        },
        "results": results,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print_summary_table(results)
    print(f"Complete JSON report saved to: {args.output}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
#1 Enterprise Bug Bounty Recon & Vulnerability Scanner Tool
-----------------------------------------------------------
Performs deep automated security auditing, vulnerability probing, and exploit verification:
  1. HTTP Security Headers Audit (CWE-693 / CWE-16)
  2. CORS Permissive Policy Analysis (CWE-942 / CWE-352)
  3. Unauthenticated Admin & API Write Access Probing (CWE-306 / CWE-862)
  4. Server-Side Request Forgery (SSRF) Vector Probing (CWE-918)
  5. Cross-Site Scripting (XSS) Reflection Probing (CWE-79)
  6. SQL / NoSQL Injection Vector Testing (CWE-89 / CWE-943)
  7. Rate Limiting & DoS Resource Exhaustion Check (CWE-400)
  8. Path Traversal & Information Disclosure Probing (CWE-22 / CWE-200)
  9. HTTP Verb / Method Tampering (CWE-650)
 10. Malformed JSON / Mass Assignment Probing (CWE-915)

Usage:
  python3 bug_bounty_scanner.py --target http://localhost:8000
  python3 bug_bounty_scanner.py --target http://localhost:8000 --proxy http://localhost:8888
"""

import sys
import time
import json
import argparse
import requests
from urllib.parse import urljoin, urlparse

# ANSI colors for terminal display
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

class BugBountyScanner:
    def __init__(self, base_url, proxy_url=None):
        self.base_url = base_url.rstrip("/")
        self.proxy_url = proxy_url
        self.proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
        self.findings = []
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "BugBountyScanner-Pro/1.0 (Security Audit Tool; +https://arena.ai/agent)"
        })

    def log_finding(self, title, severity, cwe, endpoint, description, evidence, remediation):
        finding = {
            "title": title,
            "severity": severity.upper(),
            "cwe": cwe,
            "endpoint": endpoint,
            "description": description,
            "evidence": evidence,
            "remediation": remediation,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.findings.append(finding)
        color = RED if severity.upper() == "CRITICAL" else (YELLOW if severity.upper() in ["HIGH", "MEDIUM"] else CYAN)
        print(f"  [{color}{BOLD}{severity.upper()}{RESET}] {title} ({cwe}) -> {endpoint}")

    def test_security_headers(self):
        print(f"\n{BOLD}[1/10] Auditing HTTP Security Headers...{RESET}")
        try:
            r = self.session.get(f"{self.base_url}/", proxies=self.proxies, timeout=5)
            headers = r.headers

            missing_headers = []
            if "Content-Security-Policy" not in headers:
                missing_headers.append("Content-Security-Policy")
            if "X-Content-Type-Options" not in headers:
                missing_headers.append("X-Content-Type-Options")
            if "X-Frame-Options" not in headers:
                missing_headers.append("X-Frame-Options")
            if "Strict-Transport-Security" not in headers:
                missing_headers.append("Strict-Transport-Security")

            if missing_headers:
                self.log_finding(
                    title="Missing HTTP Security Defense-in-Depth Headers",
                    severity="Low",
                    cwe="CWE-693",
                    endpoint=f"{self.base_url}/",
                    description=f"The application fails to set important HTTP security headers: {', '.join(missing_headers)}.",
                    evidence=f"HTTP response headers received: {dict(headers)}",
                    remediation="Configure helmet.js or Express middleware to enforce Content-Security-Policy, HSTS, X-Frame-Options, and X-Content-Type-Options."
                )
            else:
                print(f"  [{GREEN}PASS{RESET}] All major security headers present.")
        except Exception as e:
            print(f"  [ERROR] Security header check failed: {e}")

    def test_cors_policy(self):
        print(f"\n{BOLD}[2/10] Probing Cross-Origin Resource Sharing (CORS) Configuration...{RESET}")
        try:
            headers = {"Origin": "https://evil-attacker.com"}
            r = self.session.get(f"{self.base_url}/api/v1/proxies", headers=headers, proxies=self.proxies, timeout=5)
            acao = r.headers.get("Access-Control-Allow-Origin")
            acac = r.headers.get("Access-Control-Allow-Credentials")

            if acao == "*" or acao == "https://evil-attacker.com":
                self.log_finding(
                    title="Permissive Cross-Origin Resource Sharing (CORS) Policy",
                    severity="Medium",
                    cwe="CWE-942",
                    endpoint="/api/v1/proxies",
                    description="The API allows requests from arbitrary origins ('*'), exposing sensitive data to cross-origin reads if cookies/tokens are added.",
                    evidence=f"Sent Origin: https://evil-attacker.com | Received Access-Control-Allow-Origin: {acao}",
                    remediation="Restrict CORS to trusted admin domain origins instead of wildcard '*'."
                )
            else:
                print(f"  [{GREEN}PASS{RESET}] CORS policy is properly restricted.")
        except Exception as e:
            print(f"  [ERROR] CORS check failed: {e}")

    def test_unauthenticated_admin_write(self):
        print(f"\n{BOLD}[3/10] Probing Unauthenticated Admin & API Write Access...{RESET}")
        try:
            # Test POST /api/v1/proxies/add without API key or Auth header
            payload = {"proxies": ["http://192.0.2.1:8080"]}
            r = self.session.post(
                f"{self.base_url}/api/v1/proxies/add",
                json=payload,
                proxies=self.proxies,
                timeout=5
            )
            if r.status_code == 200 and r.json().get("success"):
                self.log_finding(
                    title="Unauthenticated Admin Write Access on Sensitive Endpoint",
                    severity="Critical",
                    cwe="CWE-306",
                    endpoint="/api/v1/proxies/add",
                    description="Any unauthenticated attacker can submit POST requests to /api/v1/proxies/add and inject arbitrary proxy nodes into the active database without authorization.",
                    evidence=f"POST /api/v1/proxies/add returned HTTP 200: {r.text[:150]}",
                    remediation="Enforce mandatory API Key authentication (e.g. Authorization: Bearer <API_KEY>) on all administrative POST/DELETE endpoints."
                )
            else:
                print(f"  [{GREEN}PASS{RESET}] Admin write endpoint rejected unauthorized payload.")
        except Exception as e:
            print(f"  [ERROR] Unauthenticated write check failed: {e}")

    def test_ssrf_vulnerability(self):
        print(f"\n{BOLD}[4/10] Testing Server-Side Request Forgery (SSRF) Vectors...{RESET}")
        try:
            # Try injecting AWS metadata or internal localhost URLs via proxy add
            ssrf_urls = [
                "http://169.254.169.254/latest/meta-data/",
                "http://127.0.0.1:22/",
                "file:///etc/passwd"
            ]
            r = self.session.post(
                f"{self.base_url}/api/v1/proxies/add",
                json={"proxies": ssrf_urls},
                proxies=self.proxies,
                timeout=5
            )
            if r.status_code == 200 and r.json().get("success"):
                self.log_finding(
                    title="Server-Side Request Forgery (SSRF) via Unvalidated URL Input",
                    severity="High",
                    cwe="CWE-918",
                    endpoint="/api/v1/proxies/add",
                    description="The proxy registration endpoint accepts internal IP addresses (e.g., 169.254.169.254, 127.0.0.1) and non-HTTP protocols without strict URL validation.",
                    evidence=f"Submitted SSRF payloads {ssrf_urls} -> Server responded with success: {r.text[:120]}",
                    remediation="Validate URL hostname against RFC 1918 private address ranges and enforce only public 'http://', 'https://', 'socks4://', and 'socks5://' schemes."
                )
            else:
                print(f"  [{GREEN}PASS{RESET}] SSRF payloads were rejected by server.")
        except Exception as e:
            print(f"  [ERROR] SSRF check failed: {e}")

    def test_xss_reflection(self):
        print(f"\n{BOLD}[5/10] Probing Cross-Site Scripting (XSS) in Query Parameters...{RESET}")
        try:
            payload = "<script>alert('XSS-Bug-Bounty-Test')</script>"
            r = self.session.get(
                f"{self.base_url}/api/v1/proxies?city={payload}",
                proxies=self.proxies,
                timeout=5
            )
            if payload in r.text and "application/json" not in r.headers.get("Content-Type", ""):
                self.log_finding(
                    title="Reflected Cross-Site Scripting (XSS)",
                    severity="High",
                    cwe="CWE-79",
                    endpoint="/api/v1/proxies",
                    description="Unsanitized query parameter is reflected back in HTTP response without HTML encoding.",
                    evidence=f"Payload reflected verbatim in HTTP response body.",
                    remediation="Ensure JSON endpoints enforce 'Content-Type: application/json' and sanitize HTML characters."
                )
            else:
                print(f"  [{GREEN}PASS{RESET}] No XSS reflection detected in query parameters.")
        except Exception as e:
            print(f"  [ERROR] XSS check failed: {e}")

    def test_sql_nosql_injection(self):
        print(f"\n{BOLD}[6/10] Testing SQL / NoSQL Injection Vectors...{RESET}")
        try:
            payloads = ["' OR 1=1 --", '{"$ne": null}', "' OR 'a'='a"]
            for p in payloads:
                r = self.session.get(
                    f"{self.base_url}/api/v1/proxies?city={p}&minScore=0",
                    proxies=self.proxies,
                    timeout=5
                )
                if r.status_code == 500 or "syntax error" in r.text.lower() or "sql" in r.text.lower():
                    self.log_finding(
                        title="Potential Database Query Injection",
                        severity="High",
                        cwe="CWE-89",
                        endpoint="/api/v1/proxies",
                        description="Database query threw an unhandled syntax exception when encountering SQL/NoSQL metacharacters.",
                        evidence=f"Payload {p} triggered response: {r.text[:100]}",
                        remediation="Use parameterized queries or strictly validate input strings against allowed character sets."
                    )
                    break
            else:
                print(f"  [{GREEN}PASS{RESET}] API handled injection symbols safely without database errors.")
        except Exception as e:
            print(f"  [ERROR] Injection check failed: {e}")

    def test_rate_limiting_dos(self):
        print(f"\n{BOLD}[7/10] Testing Rate Limiting & Denial of Service (DoS) Resilience...{RESET}")
        try:
            success_count = 0
            t0 = time.time()
            for _ in range(8):
                r = self.session.post(f"{self.base_url}/api/v1/proxies/check", proxies=self.proxies, timeout=3)
                if r.status_code == 200:
                    success_count += 1
            dt = time.time() - t0

            if success_count >= 8:
                self.log_finding(
                    title="Missing Rate Limiting on Resource-Intensive Pool Check Endpoint",
                    severity="Medium",
                    cwe="CWE-400",
                    endpoint="/api/v1/proxies/check",
                    description="The application allows rapid unthrottled invocations of the background sweep endpoint, which could exhaust server network sockets and CPU under flood attacks.",
                    evidence=f"Successfully sent 8 unthrottled POST requests in {dt:.2f} seconds without HTTP 429 Too Many Requests.",
                    remediation="Implement express-rate-limit to restrict POST /api/v1/proxies/check to 1 request per 60 seconds per IP address."
                )
            else:
                print(f"  [{GREEN}PASS{RESET}] Server rate-limited or throttled rapid requests.")
        except requests.exceptions.Timeout:
            self.log_finding(
                title="Unthrottled Resource-Intensive Sweep Causes Server Timeout (DoS Risk)",
                severity="Medium",
                cwe="CWE-400",
                endpoint="/api/v1/proxies/check",
                description="Sending concurrent POST requests to /api/v1/proxies/check caused the Node.js server event loop to stall and time out, confirming susceptibility to Denial of Service (DoS).",
                evidence="HTTPConnectionPool read timeout after rapid concurrent sweep trigger requests.",
                remediation="Add express-rate-limit and debouncing logic so runPoolSweep() cannot be executed concurrently."
            )
        except Exception as e:
            print(f"  [ERROR] Rate limit check failed: {e}")

    def test_path_traversal(self):
        print(f"\n{BOLD}[8/10] Probing Directory Traversal & Sensitive File Exposure...{RESET}")
        try:
            paths = ["/../../../../etc/passwd", "/.%2e/.%2e/.%2e/etc/passwd", "/package.json"]
            for p in paths:
                r = self.session.get(f"{self.base_url}{p}", proxies=self.proxies, timeout=5)
                if "root:x:0:0" in r.text or "dependencies" in r.text:
                    self.log_finding(
                        title="Sensitive System/Configuration File Disclosure",
                        severity="High",
                        cwe="CWE-200",
                        endpoint=p,
                        description="Static file handler allows reading internal configuration files (package.json) or traversing to OS files.",
                        evidence=f"Request to {p} returned HTTP {r.status_code} with snippet: {r.text[:100]}...",
                        remediation="Ensure static middleware root is strictly scoped to /public and block requests containing traversal sequences or dot-files."
                    )
                    break
            else:
                print(f"  [{GREEN}PASS{RESET}] Directory traversal and system files are protected.")
        except Exception as e:
            print(f"  [ERROR] Path traversal check failed: {e}")

    def test_http_method_tampering(self):
        print(f"\n{BOLD}[9/10] Testing HTTP Verb & Method Tampering...{RESET}")
        try:
            # Check if TRACE or DELETE works on read-only endpoints
            r = self.session.request("TRACE", f"{self.base_url}/api/v1/proxies", proxies=self.proxies, timeout=5)
            if r.status_code == 200 and "TRACE /api/v1/proxies" in r.text:
                self.log_finding(
                    title="HTTP TRACE Method Enabled (Cross-Site Tracing Risk)",
                    severity="Medium",
                    cwe="CWE-650",
                    endpoint="/api/v1/proxies",
                    description="The server supports the HTTP TRACE method, which can be leveraged in Cross-Site Tracing (XST) attacks to steal sensitive Authorization headers.",
                    evidence=f"TRACE request returned HTTP 200 with request body echo.",
                    remediation="Disable TRACE and TRACK HTTP methods in the web server configuration."
                )
            else:
                print(f"  [{GREEN}PASS{RESET}] Unintended HTTP methods are correctly rejected.")
        except Exception as e:
            print(f"  [ERROR] Method tampering check failed: {e}")

    def test_malformed_json_handling(self):
        print(f"\n{BOLD}[10/10] Probing Malformed JSON & Unhandled Exception Handling...{RESET}")
        try:
            r = self.session.post(
                f"{self.base_url}/api/v1/proxies/add",
                data="{'malformed': json, -without-quotes}",
                headers={"Content-Type": "application/json"},
                proxies=self.proxies,
                timeout=5
            )
            if r.status_code == 500 and ("stack" in r.text.lower() or "syntaxerror" in r.text.lower()):
                self.log_finding(
                    title="Unhandled Exception & Stack Trace Disclosure on Malformed Input",
                    severity="Medium",
                    cwe="CWE-209",
                    endpoint="/api/v1/proxies/add",
                    description="When receiving malformed JSON payloads, the server exposes internal stack traces or Node.js runtime details in the HTTP response.",
                    evidence=f"HTTP 500 response contained: {r.text[:120]}...",
                    remediation="Implement a global Express error handler that logs stack traces internally and returns clean JSON error messages to clients."
                )
            else:
                print(f"  [{GREEN}PASS{RESET}] Server handled malformed JSON cleanly without leaking stack traces.")
        except Exception as e:
            print(f"  [ERROR] Malformed JSON check failed: {e}")

    def run_all_tests(self):
        print("=" * 80)
        print(f"{BOLD}#1 BUG BOUNTY AUTOMATED AUDIT & VULNERABILITY SCANNER{RESET}")
        print(f"Target Base URL : {self.base_url}")
        print(f"Routing Proxy   : {self.proxy_url or 'Direct Connection'}")
        print("=" * 80)

        t0 = time.time()
        self.test_security_headers()
        self.test_cors_policy()
        self.test_unauthenticated_admin_write()
        self.test_ssrf_vulnerability()
        self.test_xss_reflection()
        self.test_sql_nosql_injection()
        self.test_rate_limiting_dos()
        self.test_path_traversal()
        self.test_http_method_tampering()
        self.test_malformed_json_handling()
        duration = time.time() - t0

        print("\n" + "=" * 80)
        print(f"{BOLD}SCAN COMPLETE IN {duration:.2f} SECONDS — TOTAL FINDINGS: {len(self.findings)}{RESET}")
        print("=" * 80)

        # Summary count by severity
        sev_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for f in self.findings:
            sev_counts[f["severity"]] = sev_counts.get(f["severity"], 0) + 1

        for sev, count in sev_counts.items():
            color = RED if sev == "CRITICAL" else (YELLOW if sev in ["HIGH", "MEDIUM"] else CYAN)
            print(f"  {color}{BOLD}{sev:<8}{RESET} : {count} finding(s)")
        print("=" * 80 + "\n")

        return self.findings

def main():
    parser = argparse.ArgumentParser(description="#1 Enterprise Bug Bounty & Security Scanning Tool")
    parser.add_argument("--target", default="http://localhost:8000", help="Target URL to audit")
    parser.add_argument("--proxy", help="Optional proxy URL (e.g. http://localhost:8888)")
    parser.add_argument("-o", "--output", default="BUG_BOUNTY_AUDIT_REPORT.json", help="Output JSON filename")
    args = parser.parse_args()

    scanner = BugBountyScanner(args.target, args.proxy)
    findings = scanner.run_all_tests()

    report_data = {
        "metadata": {
            "target_url": args.target,
            "scan_timestamp": time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime()),
            "total_findings": len(findings),
            "scanner_version": "1.0.0-PRO"
        },
        "findings": findings
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"JSON vulnerability report saved to: {args.output}")

if __name__ == "__main__":
    main()

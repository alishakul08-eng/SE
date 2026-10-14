# Issues found in `ecommerce_cart_system.py`

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| `eval()` on caller-supplied string | Security (Bandit B307, Pylint W0123) | 43-44 | `calculateDiscountedTotal` runs `eval(discount_expr)`, so any string passed in executes arbitrary Python code. | Removed `eval`. The function now takes a numeric `discount_rate` and computes `price * (1 - rate)`, with a 0-1 range check. |
| MD5 hash | Security (Bandit B324, High) | 49 | `hashlib.md5` is a broken hash; flagged as weak for security use. | Switched to `hashlib.sha256`. |
| `os.system()` with string concatenation | Security (Bandit B605, High) | 60 | Builds a shell command from `filename`; a filename like `x; rm -rf ~` becomes command injection. | Removed the shell call and used `print()`. |
| Insecure random for a PIN | Security (Bandit B311) | 53 | `random.randint` is predictable and unsuitable for a checkout PIN. | Used `secrets.randbelow(9000) + 1000`. |
| Hardcoded live secret, then printed | Security (manual finding) | 72, 81 | `"STRIPE_SECRET_KEY_LIVE_2026"` is in source and printed to the console. Bandit did not flag it, because its hardcoded-secret check looks at variable names such as `password`/`secret`/`token`. | Read from env var `PAYMENT_GATEWAY_KEY`; stopped printing it (prints only whether it is configured). |
| Bare `except: pass` | Security/Quality (Bandit B110, Flake8 E722, Pylint W0702) | 26-29 | Swallows every error, including `KeyboardInterrupt`. | Replaced try/except with `cart_items.pop(item_id, None)`. |
| Mutable default argument | Bug (Pylint W0102) | 15 | `audit_log=[]` is created once and shared across all calls. | Default `None`, create a new list inside the function. |
| `%d` truncates price | Bug | 21 | `"%d" % 25.99` logs `25`, hiding the cents in the audit log. | Used an f-string with `{price:.2f}`. |
| `total_sales` global is wrong and unused | Bug / Design (Pylint W0603) | 12, 16, 20 | Starts at 0 although the cart already has items, is never reduced on removal, and is never read. | Removed the global entirely. |
| Unused import `math` | Style (Flake8 F401, Pylint W0611) | 4 | Imported but never used. | Deleted. |
| Unused variable `handling_fee` | Style (Flake8 F841, Pylint W0612) | 33 | Assigned, never used. | Deleted. |
| `== None` | Style (Flake8 E711, Pylint C0121) | 34 | Should use identity comparison. | `item is not None`. |
| Redundant if/else returning booleans | Quality (Pylint R1705) | 34-39 | Several lines for what is one boolean expression. | `return item is not None and item["qty"] > 0`. |
| Line too long | Style (Flake8 E501) | 76 | 86 chars, limit is 79. | Shortened as part of the `eval` fix. |
| File opened without `with` / no encoding | Quality (Pylint R1732, W1514) | 57-59 | File is not closed if `write` raises; encoding is platform-dependent. | `with open(..., encoding="utf-8")`, and `json.dump` for a proper receipt. |
| Parameter shadows global | Quality (Pylint W0621) | 63 | `getCartSummary(cart_items)` hides the module-level `cart_items`. | Renamed parameter to `cart`. |
| Unused loop variable `k`, poor name `x` | Quality (Pylint W0612, C0103) | 64-68 | `k` never used; `x` is meaningless. | Replaced with `sum(...)` generator. |
| camelCase function names, lowercase constant | Naming (Pylint C0103) | many | PEP 8 wants `snake_case` functions and `UPPER_CASE` module constants. | Renamed all functions; `cart_items` becomes `CART_ITEMS`. |
| Missing docstrings | Quality (Pylint C0114/C0116) | all | No module or function docstrings. | Added one-line docstrings. |
| `main()` runs on import | Design | 84 | Importing the module runs the whole demo. | Added `if __name__ == "__main__":`. |
| Unused variable `base_price` | Style (Flake8 F841) | 43 | Only used inside the `eval` string, so Flake8 sees it as unused. | Removed along with the `eval` call. |
| No newline at end of file | Style (Flake8 W292) | 84 | The file does not end with a newline. | Added a trailing newline. |

## Verification

| Tool | Before | After |
|------|--------|-------|
| Pylint score | 3.86 / 10 | 10.00 / 10 |
| Bandit issues | 5 | 0 |
| Flake8 issues | 7 | 0 |
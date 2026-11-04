# Pytest + Playwright demo (local and BrowserStack)

A small end-to-end test for https://bstackdemo.com written with **pytest** and **Playwright (Python)**.
It can run on your own machine or on **BrowserStack Automate** using the plain Playwright
integration (no BrowserStack SDK).

**What the test does** (`tests/test_add_to_cart.py`):
1. Adds the first two products to the cart and checks names, bag count and subtotal.
2. Increases the quantity of the first product and checks the subtotal.
3. Removes the second product and checks the cart and subtotal.
4. Clicks Checkout, signs in with the demo user, fills the shipping address.
5. Checks the order confirmation message, order number and total.

## Prerequisites
- Python 3.9 or newer
- Git
- (For BrowserStack runs) a BrowserStack account: username and access key from
  https://www.browserstack.com/accounts/settings

## 1. Get the code
```bash
git clone <REPOSITORY_URL>
cd <REPOSITORY_FOLDER>
```

## 2. Install dependencies
macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

Windows (PowerShell):
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

## 3. Run locally
Opens a visible Chromium window (`--headed --slowmo 800` are set in `pytest.ini`):
```bash
pytest
```

Run headless (no window):
```bash
pytest -o addopts="--browser chromium"
```

## 4. Run on BrowserStack
1. Copy the example env file and add **your own** credentials:
   ```bash
   cp .env.example .env          # Windows: copy .env.example .env
   ```
   Edit `.env`:
   ```
   BROWSERSTACK_USERNAME=<your username>
   BROWSERSTACK_ACCESS_KEY=<your access key>
   ```
   `.env` is git-ignored, so your credentials are never committed.

2. Run with `BROWSERSTACK=1`:

   macOS / Linux:
   ```bash
   BROWSERSTACK=1 pytest -o addopts="--browser chromium"
   ```
   Windows (PowerShell):
   ```powershell
   $env:BROWSERSTACK = "1"
   pytest -o addopts="--browser chromium"
   ```
   (`-o addopts=...` removes the local-only `--headed --slowmo` options.)

3. Open https://automate.browserstack.com to watch the session. Each run creates a new
   build named `pytest-playwright-<YYYY-MM-DD_HH-MM-SS>`; set `BROWSERSTACK_BUILD_NAME`
   in `.env` to use your own name.

## Changing the BrowserStack platform
The single platform is defined in `BSTACK_CAPS` in `conftest.py`
(currently macOS Sonoma / Chrome latest). Edit `browser`, `browser_version`, `os` and
`os_version` to run elsewhere. Valid combinations:
https://www.browserstack.com/docs/automate/playwright/browsers-and-os

## How the BrowserStack connection works
`conftest.py` overrides the `browser` fixture. When `BROWSERSTACK=1`, it connects to
`wss://cdp.browserstack.com/playwright` with the capabilities above; otherwise it launches
a local browser. After each test it reports pass/fail to the BrowserStack session.

## Project layout
```
conftest.py              # local vs BrowserStack browser fixture, session status
pytest.ini               # base URL and local run options
requirements.txt         # Python dependencies
.env.example             # template for BrowserStack credentials
tests/test_add_to_cart.py
```

## Troubleshooting
- `playwright: command not found`: activate the virtual environment (step 2).
- BrowserStack run fails to connect or shows an authorization error: check the username
  and access key in `.env`.
- No browser window opens locally: make sure you ran plain `pytest` (not with
  `-o addopts=...`).

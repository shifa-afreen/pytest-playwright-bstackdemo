import json
import os
import urllib.parse
from datetime import datetime

import pytest
from playwright.sync_api import Playwright

# >>> EDIT THESE TWO VALUES with your own BrowserStack credentials <<<
# (https://www.browserstack.com/accounts/settings)
# Do not commit your real access key to a shared or public repository.
BROWSERSTACK_USERNAME = "YOUR_BROWSERSTACK_USERNAME"
BROWSERSTACK_ACCESS_KEY = "YOUR_BROWSERSTACK_ACCESS_KEY"

# Dynamic build name: unique for every pytest run (all tests in one run share it).
BUILD_NAME = "pytest-playwright-" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Single BrowserStack platform (legacy: plain Playwright over CDP, no BrowserStack SDK)
BSTACK_CAPS = {
    "browser": "chrome",
    "browser_version": "latest",
    "os": "osx",
    "os_version": "Sonoma",
    "name": "bstackdemo cart and checkout",
    "build": BUILD_NAME,
    "project": "PytestPW-Legacy",
    "browserstack.username": BROWSERSTACK_USERNAME,
    "browserstack.accessKey": BROWSERSTACK_ACCESS_KEY,
}


def _use_browserstack() -> bool:
    return os.environ.get("BROWSERSTACK") == "1"


@pytest.fixture
def browser(playwright: Playwright, browser_type_launch_args):
    """Override pytest-playwright's browser: connect to BrowserStack when BROWSERSTACK=1."""
    if _use_browserstack():
        caps = json.dumps(BSTACK_CAPS)
        endpoint = "wss://cdp.browserstack.com/playwright?caps=" + urllib.parse.quote(caps)
        browser = playwright.chromium.connect(endpoint, timeout=120000)
    else:
        browser = playwright.chromium.launch(**browser_type_launch_args)
    yield browser
    browser.close()


@pytest.fixture(autouse=True)
def mark_browserstack_status(request, page):
    """Report pass/fail back to the BrowserStack session."""
    yield
    if not _use_browserstack():
        return
    failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False
    status = "failed" if failed else "passed"
    reason = "Test failed" if failed else "Test passed"
    command = "browserstack_executor: " + json.dumps(
        {"action": "setSessionStatus", "arguments": {"status": status, "reason": reason}}
    )
    page.evaluate("_ => {}", command)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    setattr(item, "rep_" + call.when, outcome.get_result())

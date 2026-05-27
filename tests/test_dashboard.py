"""Playwright tests for the Prismatic dashboard at http://localhost:3000."""

import re
import pytest
from playwright.sync_api import Page, expect

BASE = "http://localhost:3000"


def wait_for_data(page: Page, timeout: int = 15_000) -> None:
    """Block until at least one stat card moves away from its initial '-'."""
    expect(page.locator("#stat-files")).not_to_have_text("-", timeout=timeout)


# ── Initial load ──────────────────────────────────────────────────────────────

def test_page_title(page: Page) -> None:
    page.goto(BASE)
    expect(page).to_have_title("Prismatic - Intelligence Dashboard")


def test_stat_cards_populate(page: Page) -> None:
    page.goto(BASE)
    wait_for_data(page)

    for stat_id in [
        "stat-files", "stat-reviews", "stat-confidential",
        "stat-confidence", "stat-review", "stat-disputes",
    ]:
        text = page.locator(f"#{stat_id}").text_content()
        assert text not in ("-", "", None), f"#{stat_id} still shows placeholder: {text!r}"


def test_refresh_badge_shows_timestamp(page: Page) -> None:
    page.goto(BASE)
    wait_for_data(page)
    badge = page.locator("#last-refresh")
    expect(badge).not_to_have_text("Loading…", timeout=15_000)
    assert "Error:" not in (badge.text_content() or "")


def test_charts_render(page: Page) -> None:
    page.goto(BASE)
    wait_for_data(page)

    for canvas_id in ["chart-classification", "chart-sentiment"]:
        box = page.locator(f"#{canvas_id}").bounding_box()
        assert box is not None, f"#{canvas_id} not found"
        assert box["width"] > 0 and box["height"] > 0, f"#{canvas_id} has zero size"


def test_category_pills_render(page: Page) -> None:
    page.goto(BASE)
    pills = page.locator("#categories-list .category-pill")
    expect(pills.first).to_be_visible(timeout=10_000)
    assert pills.count() > 0


def test_health_badges_resolve(page: Page) -> None:
    page.goto(BASE)
    for badge_id in ["health-api", "health-n8n"]:
        expect(page.locator(f"#{badge_id}")).to_have_class(
            re.compile(r"up|down"), timeout=10_000
        )


def test_documents_table_has_rows(page: Page) -> None:
    page.goto(BASE)
    wait_for_data(page)
    rows = page.locator("#docs-tbody tr")
    expect(rows.first).to_be_visible(timeout=10_000)
    assert rows.count() > 0


# ── Hard-refresh resilience ───────────────────────────────────────────────────

def test_data_loads_after_hard_refresh(page: Page) -> None:
    # First load
    page.goto(BASE)
    wait_for_data(page)

    # Simulate hard refresh: clear cache and reload
    page.context.clear_cookies()
    page.reload(wait_until="domcontentloaded")

    wait_for_data(page)
    badge = page.locator("#last-refresh")
    expect(badge).not_to_have_text("Loading…", timeout=15_000)
    assert "Error:" not in (badge.text_content() or "")


# ── Chat (RAG) ────────────────────────────────────────────────────────────────

def test_chat_input_visible_and_enabled(page: Page) -> None:
    page.goto(BASE)
    inp = page.locator("#chat-input")
    expect(inp).to_be_visible()
    expect(inp).to_be_enabled()


def test_suggested_question_sends_message(page: Page) -> None:
    page.goto(BASE)
    hint = page.locator(".welcome-hint").first
    expect(hint).to_be_visible()
    hint.click()

    # User bubble should appear immediately
    expect(page.locator(".msg-bubble-user").first).to_be_visible(timeout=5_000)
    # Status should switch to sending
    expect(page.locator("#chat-status")).to_have_text("Thinking…", timeout=5_000)

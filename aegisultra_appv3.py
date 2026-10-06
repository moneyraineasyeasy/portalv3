from __future__ import annotations

import hashlib
import hmac
import html
import json
import math
import os
import re
import textwrap
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import parse_qs, quote, urlparse

import pandas as pd
import streamlit as st


# ============================================================
# AEGIS ULTRA V3 VIP MATCH CENTRE
# ============================================================

os.environ["ARROW_DEFAULT_MEMORY_POOL"] = "system"

APP_NAME = "雨姐 Aegis Ultra V3 VIP Match Centre"
APP_VERSION = "4.0.0"

DEFAULT_SHEET_ID = (
    "1RejS-0Iksz0OnFoR5Fcq1niOmJ9yjVqQj9OBHhuHalE"
)

VISIBLE_STATUSES = {
    "published",
    "ended",
}

TIER_ORDER = {
    "OFFICIAL": 0,
    "ALTERNATIVE": 1,
    "CORRECT_SCORE": 2,
}

RECOMMENDATION_DEFAULTS: Dict[str, Any] = {
    "rec_id": "",
    "match_id": "",
    "tier": "ALTERNATIVE",
    "rank": 999,
    "rec_title": "",
    "period": "FT",
    "market": "",
    "market_scope": "",
    "selection": "",
    "line": None,
    "odds": None,
    "conservative_hit": None,
    "median_hit": None,
    "nonloss_probability": None,
    "full_loss_probability": None,
    "fair_odds": None,
    "edge": None,
    "expected_value": None,
    "stars": 3,
    "price_status": "",
    "commentary": "",
    "is_heavy": False,
    "conflict_ids": "",
    "compatibility_group": "",
    "status": "",
    "result": "",
}

MATCH_DEFAULTS: Dict[str, Any] = {
    "match_id": "",
    "match_name": "",
    "home_team": "",
    "away_team": "",
    "competition": "",
    "kickoff": "",
    "status": "",
    "model_direction": "",
    "model_summary": "",
    "top_scores": "",
    "final_score": "",
}


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "About": (
            "Aegis Ultra V2 VIP Match Centre\n\n"
            "Private member portal."
        ),
    },
)


# ============================================================
# 1. HTML rendering
# ============================================================

def render_html(markup: str) -> None:
    st.html(textwrap.dedent(markup).strip())


# ============================================================
# 2. Premium visual system
# ============================================================

st.markdown(
    """
    <style>
    * {
        box-sizing: border-box;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    :root {
        --void: #04060c;
        --obsidian: #080b14;
        --panel: rgba(16, 22, 37, 0.78);
        --panel-soft: rgba(255, 255, 255, 0.042);
        --border: rgba(255, 255, 255, 0.085);
        --border-strong: rgba(255, 255, 255, 0.14);
        --gold: #f59e0b;
        --gold-light: #fde68a;
        --emerald: #10b981;
        --cyan: #38bdf8;
        --violet: #8b5cf6;
        --rose: #f43f5e;
        --orange: #f97316;
        --lime: #84cc16;
        --muted: #94a3b8;
    }

    html {
        scroll-behavior: smooth;
    }

    body {
        background: var(--void);
    }

    .stApp {
        color: #f8fafc;
        background:
            radial-gradient(
                circle at 7% 0%,
                rgba(37, 79, 205, 0.26),
                transparent 26%
            ),
            radial-gradient(
                circle at 96% 4%,
                rgba(130, 55, 208, 0.18),
                transparent 24%
            ),
            radial-gradient(
                circle at 52% 105%,
                rgba(16, 185, 129, 0.09),
                transparent 32%
            ),
            linear-gradient(
                180deg,
                #03050a 0%,
                #080c16 45%,
                #03050a 100%
            );
    }

    .block-container {
        max-width: 1480px;
        padding-top: 1.1rem;
        padding-bottom: 5rem;
    }

    [data-testid="stSidebar"] {
        background:
            radial-gradient(
                circle at 20% 0%,
                rgba(56, 88, 220, 0.13),
                transparent 30%
            ),
            linear-gradient(
                180deg,
                rgba(12, 16, 28, 0.995),
                rgba(4, 7, 13, 0.995)
            );
        border-right: 1px solid rgba(255, 255, 255, 0.075);
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.25rem;
    }

    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: transparent;
    }

    ::-webkit-scrollbar-thumb {
        background: #263249;
        border-radius: 999px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #3a4967;
    }

    /* Hero */

    .portal-hero {
        position: relative;
        overflow: hidden;
        padding: 2.35rem 2.5rem;
        margin-bottom: 1.4rem;
        border-radius: 30px;
        background:
            linear-gradient(
                125deg,
                rgba(24, 36, 78, 0.96),
                rgba(46, 28, 78, 0.89),
                rgba(8, 55, 62, 0.79)
            );
        border: 1px solid rgba(255, 255, 255, 0.14);
        box-shadow:
            0 34px 110px rgba(0, 0, 0, 0.46),
            inset 0 1px 0 rgba(255, 255, 255, 0.10);
        backdrop-filter: blur(22px);
        -webkit-backdrop-filter: blur(22px);
    }

    .portal-hero::before {
        content: "";
        position: absolute;
        width: 390px;
        height: 390px;
        top: -290px;
        right: -80px;
        border-radius: 50%;
        background: rgba(245, 158, 11, 0.34);
        filter: blur(30px);
    }

    .portal-hero::after {
        content: "";
        position: absolute;
        width: 270px;
        height: 270px;
        bottom: -210px;
        left: 34%;
        border-radius: 50%;
        background: rgba(56, 189, 248, 0.18);
        filter: blur(38px);
    }

    .portal-eyebrow {
        position: relative;
        z-index: 2;
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.42rem 0.85rem;
        margin-bottom: 0.95rem;
        border-radius: 999px;
        color: #fde68a;
        background: rgba(245, 158, 11, 0.13);
        border: 1px solid rgba(245, 158, 11, 0.34);
        font-size: 0.74rem;
        font-weight: 950;
        letter-spacing: 0.11em;
        text-transform: uppercase;
    }

    .portal-title {
        position: relative;
        z-index: 2;
        margin: 0;
        font-size: clamp(2.3rem, 6vw, 3.35rem);
        line-height: 1.02;
        font-weight: 950;
        letter-spacing: -0.06em;
        background:
            linear-gradient(
                135deg,
                #ffffff 15%,
                #fff7d6 48%,
                #fbbf24 100%
            );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .portal-trophy {
        background: none;
        color: initial;
        -webkit-text-fill-color: initial;
    }

    .portal-subtitle {
        position: relative;
        z-index: 2;
        max-width: 900px;
        margin: 0.95rem 0 0;
        color: rgba(255, 255, 255, 0.70);
        font-size: 1.04rem;
        line-height: 1.68;
    }

    .hero-feature-row {
        position: relative;
        z-index: 2;
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-top: 1.15rem;
    }

    .hero-feature {
        padding: 0.46rem 0.72rem;
        border-radius: 999px;
        color: #cbd5e1;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.09);
        font-size: 0.76rem;
        font-weight: 800;
    }

    .live-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #34d399;
        box-shadow: 0 0 14px #34d399;
        animation: livePulse 1.8s infinite;
    }

    @keyframes livePulse {
        0%, 100% {
            opacity: 1;
            transform: scale(1);
        }

        50% {
            opacity: 0.45;
            transform: scale(0.72);
        }
    }

    /* Login */

    .login-shell {
        max-width: 650px;
        margin: 2.1rem auto 1rem;
        padding: 2.25rem;
        border-radius: 28px;
        background:
            radial-gradient(
                circle at 50% 0%,
                rgba(245, 158, 11, 0.09),
                transparent 38%
            ),
            linear-gradient(
                145deg,
                rgba(17, 24, 39, 0.96),
                rgba(8, 12, 22, 0.91)
            );
        border: 1px solid rgba(255, 255, 255, 0.11);
        box-shadow:
            0 38px 115px rgba(0, 0, 0, 0.48),
            inset 0 1px 0 rgba(255, 255, 255, 0.07);
    }

    .login-icon {
        text-align: center;
        font-size: 3.6rem;
        filter: drop-shadow(0 0 24px rgba(245, 158, 11, 0.34));
    }

    .login-title {
        margin-top: 0.5rem;
        text-align: center;
        color: white;
        font-size: 1.85rem;
        font-weight: 950;
    }

    .login-copy {
        max-width: 460px;
        margin: 0.6rem auto 0;
        text-align: center;
        color: #8290a4;
        line-height: 1.6;
    }

    .login-security {
        margin-top: 1rem;
        padding: 0.72rem 0.9rem;
        text-align: center;
        border-radius: 12px;
        color: #a7f3d0;
        background: rgba(16, 185, 129, 0.075);
        border: 1px solid rgba(16, 185, 129, 0.17);
        font-size: 0.82rem;
    }

    /* Dashboard */

    .welcome-card {
        padding: 1.35rem 1.5rem;
        margin-bottom: 1.3rem;
        border-radius: 20px;
        background:
            linear-gradient(
                120deg,
                rgba(245, 158, 11, 0.115),
                rgba(255, 255, 255, 0.035)
            );
        border: 1px solid rgba(245, 158, 11, 0.22);
        border-left: 4px solid var(--gold);
        box-shadow: 0 15px 48px rgba(0, 0, 0, 0.24);
    }

    .welcome-name {
        color: white;
        font-size: 1.3rem;
        font-weight: 950;
    }

    .welcome-name span {
        color: #fbbf24;
    }

    .welcome-copy {
        margin-top: 0.45rem;
        color: #94a3b8;
        line-height: 1.55;
    }

    .section-kicker {
        margin-top: 1.2rem;
        margin-bottom: 0.7rem;
        color: rgba(255, 255, 255, 0.46);
        font-size: 0.72rem;
        font-weight: 950;
        letter-spacing: 0.15em;
        text-transform: uppercase;
    }

    .empty-state {
        padding: 2.3rem;
        text-align: center;
        border-radius: 22px;
        color: #94a3b8;
        background: rgba(255, 255, 255, 0.032);
        border: 1px dashed rgba(255, 255, 255, 0.14);
        line-height: 1.7;
    }

    /* Match header */

    .match-heading {
        padding: 1.2rem 1.3rem;
        margin-bottom: 0.85rem;
        border-radius: 19px;
        background:
            radial-gradient(
                circle at 100% 0%,
                rgba(56, 189, 248, 0.09),
                transparent 35%
            ),
            linear-gradient(
                120deg,
                rgba(28, 39, 61, 0.88),
                rgba(15, 23, 42, 0.64)
            );
        border: 1px solid rgba(255, 255, 255, 0.09);
        box-shadow: 0 13px 38px rgba(0, 0, 0, 0.21);
    }

    .match-heading-heavy {
        background:
            radial-gradient(
                circle at 100% 0%,
                rgba(245, 158, 11, 0.16),
                transparent 36%
            ),
            linear-gradient(
                120deg,
                rgba(67, 38, 12, 0.58),
                rgba(22, 29, 47, 0.82)
            );
        border-color: rgba(245, 158, 11, 0.28);
    }

    .match-heading-ended {
        opacity: 0.84;
        background: rgba(15, 23, 42, 0.52);
    }

    .match-name {
        color: white;
        font-size: 1.32rem;
        font-weight: 950;
        letter-spacing: -0.03em;
    }

    .match-meta {
        margin-top: 0.42rem;
        color: #8190a6;
        font-size: 0.88rem;
        line-height: 1.5;
    }

    .model-direction {
        margin-top: 0.82rem;
        padding: 0.75rem 0.9rem;
        border-radius: 12px;
        color: #bae6fd;
        background: rgba(56, 189, 248, 0.075);
        border: 1px solid rgba(56, 189, 248, 0.18);
        line-height: 1.52;
    }

    .model-summary {
        margin-top: 0.74rem;
        color: #9ba9bc;
        line-height: 1.6;
    }

    .score-summary {
        margin-top: 0.6rem;
        color: #c4b5fd;
        line-height: 1.52;
    }

    /* Recommendation cards */

    .recommendation-card {
        position: relative;
        overflow: hidden;
        padding: 1.2rem 1.28rem;
        margin: 0.8rem 0;
        border-radius: 20px;
        background:
            linear-gradient(
                145deg,
                rgba(16, 24, 41, 0.91),
                rgba(11, 17, 31, 0.70)
            );
        border: 1px solid rgba(255, 255, 255, 0.088);
        box-shadow: 0 15px 46px rgba(0, 0, 0, 0.27);
    }

    .recommendation-card::after {
        content: "";
        position: absolute;
        width: 130px;
        height: 130px;
        right: -88px;
        top: -88px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.048);
    }

    .recommendation-card-official {
        border-left: 4px solid var(--emerald);
    }

    .recommendation-card-alternative {
        border-left: 4px solid var(--cyan);
    }

    .recommendation-card-score {
        border-left: 4px solid var(--violet);
    }

    .recommendation-card-heavy {
        border: 1px solid rgba(245, 158, 11, 0.41);
        border-left: 4px solid var(--gold);
        background:
            radial-gradient(
                circle at 100% 0%,
                rgba(245, 158, 11, 0.14),
                transparent 35%
            ),
            linear-gradient(
                145deg,
                rgba(64, 37, 12, 0.53),
                rgba(15, 23, 42, 0.77)
            );
        box-shadow:
            0 0 40px rgba(245, 158, 11, 0.11),
            0 15px 46px rgba(0, 0, 0, 0.29);
    }

    .tier-pill,
    .period-pill,
    .heavy-pill {
        position: relative;
        z-index: 2;
        display: inline-block;
        padding: 0.31rem 0.64rem;
        border-radius: 999px;
        font-size: 0.67rem;
        font-weight: 950;
        letter-spacing: 0.065em;
        text-transform: uppercase;
    }

    .tier-official {
        color: #bbf7d0;
        background: rgba(16, 185, 129, 0.14);
        border: 1px solid rgba(16, 185, 129, 0.29);
    }

    .tier-alternative {
        color: #bae6fd;
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.24);
    }

    .tier-score {
        color: #ddd6fe;
        background: rgba(139, 92, 246, 0.14);
        border: 1px solid rgba(139, 92, 246, 0.28);
    }

    .period-pill {
        margin-left: 0.38rem;
        color: #cbd5e1;
        background: rgba(148, 163, 184, 0.11);
        border: 1px solid rgba(148, 163, 184, 0.20);
    }

    .period-ht {
        color: #f0abfc;
        background: rgba(217, 70, 239, 0.11);
        border-color: rgba(217, 70, 239, 0.23);
    }

    .period-2h {
        color: #fcd34d;
        background: rgba(245, 158, 11, 0.12);
        border-color: rgba(245, 158, 11, 0.26);
    }

    .tier-pill-score {
        color: #ddd6fe;
        background: rgba(139, 92, 246, 0.14);
        border: 1px solid rgba(139, 92, 246, 0.28);
    }

    .tier-pill-unknown {
        color: #cbd5e1;
        background: rgba(148, 163, 184, 0.11);
        border: 1px solid rgba(148, 163, 184, 0.20);
    }

    .heavy-pill {
        margin-left: 0.38rem;
        color: #fff7ed;
        background:
            linear-gradient(
                135deg,
                rgba(220, 38, 38, 0.84),
                rgba(245, 158, 11, 0.82)
            );
        box-shadow: 0 0 18px rgba(245, 158, 11, 0.16);
    }

    .rec-title {
        position: relative;
        z-index: 2;
        margin-top: 0.78rem;
        color: white;
        font-size: 1.3rem;
        font-weight: 950;
        letter-spacing: -0.03em;
    }

    .rec-odds {
        color: #fde68a;
        font-weight: 950;
    }

    .star-row {
        position: relative;
        z-index: 2;
        margin-top: 0.53rem;
        color: #fbbf24;
        letter-spacing: 0.09em;
        filter: drop-shadow(0 0 7px rgba(245, 158, 11, 0.17));
    }

    .rec-stats {
        position: relative;
        z-index: 2;
        display: flex;
        flex-wrap: wrap;
        gap: 0.56rem;
        margin-top: 0.8rem;
    }

    .stat-chip {
        padding: 0.5rem 0.72rem;
        border-radius: 10px;
        color: #cbd5e1;
        background: rgba(255, 255, 255, 0.047);
        border: 1px solid rgba(255, 255, 255, 0.075);
        font-size: 0.81rem;
    }

    .stat-chip strong {
        color: #f8fafc;
    }

    .commentary {
        position: relative;
        z-index: 2;
        margin-top: 0.94rem;
        padding: 0.9rem 1rem;
        border-radius: 12px;
        color: #cbd5e1;
        background: rgba(0, 0, 0, 0.25);
        border-left: 3px solid var(--cyan);
        line-height: 1.62;
    }

    .commentary-heavy {
        border-left-color: var(--gold);
    }

    /* Results */

    .result-badge {
        position: relative;
        z-index: 2;
        display: inline-block;
        margin-top: 0.78rem;
        padding: 0.44rem 0.72rem;
        border-radius: 10px;
        font-size: 0.81rem;
        font-weight: 900;
    }

    .result-hit {
        color: #bbf7d0;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.24);
    }

    .result-half-win {
        color: #d9f99d;
        background: rgba(132, 204, 22, 0.14);
        border: 1px solid rgba(132, 204, 22, 0.24);
    }

    .result-push {
        color: #bae6fd;
        background: rgba(56, 189, 248, 0.14);
        border: 1px solid rgba(56, 189, 248, 0.23);
    }

    .result-half-loss {
        color: #fed7aa;
        background: rgba(249, 115, 22, 0.14);
        border: 1px solid rgba(249, 115, 22, 0.24);
    }

    .result-miss {
        color: #fecdd3;
        background: rgba(244, 63, 94, 0.14);
        border: 1px solid rgba(244, 63, 94, 0.24);
    }

    /* Selection warnings */

    .pick-warning {
        padding: 0.9rem 1rem;
        margin: 0.6rem 0;
        border-radius: 13px;
        color: #fde68a;
        background: rgba(245, 158, 11, 0.095);
        border: 1px solid rgba(245, 158, 11, 0.22);
        line-height: 1.58;
    }

    .pick-danger {
        color: #fecdd3;
        background: rgba(244, 63, 94, 0.105);
        border-color: rgba(244, 63, 94, 0.25);
    }

    .pick-info {
        color: #bae6fd;
        background: rgba(56, 189, 248, 0.085);
        border-color: rgba(56, 189, 248, 0.20);
    }

    /* Manual recommendation corner */

    .parlay-hero {
        position: relative;
        overflow: hidden;
        padding: 2rem 2.15rem;
        margin: 0.5rem 0 1.4rem;
        border-radius: 27px;
        background:
            radial-gradient(
                circle at 92% 10%,
                rgba(245, 158, 11, 0.27),
                transparent 29%
            ),
            radial-gradient(
                circle at 5% 100%,
                rgba(139, 92, 246, 0.21),
                transparent 31%
            ),
            linear-gradient(
                130deg,
                rgba(45, 27, 74, 0.94),
                rgba(38, 29, 38, 0.93),
                rgba(8, 44, 54, 0.91)
            );
        border: 1px solid rgba(245, 158, 11, 0.25);
        box-shadow:
            0 30px 90px rgba(0, 0, 0, 0.40),
            inset 0 1px 0 rgba(255, 255, 255, 0.11);
    }

    .parlay-hero::after {
        content: "";
        position: absolute;
        width: 210px;
        height: 210px;
        top: -145px;
        right: -40px;
        border-radius: 50%;
        background: rgba(253, 230, 138, 0.22);
        filter: blur(22px);
    }

    .parlay-eyebrow {
        position: relative;
        z-index: 2;
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.4rem 0.75rem;
        border-radius: 999px;
        color: #fde68a;
        background: rgba(245, 158, 11, 0.12);
        border: 1px solid rgba(245, 158, 11, 0.30);
        font-size: 0.7rem;
        font-weight: 950;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .parlay-hero-title {
        position: relative;
        z-index: 2;
        margin-top: 0.85rem;
        color: white;
        font-size: clamp(1.8rem, 5vw, 2.55rem);
        font-weight: 950;
        letter-spacing: -0.055em;
        line-height: 1.08;
    }

    .parlay-hero-copy {
        position: relative;
        z-index: 2;
        max-width: 790px;
        margin-top: 0.75rem;
        color: #cbd5e1;
        line-height: 1.7;
    }

    .parlay-disclaimer {
        position: relative;
        z-index: 2;
        display: inline-block;
        margin-top: 1rem;
        padding: 0.55rem 0.76rem;
        border-radius: 11px;
        color: #bae6fd;
        background: rgba(56, 189, 248, 0.08);
        border: 1px solid rgba(56, 189, 248, 0.17);
        font-size: 0.78rem;
        font-weight: 750;
    }

    .parlay-post {
        position: relative;
        overflow: hidden;
        padding: 1.35rem 1.45rem;
        margin: 0.8rem 0 0.55rem;
        border-radius: 21px;
        background:
            radial-gradient(
                circle at 100% 0%,
                rgba(245, 158, 11, 0.10),
                transparent 32%
            ),
            linear-gradient(
                145deg,
                rgba(23, 31, 51, 0.95),
                rgba(10, 16, 29, 0.90)
            );
        border: 1px solid rgba(255, 255, 255, 0.095);
        border-left: 4px solid #f59e0b;
        box-shadow:
            0 18px 54px rgba(0, 0, 0, 0.29),
            inset 0 1px 0 rgba(255, 255, 255, 0.045);
    }

    .parlay-post::after {
        content: "✦";
        position: absolute;
        top: 0.55rem;
        right: 1rem;
        color: rgba(253, 230, 138, 0.18);
        font-size: 3.1rem;
        line-height: 1;
    }

    .parlay-post-number {
        position: relative;
        z-index: 2;
        display: inline-block;
        padding: 0.28rem 0.56rem;
        border-radius: 999px;
        color: #fef3c7;
        background:
            linear-gradient(
                135deg,
                rgba(217, 119, 6, 0.36),
                rgba(139, 92, 246, 0.22)
            );
        border: 1px solid rgba(245, 158, 11, 0.28);
        font-size: 0.67rem;
        font-weight: 950;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .parlay-post-title {
        position: relative;
        z-index: 2;
        margin-top: 0.7rem;
        padding-right: 2.2rem;
        color: #fff7d6;
        font-size: 1.28rem;
        font-weight: 950;
        letter-spacing: -0.025em;
    }

    .parlay-post-content {
        position: relative;
        z-index: 2;
        margin-top: 0.8rem;
        color: #d5deeb;
        font-size: 0.98rem;
        line-height: 1.82;
        overflow-wrap: anywhere;
    }

    .parlay-post-meta {
        position: relative;
        z-index: 2;
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem 0.9rem;
        margin-top: 0.95rem;
        padding-top: 0.75rem;
        color: #718096;
        border-top: 1px solid rgba(255, 255, 255, 0.07);
        font-size: 0.75rem;
        font-weight: 700;
    }

    .parlay-photo-label {
        margin: 0.25rem 0 0.4rem;
        color: #94a3b8;
        font-size: 0.76rem;
        font-weight: 800;
    }

    .parlay-divider {
        height: 1px;
        margin: 1.45rem 0;
        background:
            linear-gradient(
                90deg,
                transparent,
                rgba(245, 158, 11, 0.24),
                rgba(139, 92, 246, 0.20),
                transparent
            );
    }

    @media (max-width: 700px) {
        .parlay-hero {
            padding: 1.45rem 1.2rem;
            border-radius: 22px;
        }

        .parlay-post {
            padding: 1.15rem 1.05rem;
        }
    }

    /* Streamlit widgets */

    .stButton > button,
    .stDownloadButton > button {
        min-height: 3rem;
        border-radius: 13px;
        border: 1px solid rgba(255, 255, 255, 0.11);
        font-weight: 850;
        transition:
            transform 0.15s ease,
            box-shadow 0.15s ease,
            border-color 0.15s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        border-color: rgba(245, 158, 11, 0.35);
        box-shadow: 0 11px 30px rgba(0, 0, 0, 0.26);
    }

    [data-testid="stMetric"] {
        padding: 1.02rem;
        border-radius: 17px;
        background:
            linear-gradient(
                145deg,
                rgba(255, 255, 255, 0.052),
                rgba(255, 255, 255, 0.025)
            );
        border: 1px solid rgba(255, 255, 255, 0.078);
        box-shadow: 0 10px 32px rgba(0, 0, 0, 0.19);
    }

    [data-testid="stMetricValue"] {
        font-weight: 950;
        letter-spacing: -0.04em;
    }

    [data-testid="stExpander"] {
        overflow: hidden;
        border-radius: 20px;
        border-color: rgba(255, 255, 255, 0.095);
        background: rgba(255, 255, 255, 0.027);
    }

    [data-testid="stExpander"] summary {
        font-weight: 850;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.55rem;
        padding: 0.36rem;
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.037);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding-left: 1.05rem;
        padding-right: 1.05rem;
        font-weight: 850;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {
        background: rgba(15, 23, 42, 0.86);
        border-color: rgba(255, 255, 255, 0.11);
        color: white;
    }

    hr {
        border-color: rgba(255, 255, 255, 0.08);
    }

    @media (max-width: 700px) {
        .block-container {
            padding-left: 0.78rem;
            padding-right: 0.78rem;
        }

        .portal-hero {
            padding: 1.5rem 1.25rem;
            border-radius: 22px;
        }

        .portal-title {
            font-size: 2.16rem;
        }

        .portal-subtitle {
            font-size: 0.94rem;
        }

        .recommendation-card,
        .match-heading {
            padding: 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. Generic helpers
# ============================================================

def clean_text(value: Any) -> str:
    if value is None:
        return ""

    try:
        missing = pd.isna(value)

        if isinstance(missing, bool) and missing:
            return ""

    except Exception:
        pass

    text = str(value).strip()

    if text.lower() in {
        "nan",
        "none",
        "<na>",
        "nat",
    }:
        return ""

    return text


def clean_lower(value: Any) -> str:
    return clean_text(value).lower()


def clean_upper(value: Any) -> str:
    return clean_text(value).upper()


def clean_identifier(value: Any) -> str:
    text = clean_text(value)

    if re.fullmatch(r"-?\\d+\\.0", text):
        return text[:-2]

    return text


def safe_float(
    value: Any,
    default: Optional[float] = None,
) -> Optional[float]:
    text = clean_text(value)

    if not text:
        return default

    is_percentage = text.endswith("%")

    text = (
        text.replace(",", "")
        .replace("%", "")
        .strip()
    )

    try:
        number = float(text)

    except (TypeError, ValueError):
        return default

    if not math.isfinite(number):
        return default

    if is_percentage:
        number /= 100

    return number


def safe_int(
    value: Any,
    default: int = 0,
) -> int:
    number = safe_float(value)

    if number is None:
        return default

    return int(number)


def safe_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    return clean_lower(value) in {
        "true",
        "1",
        "yes",
        "y",
        "on",
        "heavy",
        "重心",
    }


def escape(value: Any) -> str:
    return html.escape(
        clean_text(value),
        quote=True,
    )


def format_probability(
    value: Any,
    decimals: int = 1,
) -> str:
    number = safe_float(value)

    if number is None:
        return "—"

    if number > 1 and number <= 100:
        number /= 100

    return f"{number * 100:.{decimals}f}%"


def format_odds(
    value: Any,
    decimals: int = 2,
) -> str:
    number = safe_float(value)

    if number is None:
        return "—"

    return f"{number:.{decimals}f}"


def format_line(value: Any) -> str:
    number = safe_float(value)

    if number is None:
        return clean_text(value) or "—"

    if number > 0:
        return f"+{number:g}"

    return f"{number:g}"


def normalize_dataframe(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    output = dataframe.copy()

    output.columns = [
        clean_lower(column)
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
        for column in output.columns
    ]

    return output


def ensure_columns(
    dataframe: pd.DataFrame,
    defaults: Dict[str, Any],
) -> pd.DataFrame:
    output = dataframe.copy()

    for column, default in defaults.items():
        if column not in output.columns:
            output[column] = default

    return output


def fill_aliases(
    dataframe: pd.DataFrame,
    aliases: Dict[str, List[str]],
) -> pd.DataFrame:
    output = dataframe.copy()

    for target, source_columns in aliases.items():
        if target not in output.columns:
            output[target] = ""

        target_blank = (
            output[target]
            .map(clean_text)
            .eq("")
        )

        for source in source_columns:
            if source not in output.columns:
                continue

            source_available = (
                output[source]
                .map(clean_text)
                .ne("")
            )

            mask = target_blank & source_available

            output.loc[mask, target] = (
                output.loc[mask, source]
            )

            target_blank = (
                output[target]
                .map(clean_text)
                .eq("")
            )

    return output


def parse_datetime_value(
    value: Any,
) -> Optional[pd.Timestamp]:
    text = clean_text(value)

    if not text:
        return None

    try:
        parsed = pd.to_datetime(
            text,
            errors="coerce",
            utc=True,
        )

    except Exception:
        return None

    if pd.isna(parsed):
        return None

    return parsed

def google_drive_image_url(value: Any) -> str:
    """
    Convert a Google Drive sharing link created by Google Forms
    into a URL that Streamlit can display.

    The Drive file/folder must allow "Anyone with the link"
    viewer access.
    """
    link = clean_text(value)

    if not link:
        return ""

    file_id = ""

    patterns = [
        r"/file/d/([^/?#]+)",
        r"/d/([^/?#]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, link)

        if match:
            file_id = clean_text(
                match.group(1)
            )
            break

    if not file_id:
        try:
            parsed = urlparse(link)
            parameters = parse_qs(
                parsed.query
            )

            file_id = clean_text(
                parameters.get(
                    "id",
                    [""],
                )[0]
            )

        except Exception:
            file_id = ""

    if not file_id:
        return ""

    return (
        "https://drive.google.com/thumbnail"
        f"?id={quote(file_id, safe='')}"
        "&sz=w1800"
    )


def prepare_parlay_posts(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare Google Form responses.

    Expected normalized columns:
    timestamp, title, recommendation, photo
    """
    defaults = {
        "timestamp": "",
        "title": "",
        "recommendation": "",
        "photo": "",
        "submitted_by": "",
    }

    if dataframe.empty:
        return ensure_columns(
            pd.DataFrame(),
            defaults,
        )

    output = dataframe.copy()

    # Accept a few alternative Google Form question names.
    output = fill_aliases(
        output,
        {
            "timestamp": [
                "submitted_at",
                "submission_time",
                "date",
                "time",
            ],
            "title": [
                "heading",
                "recommendation_title",
                "標題",
            ],
            "recommendation": [
                "content",
                "text",
                "message",
                "recommendation_text",
                "推介",
                "推介內容",
            ],
            "photo": [
                "image",
                "image_url",
                "photo_url",
                "圖片",
            ],
            "submitted_by": [
                "submitted_by",
                "name",
                "author",
                "提交者",
            ],
        },
    )

    output = ensure_columns(
        output,
        defaults,
    )

    for column in defaults:
        output[column] = output[
            column
        ].map(clean_text)

    has_content = (
        output["title"].ne("")
        | output["recommendation"].ne("")
        | output["photo"].ne("")
    )

    output = output[
        has_content
    ].copy()

    output["_timestamp_sort"] = output[
        "timestamp"
    ].map(parse_datetime_value)

    output = output.sort_values(
        "_timestamp_sort",
        ascending=False,
        na_position="last",
    )

    return output.reset_index(drop=True)


def normalize_probability(value: Any) -> Optional[float]:
    number = safe_float(value)

    if number is None:
        return None

    if number > 1 and number <= 100:
        number /= 100

    if number < 0 or number > 1:
        return None

    return number


def normalize_period(value: Any) -> str:
    normalized = (
        clean_upper(value)
        .replace("-", "_")
        .replace(" ", "_")
    )

    aliases = {
        "": "FT",
        "FT": "FT",
        "FULL_TIME": "FT",
        "FULLTIME": "FT",
        "90_MIN": "FT",
        "90_MINUTES": "FT",
        "MATCH": "FT",
        "HT": "HT",
        "HALF_TIME": "HT",
        "HALFTIME": "HT",
        "FIRST_HALF": "HT",
        "1H": "HT",
        "H1": "HT",
        "SECOND_HALF": "2H",
        "2H": "2H",
        "H2": "2H",
    }

    return aliases.get(
        normalized,
        normalized or "FT",
    )


def normalize_market(value: Any) -> str:
    normalized = (
        clean_upper(value)
        .replace("-", "_")
        .replace(" ", "_")
        .replace("/", "_")
    )

    aliases = {
        "ASIAN_HANDICAP": "AH",
        "HANDICAP": "AH",
        "HDP": "AH",
        "OVER_UNDER": "OU",
        "TOTAL": "OU",
        "TOTALS": "OU",
        "GOALS": "OU",
        "MATCH_ODDS": "1X2",
        "MONEYLINE": "1X2",
        "THREE_WAY": "1X2",
        "HOME_HANDICAP_DRAW_AWAY": "HHAD",
        "HANDICAP_1X2": "HHAD",
        "TEAM_TOTAL": "TEAM_OU",
        "TEAM_TOTALS": "TEAM_OU",
        "TEAM_OVER_UNDER": "TEAM_OU",
        "CORRECT_SCORE": "CORRECT_SCORE",
        "SCORE": "CORRECT_SCORE",
        "CS": "CORRECT_SCORE",
    }

    return aliases.get(
        normalized,
        normalized,
    )


def normalize_tier(
    value: Any,
    market: Any = "",
) -> str:
    normalized = (
        clean_upper(value)
        .replace("-", "_")
        .replace(" ", "_")
    )

    if normalize_market(market) == "CORRECT_SCORE":
        return "CORRECT_SCORE"

    aliases = {
        "": "ALTERNATIVE",
        "OFFICIAL": "OFFICIAL",
        "PRIMARY": "OFFICIAL",
        "MAIN": "OFFICIAL",
        "MAIN_PICK": "OFFICIAL",
        "VIP": "OFFICIAL",
        "ALTERNATIVE": "ALTERNATIVE",
        "SECONDARY": "ALTERNATIVE",
        "OPTIONAL": "ALTERNATIVE",
        "AGGRESSIVE": "ALTERNATIVE",
        "CORRECT_SCORE": "CORRECT_SCORE",
        "SCORE": "CORRECT_SCORE",
    }

    return aliases.get(
        normalized,
        normalized or "ALTERNATIVE",
    )


# ============================================================
# Tier / period / result presentation
#
# 這三個函式把內部標準化的字串（OFFICIAL / HT / win …）
# 轉成「中文顯示文字 + CSS class + 整顆卡片 class」，供
# render_recommendation 與結果徽章使用。原本卡片渲染是直接
# 拼字串，統一到這裡之後，新增 tier / period / result 等級
# 只要改這一處。
# ============================================================

def tier_presentation(
    value: Any,
) -> Tuple[str, str, str]:
    """
    Returns (label, pill_class, card_class).

    card_class 是給整顆推薦卡片外框用的（render_recommendation
    會把 is_heavy 的卡片改成 recommendation-card-heavy），
    所以這裡只回傳 tier 本身的樣式。
    """

    tier = normalize_tier(value)

    if tier == "OFFICIAL":
        return (
            "正式推薦",
            "tier-pill tier-official",
            "recommendation-card-official",
        )

    if tier == "CORRECT_SCORE":
        return (
            "波膽參考",
            "tier-pill tier-pill-score",
            "recommendation-card-score",
        )

    if tier == "ALTERNATIVE":
        return (
            "進取備選",
            "tier-pill tier-alternative",
            "recommendation-card-alternative",
        )

    return (
        clean_text(value) or "備選",
        "tier-pill tier-pill-unknown",
        "recommendation-card-alternative",
    )


def period_presentation(
    value: Any,
) -> Tuple[str, str]:
    """Returns (label, pill_class)."""

    period = normalize_period(value)

    if period == "HT":
        return (
            "上半場",
            "period-pill period-ht",
        )

    if period == "2H":
        return (
            "下半場",
            "period-pill period-2h",
        )

    if period == "FT":
        return (
            "全場",
            "period-pill",
        )

    return (
        clean_text(value) or "全場",
        "period-pill",
    )


def result_badge(
    value: Any,
) -> str:
    """
    把結果狀態轉成一段帶 CSS class 的 HTML 徽章。
    傳入 None / 空值 / pending 時回傳空字串，
    避免卡片上出現「待確認」這種無意義標籤。
    """

    if value is None:
        return ""

    normalized = normalize_result(value)

    if not normalized or normalized == "pending":
        return ""

    labels = {
        "win": "全贏",
        "hit": "命中",
        "half_win": "半贏",
        "push": "和局退款",
        "half_loss": "半輸",
        "loss": "全輸",
        "miss": "未命中",
    }

    classes = {
        "win": "result-badge result-hit",
        "hit": "result-badge result-hit",
        "half_win": "result-badge result-half-win",
        "push": "result-badge result-push",
        "half_loss": "result-badge result-half-loss",
        "loss": "result-badge result-miss",
        "miss": "result-badge result-miss",
    }

    label = labels.get(
        normalized,
        clean_text(value),
    )

    css_class = classes.get(
        normalized,
        "result-badge result-push",
    )

    return (
        f'<span class="{css_class}">'
        f'{escape(label)}</span>'
    )


def normalize_status(value: Any) -> str:
    normalized = (
        clean_lower(value)
        .replace("-", "_")
        .replace(" ", "_")
    )

    aliases = {
        "publish": "published",
        "published": "published",
        "active": "published",
        "upcoming": "published",
        "open": "published",
        "live": "published",
        "ended": "ended",
        "complete": "ended",
        "completed": "ended",
        "finished": "ended",
        "settled": "ended",
        "closed": "ended",
        "draft": "draft",
        "hidden": "draft",
    }

    return aliases.get(
        normalized,
        normalized,
    )


def normalize_result(value: Any) -> str:
    normalized = (
        clean_lower(value)
        .replace("-", "_")
        .replace(" ", "_")
    )

    aliases = {
        "full_win": "win",
        "won": "win",
        "winner": "win",
        "hit": "hit",
        "win": "win",
        "halfwin": "half_win",
        "half_win": "half_win",
        "void": "push",
        "refund": "push",
        "draw": "push",
        "push": "push",
        "halfloss": "half_loss",
        "half_loss": "half_loss",
        "full_loss": "loss",
        "lost": "loss",
        "miss": "miss",
        "loss": "loss",
        "pending": "pending",
    }

    return aliases.get(
        normalized,
        normalized,
    )


def stable_recommendation_id(
    row: Dict[str, Any],
    row_number: Any,
) -> str:
    explicit = clean_identifier(
        row.get("rec_id")
    )

    if explicit:
        return explicit

    identity = "|".join([
        clean_identifier(row.get("match_id")),
        normalize_period(row.get("period")),
        normalize_market(row.get("market")),
        clean_upper(row.get("market_scope")),
        clean_upper(row.get("selection")),
        clean_text(row.get("line")),
        clean_text(row.get("rec_title")),
        clean_text(row.get("rank")),
        clean_text(row_number),
    ])

    digest = hashlib.sha256(
        identity.encode("utf-8")
    ).hexdigest()[:18]

    return f"auto_{digest}"


# ============================================================
# 4. Google Sheets
# ============================================================

def get_sheet_id() -> str:
    try:
        configured = clean_text(
            st.secrets["sheets"]["sheet_id"]
        )

        return configured or DEFAULT_SHEET_ID

    except Exception:
        return DEFAULT_SHEET_ID


def sheet_csv_url(
    worksheet_name: str,
) -> str:
    return (
        "https://docs.google.com/spreadsheets/d/"
        f"{get_sheet_id()}/gviz/tq?"
        "tqx=out:csv&sheet="
        f"{quote(worksheet_name, safe='')}"
    )


@st.cache_data(
    ttl=30,
    show_spinner=False,
)
def fetch_sheet(
    worksheet_name: str,
) -> pd.DataFrame:
    try:
        dataframe = pd.read_csv(
            sheet_csv_url(worksheet_name),
            dtype=str,
            keep_default_na=False,
        )

        return normalize_dataframe(
            dataframe
        )

    except Exception:
        return pd.DataFrame()


def load_portal_data() -> Tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    return (
        fetch_sheet("users"),
        fetch_sheet("matches"),
        fetch_sheet("recommendations"),
    )


# ============================================================
# 5. Authentication
# ============================================================

def allow_plaintext_passwords() -> bool:
    try:
        configured = st.secrets[
            "security"
        ].get(
            "allow_plaintext_passwords",
            True,
        )

        return safe_bool(configured)

    except Exception:
        # Kept enabled for compatibility with the original sheet.
        return True


def verify_sha256_password(
    password: str,
    stored_value: str,
) -> bool:
    stored = clean_text(stored_value)

    if not stored.startswith("sha256:"):
        return False

    expected = stored.split(":", 1)[1].lower()

    calculated = hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()

    return hmac.compare_digest(
        calculated,
        expected,
    )


def verify_pbkdf2_password(
    password: str,
    stored_value: str,
) -> bool:
    """
    Supported format:

    pbkdf2_sha256$260000$salt$hex_digest
    """
    stored = clean_text(stored_value)

    if not stored.startswith(
        "pbkdf2_sha256$"
    ):
        return False

    try:
        _, iterations_text, salt, expected = (
            stored.split("$", 3)
        )

        iterations = int(iterations_text)

        if iterations < 100_000:
            return False

        calculated = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        ).hex()

        return hmac.compare_digest(
            calculated,
            expected.lower(),
        )

    except Exception:
        return False


def verify_password(
    password: str,
    user: Dict[str, Any],
    columns: Set[str],
) -> bool:
    password_hash = clean_text(
        user.get("password_hash")
    )

    if password_hash:
        if verify_pbkdf2_password(
            password,
            password_hash,
        ):
            return True

        if verify_sha256_password(
            password,
            password_hash,
        ):
            return True

    if (
        allow_plaintext_passwords()
        and "password" in columns
    ):
        stored_plaintext = clean_text(
            user.get("password")
        )

        if stored_plaintext:
            return hmac.compare_digest(
                password,
                stored_plaintext,
            )

    return False


def parse_expiry_date(
    value: Any,
) -> Optional[datetime]:
    text = clean_text(value)

    if not text:
        return None

    try:
        return datetime.strptime(
            text,
            "%Y-%m-%d",
        )

    except ValueError:
        return None


def authenticate(
    users: pd.DataFrame,
    username: str,
    password: str,
) -> Tuple[
    bool,
    Optional[Dict[str, Any]],
    str,
]:
    normalized_username = clean_lower(
        username
    )

    password = clean_text(password)

    if not normalized_username or not password:
        return (
            False,
            None,
            "請輸入用戶名及密碼。",
        )

    if users.empty:
        return (
            False,
            None,
            "暫時無法讀取會員資料，請稍後再試。",
        )

    if "username" not in users.columns:
        return (
            False,
            None,
            "會員資料格式不正確：缺少 username 欄位。",
        )

    matched = users[
        users["username"]
        .map(clean_lower)
        .eq(normalized_username)
    ]

    if matched.empty:
        return (
            False,
            None,
            "用戶名或密碼錯誤。",
        )

    user = matched.iloc[0].to_dict()

    if not verify_password(
        password,
        user,
        set(users.columns),
    ):
        return (
            False,
            None,
            "用戶名或密碼錯誤。",
        )

    if clean_lower(user.get("status")) != "active":
        return (
            False,
            None,
            "您的會員帳戶目前並非啟用狀態。",
        )

    expiry_text = clean_text(
        user.get("expiry_date")
    )

    expiry = parse_expiry_date(
        expiry_text
    )

    if expiry is None:
        return (
            False,
            None,
            "會員到期日期格式錯誤，應為 YYYY-MM-DD。",
        )

    if datetime.now().date() > expiry.date():
        return (
            False,
            None,
            (
                f"您的會籍已於 {expiry_text} 到期，"
                "請聯絡雨姐續期。"
            ),
        )

    return (
        True,
        {
            "username": clean_text(
                user.get("username")
            ),
            "expiry_date": expiry_text,
        },
        "登入成功。",
    )


def validate_logged_in_member(
    users: pd.DataFrame,
    session_user: Dict[str, Any],
) -> Tuple[bool, str]:
    """
    Rechecks status and expiry without requiring the password.

    If the users sheet is temporarily unavailable, the current
    session is preserved rather than immediately logging the
    member out.
    """
    if users.empty or "username" not in users.columns:
        return True, ""

    username = clean_lower(
        session_user.get("username")
    )

    matched = users[
        users["username"]
        .map(clean_lower)
        .eq(username)
    ]

    if matched.empty:
        return (
            False,
            "會員帳戶已不存在或已被移除。",
        )

    user = matched.iloc[0].to_dict()

    if clean_lower(user.get("status")) != "active":
        return (
            False,
            "會員帳戶已暫停使用。",
        )

    expiry_text = clean_text(
        user.get("expiry_date")
    )

    expiry = parse_expiry_date(
        expiry_text
    )

    if expiry is None:
        return (
            False,
            "會員到期日期格式錯誤。",
        )

    if datetime.now().date() > expiry.date():
        return (
            False,
            f"會籍已於 {expiry_text} 到期。",
        )

    st.session_state.portal_user = {
        "username": clean_text(
            user.get("username")
        ),
        "expiry_date": expiry_text,
    }

    return True, ""


# ============================================================
# 6. Data preparation
# ============================================================

RECOMMENDATION_ALIASES = {
    "rec_id": [
        "recommendation_id",
        "pick_id",
        "id",
    ],
    "match_id": [
        "fixture_id",
        "event_id",
        "game_id",
    ],
    "rec_title": [
        "title",
        "label",
        "recommendation",
        "pick_title",
    ],
    "period": [
        "timeframe",
        "match_period",
    ],
    "market": [
        "market_type",
        "bet_type",
    ],
    "market_scope": [
        "subject",
        "team",
        "team_name",
        "market_subject",
    ],
    "selection": [
        "pick",
        "side",
        "outcome",
    ],
    "line": [
        "handicap",
        "total_line",
        "market_line",
    ],
    "odds": [
        "hkjc_odds",
        "offered_odds",
        "market_odds",
        "price",
    ],
    "conservative_hit": [
        "hit_probability_low",
        "probability_low",
        "minimum_hit_probability",
    ],
    "median_hit": [
        "hit_probability",
        "hit_probability_median",
        "probability_median",
        "model_probability",
    ],
    "nonloss_probability": [
        "non_loss_probability",
        "probability_nonloss",
    ],
    "full_loss_probability": [
        "loss_probability",
        "probability_full_loss",
    ],
    "fair_odds": [
        "model_fair_odds",
        "central_fair_odds",
    ],
    "edge": [
        "value_edge",
        "model_edge",
    ],
    "expected_value": [
        "ev",
        "model_ev",
    ],
    "commentary": [
        "analysis",
        "short_comment",
        "summary",
    ],
    "is_heavy": [
        "heavy",
        "main_focus",
    ],
    "conflict_ids": [
        "conflicts",
    ],
    "compatibility_group": [
        "compatibility_key",
        "market_group",
    ],
}

MATCH_ALIASES = {
    "match_id": [
        "fixture_id",
        "event_id",
        "game_id",
    ],
    "match_name": [
        "fixture",
        "event_name",
        "game_name",
    ],
    "home_team": [
        "home",
        "home_name",
    ],
    "away_team": [
        "away",
        "away_name",
    ],
    "competition": [
        "league",
        "tournament",
    ],
    "kickoff": [
        "kickoff_time",
        "start_time",
        "match_time",
    ],
    "model_direction": [
        "direction",
        "primary_direction",
    ],
    "model_summary": [
        "summary",
        "analysis",
    ],
    "top_scores": [
        "correct_scores",
        "score_reference",
    ],
    "final_score": [
        "score",
        "result_score",
    ],
}


def prepare_recommendations(
    recommendations: pd.DataFrame,
) -> pd.DataFrame:
    if recommendations.empty:
        return ensure_columns(
            pd.DataFrame(),
            RECOMMENDATION_DEFAULTS,
        )

    output = fill_aliases(
        recommendations,
        RECOMMENDATION_ALIASES,
    )

    output = ensure_columns(
        output,
        RECOMMENDATION_DEFAULTS,
    )

    output["match_id"] = output[
        "match_id"
    ].map(clean_identifier)

    output["period"] = output[
        "period"
    ].map(normalize_period)

    output["market"] = output[
        "market"
    ].map(normalize_market)

    output["market_scope"] = output[
        "market_scope"
    ].map(clean_upper)

    output["selection"] = output[
        "selection"
    ].map(clean_upper)

    output["tier"] = [
        normalize_tier(tier, market)
        for tier, market in zip(
            output["tier"],
            output["market"],
        )
    ]

    output["status"] = output[
        "status"
    ].map(normalize_status)

    output["result"] = output[
        "result"
    ].map(normalize_result)

    output["is_heavy"] = output[
        "is_heavy"
    ].map(safe_bool)

    output["rank"] = output[
        "rank"
    ].map(
        lambda value: safe_int(
            value,
            999,
        )
    )

    output["stars"] = output[
        "stars"
    ].map(
        lambda value: max(
            1,
            min(
                5,
                safe_int(value, 3),
            ),
        )
    )

    numeric_columns = [
        "line",
        "odds",
        "fair_odds",
        "edge",
        "expected_value",
    ]

    for column in numeric_columns:
        output[column] = output[
            column
        ].map(safe_float)

    probability_columns = [
        "conservative_hit",
        "median_hit",
        "nonloss_probability",
        "full_loss_probability",
    ]

    for column in probability_columns:
        output[column] = output[
            column
        ].map(normalize_probability)

    output["rec_title"] = output[
        "rec_title"
    ].map(clean_text)

    output["rec_id"] = [
        stable_recommendation_id(
            row.to_dict(),
            index,
        )
        for index, row in output.iterrows()
    ]

    return output.reset_index(drop=True)


def derive_matches_from_recommendations(
    recommendations: pd.DataFrame,
) -> pd.DataFrame:
    if (
        recommendations.empty
        or "match_id" not in recommendations.columns
    ):
        return ensure_columns(
            pd.DataFrame(),
            MATCH_DEFAULTS,
        )

    rows: List[Dict[str, Any]] = []

    for match_id, group in recommendations.groupby(
        "match_id",
        dropna=False,
    ):
        normalized_id = clean_identifier(
            match_id
        )

        if not normalized_id:
            continue

        statuses = group[
            "status"
        ].map(normalize_status)

        status = (
            "ended"
            if not statuses.empty
            and statuses.eq("ended").all()
            else "published"
        )

        rows.append({
            **MATCH_DEFAULTS,
            "match_id": normalized_id,
            "match_name": normalized_id,
            "status": status,
        })

    return pd.DataFrame(rows)


def prepare_matches(
    matches: pd.DataFrame,
    recommendations: pd.DataFrame,
) -> pd.DataFrame:
    if matches.empty:
        return derive_matches_from_recommendations(
            recommendations
        )

    output = fill_aliases(
        matches,
        MATCH_ALIASES,
    )

    output = ensure_columns(
        output,
        MATCH_DEFAULTS,
    )

    output["match_id"] = output[
        "match_id"
    ].map(clean_identifier)

    output["status"] = output[
        "status"
    ].map(normalize_status)

    recommendation_statuses: Dict[str, str] = {}

    if not recommendations.empty:
        for match_id, group in recommendations.groupby(
            "match_id"
        ):
            statuses = group[
                "status"
            ].map(normalize_status)

            recommendation_statuses[
                clean_identifier(match_id)
            ] = (
                "ended"
                if not statuses.empty
                and statuses.eq("ended").all()
                else "published"
            )

    for index, row in output.iterrows():
        match_id = clean_identifier(
            row.get("match_id")
        )

        if not clean_text(row.get("status")):
            output.at[index, "status"] = (
                recommendation_statuses.get(
                    match_id,
                    "",
                )
            )

        match_name = clean_text(
            row.get("match_name")
        )

        if not match_name:
            home = clean_text(
                row.get("home_team")
            )

            away = clean_text(
                row.get("away_team")
            )

            if home and away:
                output.at[
                    index,
                    "match_name",
                ] = f"{home} vs {away}"

            else:
                output.at[
                    index,
                    "match_name",
                ] = match_id

    output = output[
        output["match_id"]
        .map(clean_text)
        .ne("")
    ]

    output = output.drop_duplicates(
        subset=["match_id"],
        keep="last",
    )

    return output.reset_index(drop=True)


# ============================================================
# Analysis table helpers
#
# analysis 表由 GAS 端的 publish_analysis 寫入，裡面六個欄位
# 都是「已經被 JSON.stringify 過的字串」。Portal 要拿來渲染
# 前必須反序列化；另外 Sheet 可能回傳真正的空字串、
# 被截斷的字串，或是已經被 decode 成 dict 的值，
# 這裡全部兜在一個函式裡統一處理。
# ============================================================

def parse_json_field(
    value: Any,
) -> Any:
    """
    把 analysis 表裡的 JSON 字串還原成 Python 物件。
    傳入 None / 空字串 / 非字串值時原樣回傳（dict / list
    會直接被上層當成已解析的資料使用）。
    """

    if value is None:
        return None

    if isinstance(
        value,
        (dict, list),
    ):
        return value

    text = clean_text(value)

    if not text:
        return None

    try:
        decoded = json.loads(text)
    except (TypeError, ValueError):
        return None

    # Sheet 儲存格在 50,000 字元處被截斷時會留下不完整的
    # JSON，parse 一定會失敗，上面已經兜掉，這裡只回 None。
    return decoded


def prepare_analysis(
    analysis: pd.DataFrame,
) -> pd.DataFrame:
    """
    把 raw analysis sheet 規整成一張以 match_id 為 key、
    *_json 欄位已反序列化的表。同一場比賽有多筆時保留最新
    （updated_at 最大）那筆。
    """

    if analysis is None or (
        isinstance(
            analysis,
            pd.DataFrame,
        )
        and analysis.empty
    ):
        return pd.DataFrame(
            columns=[
                "match_id",
                "model_quality_status",
                "ht_ft_coherence_status",
                "odds_movement_status",
                "model_direction",
                "engine_version",
                "runtime_seconds",
                "published_at",
                "updated_at",
                "movement_audits_json",
                "family_out_json",
                "stress_audits_json",
                "prior_comparison_json",
                "correct_scores_json",
                "consensus_json",
            ]
        )

    if not isinstance(
        analysis,
        pd.DataFrame,
    ):
        # 容錯：若傳入的是 dict / list，先包成 DataFrame
        try:
            analysis = pd.DataFrame(list(analysis))
        except (TypeError, ValueError):
            return pd.DataFrame()

    if analysis.empty:
        return pd.DataFrame(
            columns=list(
                analysis.columns
            )
            or []
        )

    output = analysis.copy()

    if "match_id" in output.columns:
        output["match_id"] = output[
            "match_id"
        ].map(clean_identifier)

    # *_json 欄位一律反序列化，讓下游 panel 可以直接當 dict 用
    for column in output.columns:
        if not isinstance(
            column,
            str,
        ):
            continue

        if column.endswith("_json"):
            output[column] = output[
                column
            ].map(parse_json_field)

    # 同一場可能有多筆（多次 publish），保留 updated_at 最新的
    if (
        "updated_at" in output.columns
        and "match_id" in output.columns
        and not output.empty
    ):
        output = output.sort_values(
            by="updated_at",
            ascending=False,
            na_position="first",
        )

        output = output.drop_duplicates(
            subset=["match_id"],
            keep="first",
        )

    return output.reset_index(drop=True)


def analysis_for_match(
    analysis_df: pd.DataFrame,
    match_id: str,
) -> Optional[Dict[str, Any]]:
    """
    從已處理好的 analysis 表撈出某一場的遙測記錄。
    找不到時回傳 None，呼叫端應把它當成「沒有資料」處理，
    而不是顯示空面板。
    """

    if analysis_df is None or not isinstance(
        analysis_df,
        pd.DataFrame,
    ):
        return None

    if analysis_df.empty:
        return None

    target = clean_identifier(match_id)

    if not target:
        return None

    if "match_id" not in analysis_df.columns:
        return None

    matches = analysis_df[
        analysis_df["match_id"]
        .map(clean_identifier)
        .eq(target)
    ]

    if matches.empty:
        return None

    record = matches.iloc[0].to_dict()

    return {
        key: value
        for key, value in record.items()
        if isinstance(
            key,
            str
        )
    }



    visible_matches = matches[
        matches["status"].isin(
            VISIBLE_STATUSES
        )
    ].copy()

    visible_recommendations = recommendations[
        recommendations["status"].isin(
            VISIBLE_STATUSES
        )
    ].copy()

    visible_match_ids = {
        clean_identifier(value)
        for value in visible_matches["match_id"]
        if clean_identifier(value)
    }

    visible_recommendations = (
        visible_recommendations[
            visible_recommendations[
                "match_id"
            ]
            .map(clean_identifier)
            .isin(visible_match_ids)
        ]
    )

    return (
        visible_matches.reset_index(drop=True),
        visible_recommendations.reset_index(
            drop=True
        ),
    )


# ============================================================
# 8. Personal selection state
# ============================================================

def selected_ids() -> Set[str]:
    return set(
        st.session_state.get(
            "my_pick_ids",
            [],
        )
    )


def add_pick(rec_id: str) -> None:
    ids = selected_ids()

    if rec_id not in ids:
        ids.add(rec_id)

        st.session_state.my_pick_ids = (
            list(ids)
        )


def remove_pick(rec_id: str) -> None:
    ids = selected_ids()

    if rec_id in ids:
        ids.remove(rec_id)

        st.session_state.my_pick_ids = (
            list(ids)
        )


def clear_all_picks() -> None:
    st.session_state.my_pick_ids = []


# ============================================================
# Selection conflict checks
#
# 使用者在「我的選擇」頁面挑了多條推薦後，這裡做一次交叉檢查：
#   - 同一場比賽選了互斥盤口（compatibility_group 相同，
#     engine 已經標記 conflict_ids）
#   - 同一場選了超過一定數量的注項（過度集中）
#   - 命中率 / 期望值的極端情況
#
# 回傳 dict 清單，每個 dict 有 severity（danger/warning/info）
# 與 message，前端照 severity 套 pick-warning / pick-danger /
# pick-info 樣式。
# ============================================================

MAX_PICKS_PER_MATCH = 4


def selection_warnings(
    rows: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    if not rows:
        return []

    warnings: List[Dict[str, Any]] = []

    normalized: List[Dict[str, Any]] = [
        {
            "rec_id": clean_identifier(row.get("rec_id")),
            "match_id": clean_identifier(
                row.get("match_id")
            ),
            "tier": normalize_tier(row.get("tier")),
            "period": normalize_period(row.get("period")),
            "market": normalize_market(row.get("market")),
            "market_scope": clean_upper(
                row.get("market_scope")
            ),
            "selection": clean_upper(row.get("selection")),
            "line": safe_float(row.get("line")),
            "odds": safe_float(row.get("odds")),
            "compatibility_group": clean_text(
                row.get("compatibility_group")
            ),
            "conflict_ids": _split_conflict_ids(
                row.get("conflict_ids")
            ),
            "median_hit": normalize_probability(
                row.get("median_hit")
            ),
        }
        for row in rows
        if isinstance(row, dict)
    ]

    # ---- 1. 明確衝突：engine 已標記 conflict_ids ----
    selected_ids = {
        item["rec_id"]
        for item in normalized
        if item["rec_id"]
    }

    for item in normalized:
        for conflict_id in item["conflict_ids"]:
            if conflict_id in selected_ids:
                warnings.append({
                    "severity": "danger",
                    "message": (
                        f"直接衝突：{escape(item['rec_id'] or '本項')} "
                        f"與 {escape(conflict_id)} "
                        f"互斥，兩者不應同時下注。"
                    ),
                })

    # ---- 2. 同一 compatibility_group 內選多項 ----
    groups: Dict[str, List[Dict[str, Any]]] = {}

    for item in normalized:
        group = item["compatibility_group"]

        if not group:
            continue

        groups.setdefault(
            group,
            []
        ).append(item)

    for group, items in groups.items():
        if len(items) > 1:
            names = ", ".join(
                escape(item["rec_id"] or "項目")
                for item in items
            )

            warnings.append({
                "severity": "warning",
                "message": (
                    f"相容性群組「{escape(group)}」內已選 {len(items)} 項"
                    f"（{names}），請確認是否為刻意分散風險。"
                ),
            })

    # ---- 3. 同一場選了過多注項 ----
    by_match: Dict[str, List[Dict[str, Any]]] = {}

    for item in normalized:
        if not item["match_id"]:
            continue

        by_match.setdefault(
            item["match_id"],
            []
        ).append(item)

    for match_id, items in by_match.items():
        if len(items) > MAX_PICKS_PER_MATCH:
            warnings.append({
                "severity": "warning",
                "message": (
                    f"單場過度集中：{escape(match_id)} 已選 "
                    f"{len(items)} 項，建議不超過 "
                    f"{MAX_PICKS_PER_MATCH} 項。"
                ),
            })

    # ---- 4. 同一場、同一時段、同盤口但相反 selection ----
    for match_id, items in by_match.items():
        for i, first in enumerate(items):
            for second in items[i + 1:]:
                if (
                    first["period"] == second["period"]
                    and first["market"] == second["market"]
                    and first["market_scope"]
                    == second["market_scope"]
                    and first["line"] == second["line"]
                    and first["selection"]
                    and second["selection"]
                    and first["selection"]
                    != second["selection"]
                ):
                    warnings.append({
                        "severity": "danger",
                        "message": (
                            f"同一盤口相反方向："
                            f"{escape(first['rec_id'])} 與 "
                            f"{escape(second['rec_id'])} "
                            f"為互斥盤口。"
                        ),
                    })

    # ---- 5. 賠率過低提醒 ----
    for item in normalized:
        odds = item["odds"]

        if (
            odds is not None
            and odds < 1.05
        ):
            warnings.append({
                "severity": "info",
                "message": (
                    f"{escape(item['rec_id'] or '項目')} "
                    f"賠率過低（{odds:.2f}），"
                    f"扣水後幾乎沒有預期回報。"
                ),
            })

    # 去重並限制數量，避免長清單淹沒畫面
    seen = set()
    deduped: List[Dict[str, Any]] = []

    for warning in warnings:
        key = (
            warning["severity"],
            warning["message"],
        )

        if key in seen:
            continue

        seen.add(key)
        deduped.append(warning)

    return deduped[:12]


def _split_conflict_ids(value: Any) -> List[str]:
    """
    把 conflict_ids 欄位統一拆成字串清單。
    可接受逗號分隔字串、JSON 陣列、單一字串或 None。
    """

    if value is None:
        return []

    if isinstance(
        value,
        (list, tuple),
    ):
        return [
            clean_identifier(item)
            for item in value
            if clean_text(item)
        ]

    if isinstance(
        value,
        str,
    ):
        text = value.strip()

        if not text or text.lower() == "none":
            return []

        # 已經是 JSON 陣列字串就直接 parse
        if text.startswith("["):
            try:
                parsed = json.loads(text)

                if isinstance(
                    parsed,
                    list,
                ):
                    return [
                        clean_identifier(item)
                        for item in parsed
                        if clean_text(item)
                    ]
            except (TypeError, ValueError):
                pass

        # 退化成逗號分隔
        return [
            clean_identifier(part)
            for part in text.split(",")
            if clean_text(part)
        ]

    return []


# ============================================================
# Expected value formatting
# ============================================================

def format_ev(
    value: Any,
    precision: int = 1,
) -> str:
    """
    把期望值格式化成「+12.3% / -5.4%」的形式。
    None、0 或無效值顯示成中性的「0.0%」。
    """

    number = safe_float(value)

    if number is None:
        return "0.0%"

    percentage = number * 100.0

    if abs(percentage) < 0.05:
        return "0.0%"

    if percentage > 0:
        return (
            f"+{percentage:.{precision}f}%"
        )

    return (
        f"{percentage:.{precision}f}%"
    )



def update_pick_selection(
    rec_id: str,
    widget_key: str,
) -> None:
    checked = bool(
        st.session_state.get(
            widget_key,
            False,
        )
    )

    if checked:
        add_pick(rec_id)
    else:
        remove_pick(rec_id)


def recommendation_identity(
    row: Dict[str, Any],
) -> str:
    rec_id = clean_identifier(
        row.get("rec_id")
    )

    if rec_id:
        return rec_id

    return stable_recommendation_id(
        row,
        row.get("index", ""),
    )


def recommendation_title(
    row: Dict[str, Any],
) -> str:
    title = clean_text(
        row.get("rec_title")
    )

    if title:
        return title

    selection = clean_text(
        row.get("selection")
    )

    line = safe_float(
        row.get("line")
    )

    if selection and line is not None:
        return (
            f"{selection} "
            f"{format_line(line)}"
        )

    return selection or "未命名選擇"


# ============================================================
# 9. Status translations (V3)
# ============================================================

def movement_status_chinese(
    value: Any,
) -> str:
    translations = {
        "SUPPORTED": "莊家同向",
        "CONFLICTED": "莊家衝突",
        "NEUTRAL": "中性",
        "NOT_AVAILABLE": "無數據",
        "NOT_PROVIDED": "未提供",
        "STRENGTHENING": "持續加強",
        "WEAKENING": "持續減弱",
    }

    text = clean_upper(value)

    if not text:
        return "—"

    return translations.get(
        text,
        text.replace("_", " "),
    )


def movement_status_class(
    value: Any,
) -> str:
    text = clean_upper(value)

    if text in {
        "SUPPORTED",
        "STRENGTHENING",
    }:
        return "mv-sup"

    if text in {
        "CONFLICTED",
        "WEAKENING",
    }:
        return "mv-con"

    if text == "NEUTRAL":
        return "mv-neu"

    return "mv-na"


def robustness_status_chinese(
    value: Any,
) -> str:
    translations = {
        "ROBUST": "穩健",
        "FRAGILE": "脆弱",
        "PASS": "通過",
        "FAIL": "失敗",
        "NOT_AVAILABLE": "無數據",
        "NOT_PROVIDED": "未提供",
    }

    text = clean_upper(value)

    if not text:
        return "—"

    return translations.get(
        text,
        text.replace("_", " "),
    )


# ============================================================
# 10. Recommendation renderer (V3-aware)
# ============================================================

def render_recommendation(
    row: Dict[str, Any],
    *,
    allow_selection: bool = True,
) -> None:
    rec_id = recommendation_identity(
        row
    )

    tier_label, tier_class, card_class = (
        tier_presentation(
            row.get("tier")
        )
    )

    period_label, period_class = (
        period_presentation(
            row.get("period")
        )
    )

    heavy = safe_bool(
        row.get("is_heavy")
    )

    if heavy:
        card_class = (
            "recommendation-card-heavy"
        )

    title = escape(
        recommendation_title(row)
    )

    odds = safe_float(
        row.get("odds")
    )

    conservative_hit = safe_float(
        row.get("conservative_hit")
    )

    median_hit = safe_float(
        row.get("median_hit")
    )

    nonloss = safe_float(
        row.get("nonloss_probability")
    )

    full_loss = safe_float(
        row.get("full_loss_probability")
    )

    fair_odds = safe_float(
        row.get("fair_odds")
    )

    edge = safe_float(
        row.get("edge")
    )

    expected_value = safe_float(
        row.get("expected_value")
    )

    line = safe_float(
        row.get("line")
    )

    stars = max(
        1,
        min(
            5,
            safe_int(
                row.get("stars"),
                3,
            ),
        ),
    )

    commentary = escape(
        row.get("commentary")
    )

    market = escape(
        normalize_market(
            row.get("market")
        )
    )

    market_scope = escape(
        row.get("market_scope")
    )

    price_status = escape(
        row.get("price_status")
    )

    heavy_html = (
        '<span class="heavy-pill">'
        "🔥 重心"
        "</span>"
        if heavy
        else ""
    )

    odds_html = (
        ' · <span class="rec-odds">@{o}</span>'.format(
            o=format_odds(odds)
        )
        if odds is not None
        else ""
    )

    # ---- V3 movement chip ----
    movement_chips: List[str] = []

    verdict = clean_upper(
        row.get("movement_verdict")
    )

    if verdict:
        cls = movement_status_class(
            verdict
        )

        verdict_label = (
            movement_status_chinese(verdict)
        )

        strength = clean_upper(
            row.get("movement_strength")
        )

        if strength:
            verdict_label += (
                " · "
                + movement_status_chinese(strength)
            )

        movement_chips.append(
            f'<div class="stat-chip {cls}">'
            "📈 走勢 "
            f"<strong>{verdict_label}</strong>"
            "</div>"
        )

        change_pp = safe_float(
            row.get(
                "movement_probability_change_pp"
            )
        )

        if change_pp is not None:
            sign = "+" if change_pp >= 0 else ""

            movement_chips.append(
                '<div class="stat-chip {cls}">概率變動 '
                '<strong>{sign}{pp:.2f}pp</strong></div>'.format(
                    cls=cls,
                    sign=sign,
                    pp=change_pp,
                )
            )

        agreement = safe_float(
            row.get(
                "movement_agreement_ratio"
            )
        )

        if agreement is not None:
            movement_chips.append(
                '<div class="stat-chip mv-na">莊家一致 '
                '<strong>{p}</strong></div>'.format(
                    p=format_probability(agreement),
                )
            )

    family_status = clean_upper(
        row.get("family_out_status")
    )

    if family_status:
        fam_cls = (
            "mv-sup"
            if family_status == "ROBUST"
            else (
                "mv-con"
                if family_status == "FRAGILE"
                else "mv-na"
            )
        )

        movement_chips.append(
            '<div class="stat-chip {cls}">🛡️ 穩健性 '
            '<strong>{label}</strong></div>'.format(
                cls=fam_cls,
                label=robustness_status_chinese(family_status),
            )
        )

    statistics: List[str] = []

    if conservative_hit is not None:
        statistics.append(
            "<div class='stat-chip'>"
            "保守命中 "
            f"<strong>{format_probability(conservative_hit)}</strong>"
            "</div>"
        )

    if median_hit is not None:
        statistics.append(
            "<div class='stat-chip'>"
            "中位命中 "
            f"<strong>{format_probability(median_hit)}</strong>"
            "</div>"
        )

    if nonloss is not None:
        statistics.append(
            "<div class='stat-chip'>"
            "不輸概率 "
            f"<strong>{format_probability(nonloss)}</strong>"
            "</div>"
        )

    if full_loss is not None:
        statistics.append(
            "<div class='stat-chip'>"
            "全輸風險 "
            f"<strong>{format_probability(full_loss)}</strong>"
            "</div>"
        )

    if fair_odds is not None:
        statistics.append(
            "<div class='stat-chip'>"
            "模型公平賠率 "
            f"<strong>{format_odds(fair_odds)}</strong>"
            "</div>"
        )

    if edge is not None:
        edge_display = (
            edge / 100
            if abs(edge) > 1
            else edge
        )

        statistics.append(
            "<div class='stat-chip'>"
            "模型 Edge "
            f"<strong>{format_probability(edge_display)}</strong>"
            "</div>"
        )

    if expected_value is not None:
        ev_display = (
            expected_value / 100
            if abs(expected_value) > 1
            else expected_value
        )

        statistics.append(
            "<div class='stat-chip'>"
            "EV "
            f"<strong>{format_probability(ev_display)}</strong>"
            "</div>"
        )

    if market:
        statistics.append(
            "<div class='stat-chip'>"
            f"{market}"
            "</div>"
        )

    if market_scope:
        statistics.append(
            "<div class='stat-chip'>"
            f"{market_scope}"
            "</div>"
        )

    if line is not None:
        statistics.append(
            "<div class='stat-chip'>"
            "盤口 "
            f"<strong>{format_line(line)}</strong>"
            "</div>"
        )

    if price_status:
        statistics.append(
            "<div class='stat-chip'>"
            f"{price_status}"
            "</div>"
        )

    statistics.extend(
        movement_chips
    )

    commentary_class = (
        "commentary commentary-heavy"
        if heavy
        else "commentary"
    )

    commentary_html = (
        f"""
        <div class="{commentary_class}">
            🗣️ <strong>雨姐短評：</strong>
            {commentary}
        </div>
        """
        if commentary
        else ""
    )

    render_html(
        f"""
        <div class="recommendation-card {card_class}">
            <span class="tier-pill {tier_class}">
                {tier_label}
            </span>

            <span class="{period_class}">
                {period_label}
            </span>

            {heavy_html}

            <div class="rec-title">
                {title}{odds_html}
            </div>

            <div class="star-row">
                {"⭐" * stars}
            </div>

            <div class="rec-stats">
                {"".join(statistics)}
            </div>

            {commentary_html}
            {result_badge(row.get("result"))}
        </div>
        """
    )

    status = normalize_status(
        row.get("status")
    )

    if (
        allow_selection
        and status != "ended"
        and rec_id
    ):
        widget_key = (
            f"pick_checkbox_{rec_id}"
        )

        if widget_key not in st.session_state:
            st.session_state[
                widget_key
            ] = rec_id in selected_ids()

        st.checkbox(
            "加入「我的選擇」",
            key=widget_key,
            on_change=update_pick_selection,
            args=(
                rec_id,
                widget_key,
            ),
        )


# ============================================================
# 11. Analysis panels (V3)
# ============================================================

def render_correct_score_cards(
    scores: List[Dict[str, Any]],
) -> None:
    if not scores:
        return

    columns = st.columns(
        min(len(scores), 4)
    )

    for index, score in enumerate(scores):
        if not isinstance(score, dict):
            continue

        score_text = clean_text(
            score.get("score")
        )

        probability = score.get(
            "probability",
            {},
        )

        if not isinstance(probability, dict):
            probability = {}

        with columns[
            index % len(columns)
        ]:
            render_html(
                f"""
                <div class="score-card">
                    <div class="score-value">
                        {escape(score_text) or "—"}
                    </div>

                    <div class="score-note">
                        保守概率
                        <strong>
                            {format_probability(
                                probability.get(
                                    "minimum"
                                ),
                                2,
                            )}
                        </strong>
                    </div>

                    <div class="score-note">
                        中位概率
                        <strong>
                            {format_probability(
                                probability.get(
                                    "median"
                                ),
                                2,
                            )}
                        </strong>
                    </div>

                    <div class="score-note">
                        公平賠率
                        <strong>
                            {format_odds(
                                score.get(
                                    "central_fair_odds"
                                ),
                                2,
                            )}
                        </strong>
                    </div>
                </div>
                """
            )


def render_movement_audit_panel(
    analysis: Dict[str, Any],
) -> None:
    audits = parse_json_field(
        analysis.get(
            "movement_audits_json"
        )
    )

    if not isinstance(audits, list) or not audits:
        st.info(
            "本場沒有可用的結構化走勢審計資料。"
        )

        return

    rows: List[Dict[str, Any]] = []

    for audit in audits:
        if not isinstance(audit, dict):
            continue

        primary = audit.get(
            "pinnacle_confirmation",
            {},
        )

        if not isinstance(primary, dict):
            primary = {}

        hkjc = audit.get(
            "hkjc_response",
            {},
        )

        if not isinstance(hkjc, dict):
            hkjc = {}

        change_pp = safe_float(
            audit.get(
                "market_implied_probability_change_pp"
            )
        )

        sign = (
            "+"
            if change_pp is not None
            and change_pp >= 0
            else ""
        )

        rows.append({
            "候選盤": (
                escape(clean_text(audit.get('label')))
                + "<br>"
                + "<small>"
                + escape(clean_text(audit.get('period'))) + " · "
                + escape(clean_upper(audit.get('market')))
                + "</small>"
            ),
            "走勢結果": (
                '<span class="{cls}">{label} · {strength}</span>'.format(
                    cls=movement_status_class(audit.get("verdict")),
                    label=movement_status_chinese(audit.get('verdict')),
                    strength=movement_status_chinese(audit.get('strength')),
                )
            ),
            "莊家一致": format_probability(
                audit.get(
                    "agreement_ratio"
                )
            ),
            "開盤概率": format_probability(
                audit.get(
                    "consensus_opening_probability"
                ),
                2,
            ),
            "最新概率": format_probability(
                audit.get(
                    "consensus_latest_probability"
                ),
                2,
            ),
            "概率變動": (
                f"{sign}{change_pp:.2f}pp"
                if change_pp is not None
                else "—"
            ),
            "Pinnacle": (
                movement_status_chinese(
                    primary.get("status")
                )
            ),
            "HKJC": (
                movement_status_chinese(
                    hkjc.get("status")
                )
            ),
            "行動提示": escape(
                clean_text(
                    audit.get("actionability")
                ).replace("_", " ")
            ),
        })

    if not rows:
        st.info("本場沒有可用的走勢審計資料。")
        return

    display = pd.DataFrame(rows)

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "候選盤": st.column_config.TextColumn(
                "候選盤",
                width="medium",
            ),
        },
    )


def render_family_out_panel(
    analysis: Dict[str, Any],
) -> None:
    family = parse_json_field(
        analysis.get(
            "family_out_json"
        )
    )

    if not isinstance(family, dict) or not family:
        st.info("本場沒有 family-out 穩健性資料。")
        return

    rows: List[Dict[str, Any]] = []

    for key, record in family.items():
        if not isinstance(record, dict):
            continue

        probability = record.get(
            "probability",
            {},
        )

        if not isinstance(probability, dict):
            probability = {}

        hit = probability.get(
            "hit",
            {},
        )

        if not isinstance(hit, dict):
            hit = {}

        rows.append({
            "候選盤": escape(
                clean_text(
                    record.get("label") or key
                )
            ),
            "結果": (
                '<span class="{cls}">{label}</span>'.format(
                    cls=movement_status_class(record.get("verdict")),
                    label=movement_status_chinese(record.get('verdict')),
                )
            ),
            "穩健性": (
                '<span class="{cls}">{label}</span>'.format(
                    cls=movement_status_class(record.get("status")),
                    label=robustness_status_chinese(record.get('status')),
                )
            ),
            "最低命中率": format_probability(
                hit.get("minimum"),
                2,
            ),
            "中位命中率": format_probability(
                hit.get("median"),
                2,
            ),
        })

    if not rows:
        st.info("本場沒有 family-out 資料。")
        return

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )


def render_stress_panel(
    analysis: Dict[str, Any],
) -> None:
    stress = parse_json_field(
        analysis.get(
            "stress_audits_json"
        )
    )

    if not isinstance(stress, dict) or not stress:
        st.info("本場沒有壓力測試資料。")
        return

    rows: List[Dict[str, Any]] = []

    for candidate_key, candidate_stress in stress.items():
        if not isinstance(
            candidate_stress,
            dict,
        ):
            continue

        label = candidate_stress.get(
            "label"
        ) or candidate_key

        for level_key, level_label in [
            ("light", "輕度"),
            ("medium", "中度"),
            ("heavy", "重度"),
        ]:
            record = candidate_stress.get(
                level_key,
                {},
            )

            if not isinstance(record, dict):
                continue

            rows.append({
                "候選盤": escape(
                    clean_text(label)
                ),
                "程度": level_label,
                "最低命中率": format_probability(
                    record.get(
                        "minimum_hit_probability"
                    )
                ),
                "中位命中率": format_probability(
                    record.get(
                        "median_hit_probability"
                    )
                ),
                "情境數": record.get(
                    "scenario_count"
                ),
            })

    if not rows:
        st.info("本場沒有壓力測試資料。")
        return

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )


def render_prior_panel(
    analysis: Dict[str, Any],
) -> None:
    prior = parse_json_field(
        analysis.get(
            "prior_comparison_json"
        )
    )

    if not isinstance(prior, dict) or not prior:
        st.info("本場沒有 prior 比較資料。")
        return

    priors = prior.get(
        "priors",
        {},
    )

    if not isinstance(priors, dict) or not priors:
        st.info("本場沒有 prior 比較資料。")
        return

    rows: List[Dict[str, Any]] = []

    for prior_name, prior_record in priors.items():
        if not isinstance(prior_record, dict):
            continue

        rows.append({
            "Prior": escape(
                clean_text(prior_name)
            ),
            "中位命中率": format_probability(
                prior_record.get(
                    "median_hit"
                )
            ),
            "最低命中率": format_probability(
                prior_record.get(
                    "minimum_hit"
                )
            ),
            "中位 EV": format_ev(
                prior_record.get(
                    "median_expected_return"
                )
            ),
            "備註": escape(
                clean_text(
                    prior_record.get("note")
                )
            ),
        })

    if not rows:
        st.info("本場沒有 prior 比較資料。")
        return

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )


def render_analysis_panels(
    analysis: Optional[Dict[str, Any]],
) -> None:
    if not analysis:
        return

    has_movement = parse_json_field(
        analysis.get(
            "movement_audits_json"
        )
    )

    has_family = parse_json_field(
        analysis.get(
            "family_out_json"
        )
    )

    has_stress = parse_json_field(
        analysis.get(
            "stress_audits_json"
        )
    )

    has_prior = parse_json_field(
        analysis.get(
            "prior_comparison_json"
        )
    )

    if not any([
        has_movement,
        has_family,
        has_stress,
        has_prior,
    ]):
        return

    engine_version = escape(
        clean_text(
            analysis.get("engine_version")
        )
    )

    runtime = safe_float(
        analysis.get("runtime_seconds")
    )

    quality = movement_status_chinese(
        analysis.get(
            "model_quality_status"
        )
    )

    coherence = movement_status_chinese(
        analysis.get(
            "ht_ft_coherence_status"
        )
    )

    metric_cols = st.columns(4)

    with metric_cols[0]:
        st.metric(
            "模型質量",
            quality,
        )

    with metric_cols[1]:
        st.metric(
            "HT-FT 一致性",
            coherence,
        )

    with metric_cols[2]:
        st.metric(
            "引擎版本",
            engine_version or "—",
        )

    with metric_cols[3]:
        st.metric(
            "運行時長",
            (
                f"{runtime:.1f}s"
                if runtime is not None
                else "—"
            ),
        )

    with st.expander(
        "📈 市場走勢審計（Odds Movement）",
        expanded=False,
    ):
        render_movement_audit_panel(
            analysis
        )

    with st.expander(
        "🛡️ Family-out 穩健性",
        expanded=False,
    ):
        render_family_out_panel(
            analysis
        )

    with st.expander(
        "🔥 壓力測試（Stress Audit）",
        expanded=False,
    ):
        render_stress_panel(
            analysis
        )

    with st.expander(
        "🎲 Prior 比較（Dixon-Coles / "
        "Independent Poisson / COM-Poisson）",
        expanded=False,
    ):
        render_prior_panel(
            analysis
        )


# ============================================================
# 12. Match renderer
# ============================================================

def match_title(
    match: Dict[str, Any],
    match_recommendations: pd.DataFrame,
) -> str:
    status = normalize_status(
        match.get("status")
    )

    name = clean_text(
        match.get("match_name")
    )

    if not name:
        home = clean_text(
            match.get("home_team")
        )

        away = clean_text(
            match.get("away_team")
        )

        if home and away:
            name = f"{home} vs {away}"
        else:
            name = clean_identifier(
                match.get("match_id")
            )

    return name


def render_match(
    match: Dict[str, Any],
    recommendations: pd.DataFrame,
    analysis: Optional[Dict[str, Any]] = None,
) -> None:
    match_id = clean_identifier(
        match.get("match_id")
    )

    match_recommendations = (
        recommendations[
            recommendations["match_id"]
            .map(clean_identifier)
            .eq(match_id)
        ].copy()
    )

    if match_recommendations.empty:
        return

    match_recommendations[
        "_tier_order"
    ] = (
        match_recommendations["tier"]
        .map(TIER_ORDER)
        .fillna(9)
    )

    match_recommendations[
        "_period_order"
    ] = (
        match_recommendations["period"]
        .map({
            "FT": 0,
            "HT": 1,
            "2H": 2,
        })
        .fillna(9)
    )

    match_recommendations = (
        match_recommendations.sort_values(
            by=[
                "_tier_order",
                "_period_order",
                "rank",
            ],
            ascending=True,
            na_position="last",
        )
    )

    title = match_title(
        match,
        match_recommendations,
    )

    status = normalize_status(
        match.get("status")
    )

    has_heavy = (
        match_recommendations[
            "is_heavy"
        ].map(safe_bool).any()
    )

    heading_classes = [
        "match-heading",
    ]

    if has_heavy:
        heading_classes.append(
            "match-heading-heavy"
        )

    if status == "ended":
        heading_classes.append(
            "match-heading-ended"
        )

    competition = escape(
        match.get("competition")
    )

    kickoff = escape(
        match.get("kickoff")
    )

    model_direction = escape(
        match.get("model_direction")
    )

    model_summary = escape(
        match.get("model_summary")
    )

    final_score = escape(
        match.get("final_score")
    )

    meta_parts = [
        item
        for item in [
            competition,
            kickoff,
        ]
        if item
    ]

    meta_html = " · ".join(
        meta_parts
    )

    direction_html = (
        f"""
        <div class="model-direction">
            <strong>Ultra V3 模型方向：</strong>
            {model_direction}
        </div>
        """
        if model_direction
        else ""
    )

    summary_html = (
        f"""
        <div class="model-summary">
            {model_summary}
        </div>
        """
        if model_summary
        else ""
    )

    final_html = (
        f"""
        <div class="score-summary">
            <strong>完場比分：</strong>
            {final_score}
        </div>
        """
        if final_score
        else ""
    )

    # ---- V3 correct-score fallback from analysis ----
    correct_scores = parse_json_field(
        analysis.get(
            "correct_scores_json"
        )
        if analysis is not None
        else None
    ) if analysis is not None else None

    cs_html = ""

    if correct_scores and isinstance(
        correct_scores,
        list,
    ) and correct_scores:
        cs_html = (
            '<div class="score-summary">'
            "<strong>🎯 波膽參考（V3 自動生成）：</strong>"
            "</div>"
        )

    # movement hint in heading
    movement_status = ""

    if analysis is not None:
        mv = clean_upper(
            analysis.get(
                "odds_movement_status"
            )
        )

        if mv:
            movement_status = (
                '<span class="period-pill {cls}">📈 {label}</span> '.format(
                    cls=movement_status_class(mv),
                    label=movement_status_chinese(mv),
                )
            )

    with st.expander(
        title,
        expanded=False,
    ):
        render_html(
            f"""
            <div class="{' '.join(heading_classes)}">
                <div class="match-name">
                    {movement_status}
                    {escape(match.get("match_name"))}
                </div>

                <div class="match-meta">
                    {meta_html}
                </div>

                {direction_html}
                {summary_html}
                {final_html}
                {cs_html}
            </div>
            """
        )

        # ---- Correct-score reference cards ----
        if correct_scores and isinstance(
            correct_scores,
            list,
        ) and correct_scores:
            st.markdown(
                "#### 🎯 FT 波膽參考"
            )

            st.caption(
                "波膽由 FT 模型自動生成，屬高風險參考；"
                "同一場的不同比分互相排斥。"
            )

            render_correct_score_cards(
                correct_scores
            )

        # ---- V3 analysis panels ----
        if analysis is not None:
            render_analysis_panels(
                analysis
            )

        official = match_recommendations[
            match_recommendations["tier"]
            .eq("OFFICIAL")
        ]

        alternatives = match_recommendations[
            match_recommendations["tier"]
            .eq("ALTERNATIVE")
        ]

        scores = match_recommendations[
            match_recommendations["tier"]
            .eq("CORRECT_SCORE")
        ]

        has_cs = (
            correct_scores is not None
            and isinstance(correct_scores, list)
            and bool(correct_scores)
        )

        tab_labels = [
            "✅ 官方推薦 ({n})".format(n=len(official)),
            "⚡ 進取選擇 ({n})".format(n=len(alternatives)),
        ]

        if not scores.empty or has_cs:
            tab_labels.append(
                "🎯 波膽 ({n})".format(
                    n=len(scores) + (1 if has_cs else 0)
                )
            )

        official_tab, alternative_tab, *rest = (
            st.tabs(tab_labels)
        )

        score_tab = rest[0] if rest else None

        with official_tab:
            if official.empty:
                st.info("本場未有官方推薦。")
            else:
                for _, row in official.iterrows():
                    render_recommendation(
                        row.to_dict()
                    )

        with alternative_tab:
            if alternatives.empty:
                st.info(
                    "本場未有額外進取選擇。"
                )
            else:
                st.caption(
                    "進取選擇不等同官方推薦。"
                    "會員可按個人賠率、市場及風險偏好選擇。"
                )

                for _, row in alternatives.iterrows():
                    render_recommendation(
                        row.to_dict()
                    )

        if score_tab is not None:
            with score_tab:
                if not scores.empty:
                    st.warning(
                        "以下為手動上架的波膽推薦。"
                    )

                    for _, row in scores.iterrows():
                        render_recommendation(
                            row.to_dict()
                        )

                if has_cs:
                    st.markdown(
                        "**模型自動生成波膽參考**"
                    )

                    render_correct_score_cards(
                        correct_scores
                    )


# ============================================================
# 13. Filtering
# ============================================================

def filter_recommendations(
    recommendations: pd.DataFrame,
    *,
    tiers: List[str],
    periods: List[str],
    markets: List[str],
    available_periods: List[str],
    available_markets: List[str],
    minimum_odds: float,
    maximum_odds: float,
) -> pd.DataFrame:
    if recommendations.empty:
        return recommendations

    output = recommendations.copy()

    if not tiers:
        return output.iloc[0:0]

    output = output[
        output["tier"].isin(tiers)
    ]

    if available_periods:
        if not periods:
            return output.iloc[0:0]

        output = output[
            output["period"].isin(periods)
        ]

    if available_markets:
        if not markets:
            return output.iloc[0:0]

        output = output[
            output["market"].isin(markets)
        ]

    lower = min(
        minimum_odds,
        maximum_odds,
    )

    upper = max(
        minimum_odds,
        maximum_odds,
    )

    score_mask = (
        output["tier"]
        .eq("CORRECT_SCORE")
    )

    odds_mask = (
        output["odds"].isna()
        | (
            output["odds"].ge(lower)
            & output["odds"].le(upper)
        )
    )

    return output[
        score_mask | odds_mask
    ]


def matching_match_ids(
    recommendations: pd.DataFrame,
) -> Set[str]:
    if recommendations.empty:
        return set()

    return {
        clean_identifier(value)
        for value in recommendations[
            "match_id"
        ]
        if clean_identifier(value)
    }


# ============================================================
# 14. Session setup
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "portal_user" not in st.session_state:
    st.session_state.portal_user = {}

if "my_pick_ids" not in st.session_state:
    st.session_state.my_pick_ids = []


users_df, raw_matches_df, raw_recommendations_df = (
    load_portal_data()
)

parlay_corner_df = fetch_sheet("parlay_corner")

raw_analysis_df = fetch_sheet("analysis")


# ============================================================
# 15. Hero
# ============================================================

render_html(
    """
    <div class="portal-hero">
        <div class="portal-eyebrow">
            <span class="live-dot"></span>
            Aegis Ultra V3 · VIP Access
        </div>

        <h1 class="portal-title">
    <span class="portal-trophy">🏆</span>
    雨姐 VIP Match Centre
        </h1>

        <p class="portal-subtitle">
            Ultra V3 賽事分析平台，集中顯示官方推薦、
            進取選擇、半場及全場市場、波膽參考，
            並檢查重疊、走廊及直接衝突風險。
            全新升級：市場走勢審計（Odds Movement）、
            Family-out 穩健性、壓力測試及 Prior 比較。
        </p>

        <div class="hero-feature-row">
            <span class="hero-feature">⚽ FT 全場</span>
            <span class="hero-feature">⏱️ HT 半場</span>
            <span class="hero-feature">🛡️ 衝突檢查</span>
            <span class="hero-feature">📊 模型概率</span>
            <span class="hero-feature">📈 走勢審計</span>
            <span class="hero-feature">🛡️ 穩健性</span>
            <span class="hero-feature">🎯 波膽參考</span>
        </div>
    </div>
    """
)


# ============================================================
# 16. Login
# ============================================================

if not st.session_state.logged_in:
    render_html(
        """
        <div class="login-shell">
            <div class="login-icon">
                🔐
            </div>

            <div class="login-title">
                VIP 會員登入
            </div>

            <div class="login-copy">
                登入後查看最新 Aegis Ultra V3
                賽事分析、官方推薦、進取選擇、
                半場市場、市場走勢審計、穩健性測試
                及會員專屬波膽參考。
            </div>

            <div class="login-security">
                🛡️ Secure Member Access · Ultra V3
            </div>
        </div>
        """
    )

    with st.form(
        "client_login_form",
        clear_on_submit=False,
    ):
        username = st.text_input(
            "用戶名 Username",
            placeholder="輸入會員帳號",
        )

        password = st.text_input(
            "密碼 Password",
            type="password",
            placeholder="輸入會員密碼",
        )

        login_clicked = (
            st.form_submit_button(
                "驗證並進入 VIP Match Centre",
                type="primary",
                use_container_width=True,
            )
        )

    if login_clicked:
        valid, authenticated_user, message = (
            authenticate(
                users_df,
                username,
                password,
            )
        )

        if (
            valid
            and authenticated_user is not None
        ):
            status_box = st.empty()

            status_box.info(
                "🛡️ 正在驗證會員身份..."
            )
            time.sleep(0.18)

            status_box.warning(
                "⚙️ 正在連接 Aegis Ultra V3..."
            )
            time.sleep(0.18)

            status_box.success(
                "✅ 驗證成功。"
            )
            time.sleep(0.14)

            status_box.empty()

            st.session_state.logged_in = True
            st.session_state.portal_user = (
                authenticated_user
            )

            st.rerun()

        else:
            st.error(message)

    st.stop()


# ============================================================
# 17. Validate existing session
# ============================================================

member_valid, member_message = (
    validate_logged_in_member(
        users_df,
        st.session_state.portal_user,
    )
)

if not member_valid:
    st.session_state.logged_in = False
    st.session_state.portal_user = {}
    clear_all_picks()

    st.error(member_message)
    st.info("請重新登入或聯絡雨姐。")
    st.stop()


# ============================================================
# 18. Prepare logged-in data
# ============================================================

recommendations_df = prepare_recommendations(
    raw_recommendations_df
)

matches_df = prepare_matches(
    raw_matches_df,
    recommendations_df,
)

analysis_df = prepare_analysis(
    raw_analysis_df
)

matches_df, recommendations_df = (
    visible_records(
        matches_df,
        recommendations_df,
    )
)

user = st.session_state.portal_user


def get_analysis_for(
    match_id: str,
) -> Optional[Dict[str, Any]]:
    return analysis_for_match(
        analysis_df,
        match_id,
    )


# ============================================================
# 19. Sidebar
# ============================================================

with st.sidebar:
    st.markdown("## 🏆 VIP Control Centre")

    st.success(
        f"會員：{user.get('username', '')}\n\n"
        f"到期日：{user.get('expiry_date', '')}"
    )

    st.caption(
        f"Aegis Ultra V3 · Portal {APP_VERSION}"
    )

    st.markdown("---")

    navigation = st.radio(
        "頁面",
        [
            "⚽ Match Centre",
            "📌 過關專區",
            "🧺 我的選擇",
            "📜 完場紀錄",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### 🎛️ 顯示設定")

    tier_options = [
        "OFFICIAL",
        "ALTERNATIVE",
        "CORRECT_SCORE",
    ]

    selected_tiers = st.multiselect(
        "推薦類別",
        options=tier_options,
        default=tier_options,
        format_func=lambda value: {
            "OFFICIAL": "✅ 官方推薦",
            "ALTERNATIVE": "⚡ 進取選擇",
            "CORRECT_SCORE": "🎯 波膽",
        }.get(value, value),
    )

    period_options = sorted(
        {
            normalize_period(value)
            for value in recommendations_df[
                "period"
            ]
            if clean_text(value)
        },
        key=lambda value: {
            "FT": 0,
            "HT": 1,
            "2H": 2,
        }.get(value, 9),
    )

    selected_periods = st.multiselect(
        "結算時段",
        options=period_options,
        default=period_options,
        format_func=lambda value: {
            "FT": "⚽ FT 全場",
            "HT": "⏱️ HT 半場",
            "2H": "⏱️ 2H 下半場",
        }.get(value, value),
    )

    market_options = sorted({
        normalize_market(value)
        for value in recommendations_df[
            "market"
        ]
        if clean_text(value)
    })

    selected_markets = st.multiselect(
        "市場",
        options=market_options,
        default=market_options,
    )

    minimum_odds = st.number_input(
        "最低賠率",
        min_value=1.01,
        max_value=100.0,
        value=1.01,
        step=0.05,
        format="%.2f",
    )

    maximum_odds = st.number_input(
        "最高賠率",
        min_value=1.01,
        max_value=100.0,
        value=20.0,
        step=0.10,
        format="%.2f",
    )

    if minimum_odds > maximum_odds:
        st.warning(
            "最低賠率高於最高賠率；"
            "系統會自動交換兩者。"
        )

    competition_options = sorted({
        clean_text(value)
        for value in matches_df[
            "competition"
        ]
        if clean_text(value)
    })

    selected_competitions = st.multiselect(
        "賽事",
        options=competition_options,
        default=competition_options,
    )

    show_movement_only = st.checkbox(
        "只顯示有走勢數據的場次",
        value=False,
        help=(
            "勾選後只列出已完成市場走勢審計的場次"
        ),
    )

    st.markdown("---")

    if st.button(
        "🔄 更新最新內容",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.rerun()

    if st.button(
        "🚪 登出系統",
        use_container_width=True,
    ):
        st.session_state.logged_in = False
        st.session_state.portal_user = {}
        clear_all_picks()
        st.rerun()


# ============================================================
# 20. Welcome card
# ============================================================

render_html(
    f"""
    <div class="welcome-card">
        <div class="welcome-name">
            👋 歡迎回來，
            <span>{escape(user.get("username"))}</span>
        </div>

        <div class="welcome-copy">
            Ultra V3 已啟用全場及半場時段識別，
            並新增市場走勢審計、Family-out 穩健性、
            壓力測試與 Prior 比較。每場賽事詳情內
            可展開查看走勢與模型敏感度分析。
        </div>
    </div>
    """
)


if (
    raw_recommendations_df.empty
    and raw_matches_df.empty
):
    st.warning(
        "目前無法讀取 matches 及 recommendations "
        "工作表，或兩個工作表尚未有資料。"
    )


# ============================================================
# 21. Apply filters
# ============================================================

filtered_recommendations = (
    filter_recommendations(
        recommendations_df,
        tiers=selected_tiers,
        periods=selected_periods,
        markets=selected_markets,
        available_periods=period_options,
        available_markets=market_options,
        minimum_odds=minimum_odds,
        maximum_odds=maximum_odds,
    )
)

if competition_options:
    if selected_competitions:
        filtered_matches = matches_df[
            matches_df["competition"].isin(
                selected_competitions
            )
        ].copy()

    else:
        filtered_matches = (
            matches_df.iloc[0:0].copy()
        )

else:
    filtered_matches = matches_df.copy()

allowed_match_ids = matching_match_ids(
    filtered_recommendations
)

filtered_matches = filtered_matches[
    filtered_matches["match_id"]
    .map(clean_identifier)
    .isin(allowed_match_ids)
].copy()

if (
    show_movement_only
    and not analysis_df.empty
):
    matches_with_movement = {
        clean_identifier(value)
        for value in analysis_df[
            "match_id"
        ]
        if clean_identifier(value)
        and parse_json_field(
            analysis_df[
                analysis_df["match_id"]
                .map(clean_identifier)
                .eq(
                    clean_identifier(value)
                )
            ]["movement_audits_json"]
            .iloc[0]
            if (
                clean_identifier(value)
                and not analysis_df[
                    analysis_df["match_id"]
                    .map(clean_identifier)
                    .eq(
                        clean_identifier(value)
                    )
                ].empty
            )
            else ""
        )
    }

    filtered_matches = filtered_matches[
        filtered_matches["match_id"]
        .map(clean_identifier)
        .isin(matches_with_movement)
    ].copy()


# ============================================================
# 22. Match Centre
# ============================================================

if navigation == "⚽ Match Centre":
    active_matches = filtered_matches[
        filtered_matches["status"]
        .eq("published")
    ].copy()

    active_ids = {
        clean_identifier(value)
        for value in active_matches[
            "match_id"
        ]
        if clean_identifier(value)
    }

    active_recommendations = (
        filtered_recommendations[
            filtered_recommendations[
                "match_id"
            ]
            .map(clean_identifier)
            .isin(active_ids)
        ].copy()
    )

    official_count = int(
        active_recommendations[
            "tier"
        ].eq("OFFICIAL").sum()
    )

    alternative_count = int(
        active_recommendations[
            "tier"
        ].eq("ALTERNATIVE").sum()
    )

    heavy_count = int(
        active_recommendations[
            "is_heavy"
        ].map(safe_bool).sum()
    )

    movement_count = int(
        active_recommendations[
            "movement_verdict"
            .map(clean_upper)
            .ne("")
        ].sum()
    )

    first, second, third, fourth, fifth = (
        st.columns(5)
    )

    first.metric(
        "公開賽事",
        len(active_matches),
    )

    second.metric(
        "官方推薦",
        official_count,
    )

    third.metric(
        "進取選擇",
        alternative_count,
    )

    fourth.metric(
        "🔥 重心",
        heavy_count,
    )

    fifth.metric(
        "📈 有走勢",
        movement_count,
    )

    render_html(
        """
        <div class="section-kicker">
            Ultra V3 Live Match Catalogue
        </div>
        """
    )

    st.header("⚽ Match Centre")

    if active_matches.empty:
        render_html(
            """
            <div class="empty-state">
                ☘️ 暫時未有符合目前篩選條件的公開賽事。
                <br>
                您可以調整時段、賠率、市場或推薦類別。
            </div>
            """
        )

    else:
        active_matches[
            "_kickoff_sort"
        ] = active_matches[
            "kickoff"
        ].map(parse_datetime_value)

        active_matches = (
            active_matches.sort_values(
                "_kickoff_sort",
                na_position="last",
            )
        )

        for _, match_row in (
            active_matches.iterrows()
        ):
            render_match(
                match_row.to_dict(),
                active_recommendations,
                get_analysis_for(
                    clean_identifier(
                        match_row.get(
                            "match_id"
                        )
                    )
                ),
            )


# ============================================================
# 23. Manual Parlay Corner
# ============================================================

elif navigation == "📌 過關專區":
    render_html(
        """
        <div class="parlay-hero">
            <div class="parlay-eyebrow">
                ✦ Manual VIP Bulletin
            </div>

            <div class="parlay-hero-title">
                📌 雨姐過關專區
            </div>

            <div class="parlay-hero-copy">
                集中查看最新人手過關推介、文字訊息及圖片。
                本區內容以簡單公告形式顯示，不會進行
                自動計算、盤口分析或結果結算。
            </div>

            <div class="parlay-disclaimer">
                ℹ️ 人手分享內容 · 並非 Ultra V3 模型官方推薦
            </div>
        </div>
        """
    )

    refresh_column, count_column = st.columns(
        [1, 2]
    )

    with refresh_column:
        if st.button(
            "🔄 更新過關專區",
            key="refresh_parlay_corner",
            use_container_width=True,
        ):
            st.cache_data.clear()
            st.rerun()

    parlay_posts = prepare_parlay_posts(
        parlay_corner_df
    )

    with count_column:
        if not parlay_posts.empty:
            st.info(
                "目前顯示最新 {n} 則人手推介。".format(
                    n=min(len(parlay_posts), 30)
                )
            )

    if parlay_posts.empty:
        render_html(
            """
            <div class="empty-state">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">
                    📭
                </div>

                暫時未有過關推介。
                <br>
                新的 Google Form 提交內容將會顯示在這裡。
            </div>
            """
        )

    else:
        parlay_posts = parlay_posts.head(30)

        for post_number, (_, post) in enumerate(
            parlay_posts.iterrows(),
            start=1,
        ):
            title = clean_text(
                post.get("title")
            ) or "最新過關推介"

            recommendation = clean_text(
                post.get("recommendation")
            )

            photo_link = clean_text(
                post.get("photo")
            )

            timestamp = clean_text(
                post.get("timestamp")
            )

            submitted_by = clean_text(
                post.get("submitted_by")
            )

            recommendation_html = ""

            if recommendation:
                safe_recommendation = escape(
                    recommendation
                ).replace(
                    "\n",
                    "<br>",
                )

                recommendation_html = (
                    '<div class="parlay-post-content">'
                    f"{safe_recommendation}"
                    "</div>"
                )

            metadata: List[str] = []

            if timestamp:
                metadata.append(
                    "🕒 {t}".format(t=escape(timestamp))
                )

            if submitted_by:
                metadata.append(
                    "👤 {t}".format(t=escape(submitted_by))
                )

            metadata_html = ""

            if metadata:
                metadata_html = (
                    '<div class="parlay-post-meta">'
                    + "".join(
                        f"<span>{item}</span>"
                        for item in metadata
                    )
                    + "</div>"
                )

            render_html(
                f"""
                <div class="parlay-post">
                    <div class="parlay-post-number">
                        VIP Post · {post_number:02d}
                    </div>

                    <div class="parlay-post-title">
                        📌 {escape(title)}
                    </div>

                    {recommendation_html}
                    {metadata_html}
                </div>
                """
            )

            if photo_link:
                image_url = google_drive_image_url(
                    photo_link
                )

                render_html(
                    """
                    <div class="parlay-photo-label">
                        🖼️ 推介圖片
                    </div>
                    """
                )

                if image_url:
                    try:
                        st.image(
                            image_url,
                            caption=title,
                            use_container_width=True,
                        )

                    except Exception:
                        st.warning(
                            "圖片暫時無法顯示。"
                            "請確認 Google Drive 圖片已設定為"
                            "「知道連結的任何人都可查看」。"
                        )

                else:
                    st.warning(
                        "未能識別此圖片的 Google Drive 連結。"
                    )

                    st.link_button(
                        "在 Google Drive 查看圖片",
                        photo_link,
                        use_container_width=True,
                    )

            if post_number < len(parlay_posts):
                render_html(
                    '<div class="parlay-divider"></div>'
                )


# ============================================================
# 24. My Picks
# ============================================================

elif navigation == "🧺 我的選擇":
    render_html(
        """
        <div class="section-kicker">
            Personal Selection Desk
        </div>
        """
    )

    st.header("🧺 我的選擇")

    st.caption(
        "此頁只整理您的個人選擇。"
        "個人選擇不會自動變成官方推薦，"
        "亦不代表互相獨立。"
    )

    current_ids = selected_ids()

    selected_rows_df = recommendations_df[
        recommendations_df["rec_id"]
        .map(clean_identifier)
        .isin(current_ids)
    ].copy()

    if selected_rows_df.empty:
        render_html(
            """
            <div class="empty-state">
                尚未加入任何選擇。
                <br>
                前往 Match Centre，
                在心儀盤口下方勾選
                「加入我的選擇」。
            </div>
            """
        )

    else:
        valid_odds = [
            value
            for value in (
                safe_float(item)
                for item in selected_rows_df[
                    "odds"
                ]
            )
            if value is not None
        ]

        official_selected = int(
            selected_rows_df[
                "tier"
            ].eq("OFFICIAL").sum()
        )

        represented_matches = (
            selected_rows_df[
                "match_id"
            ]
            .map(clean_identifier)
            .nunique()
        )

        first, second, third, fourth = (
            st.columns(4)
        )

        first.metric(
            "已選項目",
            len(selected_rows_df),
        )

        second.metric(
            "涉及賽事",
            represented_matches,
        )

        third.metric(
            "官方推薦",
            official_selected,
        )

        fourth.metric(
            "平均賠率",
            (
"{v:.2f}".format(v=sum(valid_odds) / len(valid_odds))
                if valid_odds
                else "—"
            ),
        )

        warnings = selection_warnings(
            selected_rows_df.to_dict(
                orient="records"
            )
        )

        if not warnings:
            st.success(
                "✅ 目前未發現明顯直接衝突。"
            )

        for warning in warnings:
            class_name = {
                "danger": (
                    "pick-warning pick-danger"
                ),
                "warning": (
                    "pick-warning"
                ),
                "info": (
                    "pick-warning pick-info"
                ),
            }.get(
                warning["severity"],
                "pick-warning",
            )

            render_html(
                f"""
                <div class="{class_name}">
                    <strong>
                        {escape(warning["title"])}
                    </strong>
                    <br>
                    {escape(warning["message"])}
                </div>
                """
            )

        st.subheader("您的選擇")

        selected_rows_df[
            "_tier_order"
        ] = (
            selected_rows_df["tier"]
            .map(TIER_ORDER)
            .fillna(9)
        )

        selected_rows_df = (
            selected_rows_df.sort_values(
                [
                    "match_id",
                    "_tier_order",
                    "period",
                    "rank",
                ],
                na_position="last",
            )
        )

        for _, row in (
            selected_rows_df.iterrows()
        ):
            row_dict = row.to_dict()

            match_id = clean_identifier(
                row_dict.get("match_id")
            )

            matching_match = matches_df[
                matches_df["match_id"]
                .map(clean_identifier)
                .eq(match_id)
            ]

            if not matching_match.empty:
                match_name = clean_text(
                    matching_match.iloc[0].get(
                        "match_name"
                    )
                )

                if match_name:
                    st.caption(
                        f"⚽ {match_name}"
                    )

            render_recommendation(
                row_dict,
                allow_selection=False,
            )

            rec_id = recommendation_identity(
                row_dict
            )

            if st.button(
                "移除此選擇",
                key=f"remove_pick_{rec_id}",
                use_container_width=True,
            ):
                remove_pick(rec_id)
                st.rerun()

        export_columns = [
            column
            for column in [
                "rec_id",
                "match_id",
                "tier",
                "period",
                "market",
                "market_scope",
                "selection",
                "line",
                "rec_title",
                "odds",
                "conservative_hit",
                "median_hit",
                "fair_odds",
                "is_heavy",
                "movement_verdict",
                "movement_probability_change_pp",
                "family_out_status",
            ]
            if column in selected_rows_df.columns
        ]

        export_csv = (
            selected_rows_df[
                export_columns
            ]
            .to_csv(index=False)
            .encode("utf-8-sig")
        )

        download_column, clear_column = (
            st.columns(2)
        )

        with download_column:
            st.download_button(
                "📥 下載我的選擇 CSV",
                data=export_csv,
                file_name="aegis_ultra_v3_my_picks.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with clear_column:
            if st.button(
                "🗑️ 清除全部選擇",
                use_container_width=True,
            ):
                clear_all_picks()
                st.rerun()


# ============================================================
# 25. Completed archive
# ============================================================

else:
    ended_matches = filtered_matches[
        filtered_matches["status"]
        .eq("ended")
    ].copy()

    ended_ids = {
        clean_identifier(value)
        for value in ended_matches[
            "match_id"
        ]
        if clean_identifier(value)
    }

    ended_recommendations = (
        filtered_recommendations[
            filtered_recommendations[
                "match_id"
            ]
            .map(clean_identifier)
            .isin(ended_ids)
        ].copy()
    )

    official_ended = (
        ended_recommendations[
            ended_recommendations["tier"]
            .eq("OFFICIAL")
        ]
    )

    settled_values = {
        "hit",
        "win",
        "half_win",
        "push",
        "half_loss",
        "miss",
        "loss",
    }

    settled = official_ended[
        official_ended["result"].isin(
            settled_values
        )
    ]

    positive_values = {
        "hit",
        "win",
        "half_win",
    }

    positive_results = int(
        settled["result"]
        .isin(positive_values)
        .sum()
    )

    settled_count = len(settled)

    positive_rate = (
        positive_results / settled_count
        if settled_count
        else None
    )

    first, second, third = st.columns(3)

    first.metric(
        "已完場賽事",
        len(ended_matches),
    )

    second.metric(
        "已結算官方推薦",
        settled_count,
    )

    third.metric(
        "官方推薦命中率",
        (
            format_probability(
                positive_rate
            )
            if positive_rate is not None
            else "—"
        ),
    )

    render_html(
        """
        <div class="section-kicker">
            Completed Match Archive
        </div>
        """
    )

    st.header("📜 完場紀錄")

    st.caption(
        "名義正面結果率把全中、全贏及半贏列為"
        "正面結果，並非實際投注回報率。"
    )

    if ended_matches.empty:
        render_html(
            """
            <div class="empty-state">
                暫時未有符合目前篩選條件的完場紀錄。
            </div>
            """
        )

    else:
        ended_matches[
            "_kickoff_sort"
        ] = ended_matches[
            "kickoff"
        ].map(parse_datetime_value)

        ended_matches = (
            ended_matches.sort_values(
                "_kickoff_sort",
                ascending=False,
                na_position="last",
            )
        )

        for _, match_row in (
            ended_matches.iterrows()
        ):
            render_match(
                match_row.to_dict(),
                ended_recommendations,
                get_analysis_for(
                    clean_identifier(
                        match_row.get(
                            "match_id"
                        )
                    )
                ),
            )


# ============================================================
# 26. Footer
# ============================================================

st.markdown(
    "<br><br>",
    unsafe_allow_html=True,
)

st.divider()

st.caption(
    f"🛡️ Powered by Aegis Ultra V3 · "
    f"Match Centre {APP_VERSION}"
)

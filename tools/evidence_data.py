"""Build the evidence page's data from the research sweep spreadsheet.

Usage: python3 tools/evidence_data.py path/to/societal_impact_ai_research_evidence.csv

Splits the sheet into two sets:
  research - rows tagged with one of the four threat models (scored 2 or higher)
  demand   - the "Cross-cutting / demand signal" rows plus programme/hub rows, and the
             hand-curated community calls in tools/evidence_community.csv:
             evidence that labs, governments, universities and researchers are asking for this work

Writes evidence/data.js (read by the page) and a public CSV of the research set. The sheet's Notes column
and impact scores are internal and are never written out; the score only sets the order.
"""

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "evidence"

TM = {
    "1. Human-AI interaction harms": 1,
    "2. Misuse - persuasion and manipulation": 2,
    "3. Structural risk - economic/labor": 3,
    "4. Structural risk - institutional/organizational": 4,
}
TM_NAMES = {
    1: "Human-AI interaction",
    2: "Persuasion and manipulation",
    3: "Economic and labor",
    4: "Institutional and organizational",
}

# Score-1 rows outside the cross-cutting group that are programmes, not findings.
DEMAND_EXTRA = {"Economic Futures (program)"}

# Rows that repeat another row's study; the other copy is kept.
DUPLICATES = {
    ("Stanford University (academia) - Digital Economy Lab (Stanford HAI)",
     "GPTs are GPTs: An Early Look at the Labor Market Impact Potential of Large Language Models"),
    ("University of Virginia (academia) - Economics of Transformative AI (EconTAI) Initiative",
     "Concentrating Intelligence: Scaling and Market Structure in Artificial Intelligence"),
    ("OpenAI (lab) - Economic Research team", "How people are using ChatGPT"),  # blog summary of the NBER paper
}

# Demand rows that are research methods, datasets or measurement infrastructure.
METHODS = {
    "Clio: A system for privacy-preserving insights into real-world AI use",
    "Coding agents in the social sciences",
    "Enabling independent research on how people use Claude",
    "Predictability and Surprise in Large Generative Models",
    "Red teaming language models to reduce harms: methods, scaling behaviors, and lessons learned",
    "Results from the first Anthropic Public Record",
    "Atlas of Human-AI Interaction (v1): An Interactive Meta-Science Platform for Large-Scale Research Literature Sensemaking",
    "GPT as a measurement tool",
    "How ChatGPT adoption broadened in early 2026",
    "How ChatGPT adoption has expanded",
    "OpenAI Signals",
    "AI Economic Indicators: June 2026 Update",
    "In Silico Sociology: Forecasting COVID-19 Polarization with Large Language Models",
    "LLM Social Simulations Are a Promising Research Method",
    "Semantic Structure in Large Language Model Embeddings",
    "Semantic Structure of Feature Space in Large Language Models",
    "Simulating Subjects: The Promise and Peril of Artificial Intelligence Stand-Ins for Social Agents and Interactions",
}

TEAM_SOURCES = {"Lab team", "Lab institute", "Academic department", "Lab research initiative", "Lab program"}


def demand_kind(row):
    title, source = row["Title"], row["Source Type"]
    if "hiring" in source.lower():
        return "Hiring"
    if "conference" in source.lower():
        return "Convenings"
    if re.search(r"grant|fund", source + " " + title, re.I) or title.startswith("Announcing the Alignment Project"):
        return "Funding"
    if source in TEAM_SOURCES or title.startswith("Introducing") or "cohort" in title.lower():
        return "Teams and institutes"
    if title in METHODS:
        return "Methods and data"
    return "Agendas and calls"


def sector(org):
    if "(lab)" in org:
        return "AI labs"
    if org.startswith("UK Government"):
        return "Government"
    if re.search(r"academ|universit", org, re.I):
        return "Universities"
    return "Other"


def clean_org(org):
    org = re.sub(r" \((lab|academia|academic|think tank|safety institute|professional body)\)", "", org)
    return org.replace(" - ", " · ")


def year_of(s):
    """First four-digit year in the field, so a range like 2024-2026 counts once, at its start."""
    m = re.search(r"(20\d\d)", s)
    return int(m.group(1)) if m else None


def year_label(s):
    years = re.findall(r"20\d\d", s)
    if not years:
        return s
    return years[0] if len(set(years)) == 1 else f"{years[0]}–{years[-1]}"


def main(src):
    rows = list(csv.DictReader(open(src, newline="", encoding="utf-8")))
    # Studies added after the sweep (verified by hand), in the sheet's columns.
    rows += list(csv.DictReader(open(ROOT / "tools" / "evidence_additions.csv", newline="", encoding="utf-8")))
    research, demand = [], []
    for r in rows:
        if (r["Organization"], r["Title"]) in DUPLICATES:
            continue
        score = int(r["Societal Impact Score (1-5)"])
        base = {
            "t": r["Title"].strip(),
            "a": r["Author/Team"].strip(),
            "o": clean_org(r["Organization"].strip()),
            "y": year_label(r["Year"]),
            "yn": year_of(r["Year"]),
            "u": r["Link"].strip(),
            "s": r["Source Type"].strip(),
            "k": score,
        }
        tm = TM.get(r["Fellowship Threat Model"])
        if tm and r["Title"] not in DEMAND_EXTRA:
            if score < 2:
                continue  # press releases and short articles without findings
            base.update({
                "m": tm,
                "d": r["Primary Discipline"].strip(),
                "d2": r["Secondary Discipline"].strip(),
                "g": r["Evidence Tier"].startswith("Gold"),
            })
            research.append(base)
        else:
            kind = demand_kind(r)
            if kind == "Hiring":
                continue  # job posts expire and their links break; the page states the hiring trend in prose
            base.update({"c": kind, "x": sector(r["Organization"])})
            demand.append(base)

    # Calls from the AI safety community for social science, curated by hand (see tools/evidence_community.csv).
    for r in csv.DictReader(open(ROOT / "tools" / "evidence_community.csv", newline="", encoding="utf-8")):
        demand.append({
            "t": r["Title"], "a": r["Author/Team"], "o": clean_org(r["Organization"]), "y": r["Year"],
            "yn": int(r["Year"]), "u": r["Link"], "s": r["Source Type"], "k": 3,
            "c": "Community calls", "x": "Research community",
        })

    for group in (research, demand):
        group.sort(key=lambda x: (-x["k"], -(x["yn"] or 0), x["t"]))

    OUT.mkdir(exist_ok=True)
    data = {"tm": TM_NAMES, "research": research, "demand": demand}
    for group in (research, demand):
        for x in group:
            del x["k"]  # order is kept; the score itself stays internal
    (OUT / "data.js").write_text(
        "// Generated by tools/evidence_data.py from the SIRA research sweep. Do not edit by hand.\n"
        "window.SIRA_EVIDENCE = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )

    with open(OUT / "sira-evidence-research.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Title", "Authors / team", "Organization", "Year", "Threat model",
                    "Primary discipline", "Secondary discipline", "Source type", "Large-N or RCT", "Link"])
        for x in research:
            w.writerow([x["t"], x["a"], x["o"], x["y"], TM_NAMES[x["m"]], x["d"], x["d2"], x["s"],
                        "Yes" if x["g"] else "", x["u"]])

    # Summary for writing the page copy.
    from collections import Counter
    print("research", len(research), "demand", len(demand))
    print("gold", sum(x["g"] for x in research), "orgs", len({x["o"].split(" · ")[0] for x in research}))
    print("by tm", sorted(Counter(x["m"] for x in research).items()))
    print("by year", sorted(Counter(x["yn"] for x in research).items(), key=lambda t: t[0] or 0))
    print("by disc", Counter(x["d"] for x in research).most_common())
    print("demand kinds", Counter(x["c"] for x in demand).most_common())
    print("demand sectors", Counter(x["x"] for x in demand).most_common())
    print("demand orgs", len({x["o"].split(" · ")[0] for x in demand}))
    for x in demand:
        if x["c"] in ("Hiring", "Funding", "Teams and institutes", "Convenings"):
            print(" ", x["c"], "|", x["o"], "|", x["t"][:70])


if __name__ == "__main__":
    main(sys.argv[1])

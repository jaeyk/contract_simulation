"""Code contract clauses from the source PDFs into contract_terms.csv.

Requires Poppler's `pdftotext`. Text is cached under simulation/.cache/contract_text.
Each indicator records the number of matching documents and the first matching
snippet so every code can be audited. Manual corrections belong in
term_overrides.csv, which calibrate.py applies after this automated pass.
"""
import csv
from pathlib import Path
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data"
CACHE = HERE.parent / ".cache" / "contract_text"

# Patterns are case-insensitive and applied to whitespace-normalized text.
RULES = {
    "liquidated_damages": r"liquidated damages",
    "sla_fee_reduction": r"service level (agreement )?(service )?credits?|sla credits?|fee reductions?|at[- ]risk (fee|amount)|performance credits?",
    "defect_warranty": r"warrant(y|s|ies)? (that )?(the )?(system|software|solution|deliverables?|services?|products?)[^.]{0,120}(defect|conform|perform|free from|error)|warranty period|warranty services",
    "transition_assistance": r"transition(-| )(assistance|services|plan|out)|turnover plan|disentangle|knowledge transfer",
    "data_ownership": r"(data|work product|deliverables?|materials)[^.]{0,80}(property of|owned by|ownership)[^.]{0,40}(state|agency|department|district|commonwealth|purchasing entity|customer)|(state|agency) shall own",
    "source_code_escrow": r"source code escrow|escrow (agent|agreement|package)",
    "unit_pricing": r"per (profile|transaction|search|record|claim|case|lookup|query|check|seat)\b|/ ?(profile|transaction|search|claim)\b",
    "outcome_payment": r"shared savings|percentage of (the )?(savings|recover)|contingency fee (basis|arrangement)|(paid|payment|compensat)[^.]{0,60}(per|for each) (verified|successful|confirmed) (recover|outcome|case)",
    "independent_testing": r"independent verification and validation|iv&v",
    "change_notification": r"(notify|notice|notification)[^.]{0,100}(change|modification|update|substitution)s? (to|in|of) (the )?(software|model|algorithm|data source|subcontractor|system|service)",
    "audit_rights": r"right to audit|audit (rights|the (books|records))|access to [^.]{0,30}records",
    "accuracy_standard": r"false positives?|accuracy (rate|standard|requirement)|(maximum|acceptable|target) error rate",
    "local_acceptance_testing": r"user acceptance test|acceptance testing|product acceptance testing|operational readiness test",
}

# A match is skipped when the surrounding 150 characters match its exclusion.
EXCLUDE = {
    "liquidated_damages": r"requiring the state[^.]{0,40}to pay|does not agree to pay|unpaid wages|laborer or mechanic|overtime|indemnification, intellectual property, liquidated",
    "defect_warranty": r"insurance|procure and maintain|cease to provide the maintenance or warranty",
    "data_ownership": r"property of the (ssa|homeland)|wris data",
    "sla_fee_reduction": r"seniority|retirement",
    "outcome_payment": r"contingent fees?|covenant against",
    "accuracy_standard": r"payment error rate measurement|perm:",
}


def text_for(prefix):
    matches = sorted(DATA.glob(f"{prefix}__*"))
    if len(matches) != 1:
        raise FileNotFoundError(f"Expected one file for {prefix}, found {len(matches)}")
    source = matches[0]
    if source.suffix.lower() != ".pdf":
        return "", source.name
    target = CACHE / (source.stem + ".txt")
    if not target.exists():
        if not shutil.which("pdftotext"):
            raise RuntimeError("pdftotext is required to extract contract text")
        CACHE.mkdir(parents=True, exist_ok=True)
        subprocess.run(["pdftotext", "-layout", str(source), str(target)], check=True,
                       stderr=subprocess.DEVNULL)
    return re.sub(r"\s+", " ", target.read_text(errors="ignore")), source.name


def first_match(name, pattern, text):
    for m in re.finditer(pattern, text, re.I):
        window = text[max(0, m.start()-150):m.end()+150]
        if name not in EXCLUDE or not re.search(EXCLUDE[name], window, re.I):
            return m
    return None


def main():
    families = list(csv.DictReader((HERE / "contracts.csv").open()))
    rows = []
    for fam in families:
        texts = [text_for(p) for p in fam["documents"].split(";")]
        chars = sum(len(t) for t, _ in texts)
        for name, pattern in RULES.items():
            hits, snippet, where = 0, "", ""
            for text, filename in texts:
                m = first_match(name, pattern, text)
                if m:
                    hits += 1
                    if not snippet:
                        snippet = text[max(0, m.start()-120):m.end()+120].strip()
                        where = filename.split("__")[0]
            rows.append(dict(family_id=fam["family_id"], indicator=name, present=int(hits > 0),
                             documents_matched=hits, documents=len(texts), text_chars=chars,
                             document=where, snippet=snippet))
    with (HERE / "contract_terms.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Coded {len(RULES)} indicators for {len(families)} contract families")


if __name__ == "__main__":
    main()

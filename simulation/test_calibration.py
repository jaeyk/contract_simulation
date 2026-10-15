"""Data integrity of the hand-coded contract records and calibration identities."""
import json
import unittest

from calibrate import (CAL, amendment_moments, calibrate_family, coded_terms, map_parameters, read)
from models import solve


class CalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = json.loads((CAL / "coding_rules.json").read_text())
        cls.amendments = read("amendments.csv")
        cls.moments = amendment_moments(cls.amendments)
        cls.codes = coded_terms(read("contract_terms.csv"), read("term_overrides.csv"))

    def test_records_reference_known_families_and_documents(self):
        contracts = {r["family_id"]: r for r in read("contracts.csv")}
        for name in ["amendments.csv", "prices.csv", "sla_caps.csv", "negotiated_terms.csv"]:
            for r in read(name):
                self.assertIn(r["family_id"], contracts, name)
                self.assertIn(r["document"], contracts[r["family_id"]]["documents"], name)
        self.assertEqual(set(self.codes), set(contracts))

    def test_amendment_values_chain_and_match_stated_totals(self):
        for r in self.amendments:
            if r["value_before"] and r["change"] and r["value_after"]:
                self.assertAlmostEqual(float(r["value_before"])+float(r["change"]), float(r["value_after"]), delta=.02)
        il = self.moments["IL-IDES-DELOITTE-PUA"]
        self.assertAlmostEqual(il["base"]+il["unplanned"], 33834194)  # "Revised Total" in the 7th amendment
        mi = self.moments["MI-DTMB-FAST-MIDAS"]
        self.assertAlmostEqual(mi["base"]+mi["unplanned"]+mi["planned"], 88949785.72, delta=.02)  # CN32 aggregate

    def test_overrides_apply(self):
        self.assertEqual(self.codes["MI-DTMB-FAST-MIDAS"]["liquidated_damages"], 0)

    def test_calibrated_amendment_price_matches_observed_growth(self):
        fam = "MI-DTMB-FAST-MIDAS"
        mapped = map_parameters(fam, self.codes, read("negotiated_terms.csv"), read("sla_caps.csv"), self.rules)
        self.assertAlmostEqual(mapped["F"], self.rules["base_units"]*.05)
        rows = calibrate_family(fam, self.moments[fam], mapped, .5, self.rules)
        for r in rows:
            if r["consistent"]:
                self.assertAlmostEqual(r["amendment_price"], self.moments[fam]["growth"]*self.rules["base_units"])
                self.assertAlmostEqual(solve(1, r["params"])["initial_price"]+r["base_scope_cost"],
                                       self.rules["base_units"])
        # Margin share rises with bargaining power over the consistent set.
        shares = [r["amendment_margin_share"] for r in rows if r["consistent"]]
        self.assertEqual(shares, sorted(shares))

    def test_negotiated_reductions_lower_mapped_parameters(self):
        fam = "AZ-DES-GEOSOL-UI"
        caps = read("sla_caps.csv")
        with_cuts = map_parameters(fam, self.codes, read("negotiated_terms.csv"), caps, self.rules)
        without = map_parameters(fam, self.codes, [], caps, self.rules)
        self.assertLess(with_cuts["p"], without["p"])
        self.assertLess(with_cuts["w"], without["w"])


if __name__ == "__main__":
    unittest.main()

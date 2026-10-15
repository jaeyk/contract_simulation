"""Economic invariants, boundary cases, and independent objective comparisons."""
import math
import unittest
from design import optimize
from models import DEFAULTS, solve


class EquilibriumTests(unittest.TestCase):
    def test_baseline_accounting_and_portability(self):
        for p in [0, 1, 4]:
            r = solve(1, {"p": p})
            self.assertAlmostEqual(r["vendor_profit"], 0)
            self.assertAlmostEqual(r["agency_gross_payment"], r["vendor_real_cost"]+r["expected_penalty"])
        self.assertGreater(solve(1, {"p": 0})["dependence"], solve(1, {"p": 4})["dependence"])
        with self.assertRaises(ValueError):
            solve(1, {"cI": 100})

    def test_remediation_against_direct_objective(self):
        for w in [0, .375, .5, 1]:
            r = solve(2, {"w": w})
            e = r["effort"]
            payoff = lambda x: -x*x/2+math.exp(-x)*((1-w)*3-w*5)
            for i in range(501):
                self.assertGreaterEqual(payoff(e)+1e-10, payoff(i/100))
            self.assertGreaterEqual(r["welfare_loss"], -1e-10)
        self.assertEqual(solve(2, {"w": .375})["effort"], 0)

    def test_workflow_boundaries_and_benchmark(self):
        self.assertEqual(solve(3, {"t": 0, "R": 0})["work"], 0)
        self.assertEqual(solve(3, {"t": 100})["work"], 10)
        self.assertAlmostEqual(solve(3)["work"], 2)
        for t in [0, 3, 8]:
            for R in [0, 5, 20]:
                r = solve(3, {"t": t, "R": R})
                payoff = lambda x: (t-1)*x-x*x/2+R*(1-math.exp(-.5*x))
                self.assertGreaterEqual(payoff(r["work"])+1e-10, max(payoff(i/100) for i in range(1001)))
                self.assertGreaterEqual(r["welfare_loss"], -1e-10)

    def test_flags_conservation_and_alignment(self):
        tau = 22/70
        r = solve(4, {"t": 2+5*(1-tau)})
        self.assertAlmostEqual(r["welfare_loss"], 0)
        self.assertAlmostEqual(r["true_positive_mass"]+r["false_positive_mass"], r["flag_rate"])
        self.assertEqual(solve(4, {"m": 0, "t": 2})["flag_rate"], 0)
        self.assertEqual(solve(4, {"t": 100})["flag_rate"], 1)

    def test_validation_incentives(self):
        r = solve(5)
        x = r["test_probability"]
        self.assertAlmostEqual(1-.4, 1-(1-x)**4)
        self.assertGreaterEqual(r["duplicate_test_probability"], 0)
        r = solve(5, {"c": 1.5})
        self.assertEqual(r["expected_tests"], 0)
        self.assertGreater(r["coordinated_welfare"], 0)
        self.assertTrue(solve(5, {"c": 1})["equality_boundary"])

    def test_local_validation(self):
        r = solve(5)  # omega*Lloc = .5 < ell = .6 < Lloc = 1: socially valuable test omitted
        self.assertFalse(r["local_test"])
        self.assertTrue(r["local_test_public"])
        self.assertAlmostEqual(r["local_welfare_loss"], 5*.4)
        self.assertAlmostEqual(r["total_welfare_loss"], r["welfare_loss"]+r["local_welfare_loss"])
        self.assertEqual(solve(5, {"omega": 1})["local_welfare_loss"], 0)  # full internalization
        self.assertEqual(solve(5, {"ell": 2})["local_welfare_loss"], 0)  # not worth testing
        self.assertTrue(solve(5, {"omega": .6})["local_test"])  # tie: test

    def test_review_backward_induction(self):
        r = solve(6)
        self.assertFalse(r["high_effort"])
        self.assertTrue(r["review"])
        self.assertEqual(r["social_cost"], 20)
        self.assertEqual(r["public_social_cost"], 15)
        for h in [1, 8, 20, 40, 60]:
            for c in [5, 10]:
                r = solve(6, {"h": h, "c": c})
                # Exhaustively compare the four planner choices.
                benchmark = min(h, 50, c+h, c+10)
                self.assertEqual(r["public_social_cost"], benchmark)
                self.assertGreaterEqual(r["welfare_loss"], 0)
        self.assertTrue(solve(6, {"h": 60})["high_effort"])

    def test_substitution_feasibility_and_social_savings(self):
        r = solve(7)
        self.assertFalse(r["substitutes"])
        self.assertAlmostEqual(r["minimum_audit"], 2/3)
        r = solve(7, {"F": 0, "R": 0})
        self.assertIsNone(r["minimum_audit"])
        self.assertTrue(r["substitutes"])
        r = solve(7, {"H": 2})
        self.assertEqual(r["social_cost"], -2)  # Beneficial substitution.
        self.assertTrue(solve(7, {"rho": 0})["substitutes"])

    def test_lockin_remediation_joint_optimum(self):
        for over in [{}, {"p": 0}, {"w": .1}, {"w": .9, "theta": .8}, {"lam": 0}]:
            q = DEFAULTS["8"] | over
            r = solve(8, over)
            S = lambda k: q["s0"]+q["alpha"]*k/(1+q["p"])
            def payoff(e, k):
                mu = q["theta"]*(q["rR"]+S(k)-q["r"])
                return (-q["c"]*e*e/2-q["ck"]*k*k/2+q["lam"]*q["theta"]*(q["cR"]+S(k)-q["cI"])
                        + math.exp(-e)*((1-q["w"])*mu-q["w"]*(q["r"]+q["f"])))
            best = max(payoff(i/50, j/100) for i in range(151) for j in range(151))
            self.assertGreaterEqual(payoff(r["effort"], r["dependence"])+1e-9, best)
            self.assertAlmostEqual(r["vendor_profit"], 0)
            self.assertGreaterEqual(r["welfare_loss"], -1e-10)
        # Lock-in feedback: portability lowers dependence and therefore raises prevention.
        self.assertGreater(solve(8, {"p": 4})["effort"], solve(8, {"p": 0})["effort"])
        self.assertLess(solve(8, {"p": 4})["dependence"], solve(8, {"p": 0})["dependence"])
        # Without bargaining power, repairs carry no margin and Model 2's warranty condition returns.
        r = solve(8, {"theta": 0})
        self.assertEqual(r["dependence"], 0)
        self.assertAlmostEqual(r["effort"], solve(2, {"w": .5, "mu": 0, "r": 2, "f": 3, "c": 1})["effort"], 6)

    def test_workflow_review_backward_induction(self):
        for over in [{}, {"t": 6}, {"f": 12}, {"h": 20}, {"R": 10, "t": 0}, {"kappa": 15}]:
            q = DEFAULTS["9"] | over
            r = solve(9, over)
            def vendor(n):
                raw = math.exp(-q["a"]*n)
                reviewed = q["h"] <= raw*(q["L"]-q["f"]-q["kappa"])
                return ((q["t"]-q["c"])*n-q["d"]*n*n/2+q["R"]*(1-raw)
                        - q["f"]*raw*(not reviewed))
            grid = [i/100 for i in range(1001)]
            self.assertGreaterEqual(vendor(r["work"])+1e-9, max(map(vendor, grid)))
            def social(n, rv):
                raw = math.exp(-q["a"]*n)
                return ((q["c"]+q["b"])*n+q["d"]*n*n/2
                        + (q["h"]+q["kappa"]*raw if rv else q["L"]*raw))
            best = min(social(n, rv) for n in grid for rv in (0, 1))
            self.assertLessEqual(r["public_social_cost"], best+1e-9)
            self.assertGreaterEqual(r["welfare_loss"], -1e-10)
        self.assertTrue(solve(9)["review"])
        self.assertFalse(solve(9, {"h": 20})["review"])

    def test_optimal_design(self):
        # One instrument suffices to implement the one-dimensional public optimum in Model 3.
        usage = optimize(3, {"t": [0, 10]}, "social_welfare", {"R": 0})
        self.assertAlmostEqual(usage["outcome"]["welfare_loss"], 0, 6)
        # Model 4 recovers the analytic alignment reward t = c + m f (1 - tau_SP).
        flags = optimize(4, {"t": [0, 15]}, "social_welfare")
        self.assertAlmostEqual(flags["instruments"]["t"], 2+5*(1-22/70), 3)
        # Model 6: a large enough penalty removes the agency's review commitment problem.
        review = optimize(6, {"f": [0, 99.9]}, "social_cost")
        self.assertEqual(review["value"], 15)
        self.assertGreater(review["instruments"]["f"], 60)
        # A higher weight on applicant burden weakly raises monitoring.
        low = optimize(1, {"m": [0, 1]}, "agency_value", {"omega": 0})
        high = optimize(1, {"m": [0, 1]}, "agency_value", {"omega": 3})
        self.assertGreaterEqual(high["instruments"]["m"], low["instruments"]["m"])
        with self.assertRaises(ValueError):
            optimize(2, {"w": [0, 1]}, "social_cost", costs={"mu": 1})

    def test_invalid_parameters(self):
        for model, override in [(1, {"m": 2}), (2, {"c": 0}), (3, {"a": -1}),
                                (4, {"v": float("nan")}), (5, {"N": 2.5}), (5, {"omega": 2}),
                                (6, {"f": 100}), (7, {"rho": 2}), (8, {"r": 10}),
                                (8, {"w": 1.5}), (9, {"f": 20}), (9, {"h": 0}), (1, {"typo": 1})]:
            with self.assertRaises(ValueError):
                solve(model, override)


if __name__ == "__main__":
    unittest.main()

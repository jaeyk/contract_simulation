"""Deterministic continuation equilibria; notation follows game_theory notes."""
import math
from math import exp, isfinite


DEFAULTS = {
    "1": dict(m=.5, p=1., F=10., ce=1., ck=1., lam=.5, theta=.5,
              alpha=2., s0=1., cR=3., cI=2., V=20., b=5., omega=1., gm=1., gp=.2),
    "2": dict(w=.5, mu=3., r=2., f=3., c=1., H=10.),
    "3": dict(t=3., R=0., a=.5, c=1., d=1., b=1., V=20., cap=10.),
    "4": dict(t=5., c=2., m=.5, f=10., v=50., h=20.),
    "5": dict(N=5, c=.4, B=1., ell=.6, Lloc=1., omega=.5),
    "6": dict(pH=.1, pL=.5, L=100., f=20., h=20., c=5.),
    "7": dict(s=4., H=10., d=.5, F=2., R=10., rho=1., k=5.),
    "8": dict(w=.5, f=3., r=2., rR=3., p=1., theta=.5, alpha=2., s0=1., lam=.5,
              cI=2., cR=3., c=1., ck=1., H=10.),
    "9": dict(t=3., R=0., a=.5, c=1., d=1., b=1., cap=10., L=20., f=5., h=2., kappa=4.),
}


def validate(model, p):
    if set(p) != set(DEFAULTS[model]):
        raise ValueError(f"Model {model}: expected parameters {sorted(DEFAULTS[model])}")
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or
           not isfinite(x) or x < 0 for x in p.values()):
        raise ValueError("Parameters must be finite, nonnegative numbers")
    bounded = {"1": ["m", "lam", "theta"], "2": ["w"], "3": [],
               "4": ["m"], "5": ["omega"], "6": ["pH", "pL"], "7": ["d", "rho"],
               "8": ["w", "theta", "lam"], "9": []}
    positive = {"1": ["ce", "ck"], "2": ["c", "H"], "3": ["a", "d", "V", "cap"],
                "4": ["v"], "5": ["c", "B", "ell"], "6": ["L", "h", "c"],
                "7": ["s", "d", "k"], "8": ["c", "ck", "H"],
                "9": ["a", "d", "cap", "L", "h"]}
    if any(p[k] > 1 for k in bounded[model]) or any(p[k] <= 0 for k in positive[model]):
        raise ValueError(f"Model {model}: parameter outside its theoretical domain")
    if model == "1" and p["cR"] + p["s0"] < p["cI"]:
        raise ValueError("Model 1 requires cR+s0 >= cI (global continuation region)")
    if model == "5" and (p["N"] < 2 or int(p["N"]) != p["N"]):
        raise ValueError("N must be an integer >= 2")
    if model == "6" and not (p["pH"] < p["pL"] and p["f"] < p["L"]):
        raise ValueError("Model 6 requires pH < pL and f < L")
    if model == "8" and (p["cR"] + p["s0"] < p["cI"] or p["rR"] + p["s0"] < p["r"]):
        raise ValueError("Model 8 requires cR+s0 >= cI and rR+s0 >= r (continuation regions)")
    if model == "9" and p["f"] >= p["L"]:
        raise ValueError("Model 9 requires f < L")


def optimum(derivative, upper):
    """Maximize a concave objective on [0, upper] by its decreasing derivative."""
    if derivative(0.) <= 0:
        return 0.
    if derivative(upper) >= 0:
        return upper
    lo, hi = 0., upper
    for _ in range(90):
        mid = (lo + hi) / 2
        if derivative(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def effort(incentive, cost):
    if incentive <= 0:
        return 0.
    hi = 1.
    while cost * hi < incentive * exp(-hi):
        hi *= 2
    return optimum(lambda e: incentive * exp(-e) - cost * e, hi)


def baseline(m, p, F, ce, ck, lam, theta, alpha, s0, cR, cI, V, b, omega, gm, gp):
    e = effort(m * F, ce)
    k = lam * theta * alpha / (ck * (1 + p))
    failure = exp(-e)
    switch = s0 + alpha * k / (1 + p)
    amendment = cI + theta * (cR + switch - cI)
    real_cost = ce * e**2 / 2 + ck * k**2 / 2 + lam * cI
    penalty = m * F * failure
    initial = real_cost + penalty - lam * amendment
    payments = initial + lam * amendment
    governance = (gm * m*m + gp * p*p) / 2
    return dict(effort=e, dependence=k, success=1-failure, burden=b*failure,
                switching_cost=switch, amendment_price=amendment, initial_price=initial,
                negative_initial_bid=initial < 0, vendor_revenue=payments,
                vendor_real_cost=real_cost, expected_penalty=penalty,
                vendor_profit=payments-real_cost-penalty, agency_gross_payment=payments,
                agency_net_payment_if_penalty_received=payments-penalty,
                agency_value=V*(1-failure)-payments-omega*b*failure-governance,
                social_welfare_if_penalty_transfer=V*(1-failure)-real_cost-b*failure-governance)


def remediation(w, mu, r, f, c, H):
    D = w*(r+f)-(1-w)*mu
    e, sp = effort(D, c), effort(H, c)
    defect = exp(-e)
    revenue = defect*(1-w)*(r+mu)
    cost = c*e*e/2 + defect*r
    penalty = defect*w*f
    social = c*e*e/2 + H*defect
    best = c*sp*sp/2 + H*exp(-sp)
    return dict(effort=e, public_effort=sp, defect_probability=defect,
                private_defect_loss=D, vendor_revenue_excluding_fixed=revenue,
                vendor_real_cost=cost, expected_penalty=penalty,
                vendor_profit_excluding_fixed=revenue-cost-penalty,
                agency_gross_payment_excluding_fixed=revenue,
                social_cost=social, public_social_cost=best, welfare_loss=social-best)


def workflow(t, R, a, c, d, b, V, cap):
    n = optimum(lambda x: t-c-d*x+R*a*exp(-a*x), cap)
    sp = optimum(lambda x: V*a*exp(-a*x)-c-b-d*x, cap)
    q = 1-exp(-a*n)
    revenue = t*n+R*q
    cost = c*n+d*n*n/2
    welfare = lambda x: V*(1-exp(-a*x))-(c+b)*x-d*x*x/2
    return dict(work=n, public_work=sp, work_gap=n-sp, success=q,
                vendor_revenue_excluding_fixed=revenue, vendor_real_cost=cost,
                vendor_profit_excluding_fixed=revenue-cost, burden=b*n,
                social_welfare=welfare(n), public_social_welfare=welfare(sp),
                welfare_loss=welfare(sp)-welfare(n))


def flags(t, c, m, f, v, h):
    # z ~ Uniform(0,1), with truth Bernoulli(z): calibrated prevalence = 1/2.
    tau = max(0., min(1., 1-(t-c)/(m*f))) if m*f else (0. if t > c else 1.)
    sp = max(0., min(1., (h+c)/(v+h)))
    def metrics(x):
        tp, fp = (1-x*x)/2, (1-x)**2/2
        return tp, fp, v*tp-h*fp-c*(1-x)
    tp, fp, welfare = metrics(tau)
    best = metrics(sp)[2]
    revenue, cost, penalty = t*(1-tau), c*(1-tau), m*f*fp
    return dict(threshold=tau, public_threshold=sp, flag_rate=1-tau,
                true_positive_mass=tp, false_positive_mass=fp,
                false_negative_mass=.5-tp, false_positive_rate=2*fp,
                vendor_revenue_excluding_fixed=revenue, vendor_real_cost=cost,
                expected_penalty=penalty, vendor_profit_excluding_fixed=revenue-cost-penalty,
                applicant_harm=h*fp, social_welfare=welfare, welfare_loss=best-welfare)


def validation(N, c, B, ell, Lloc, omega):
    # At c=B select the no-testing equilibrium; other weak equilibria exist.
    x = 1-(c/B)**(1/(N-1)) if c < B else 0.
    no = (1-x)**N
    one = N*x*(1-x)**(N-1)
    welfare = N*B*(1-no)-c*N*x
    coordinated = max(0., N*B-c)
    return dict(test_probability=x, no_test_probability=no,
                duplicate_test_probability=max(0., 1-no-one), expected_tests=N*x,
                symmetric_equilibrium="mixed" if c < B else "no_test",
                asymmetric_one_tester_equilibrium=c <= B,
                selected_welfare=welfare, coordinated_welfare=coordinated,
                welfare_loss=coordinated-welfare, equality_boundary=c == B,
                # Independent local tests: no spillovers; the agency values omega*Lloc.
                local_test=omega*Lloc >= ell, local_test_public=Lloc >= ell,
                local_welfare_loss=N*(Lloc-ell)*(omega*Lloc < ell <= Lloc),
                total_welfare_loss=coordinated-welfare+N*(Lloc-ell)*(omega*Lloc < ell <= Lloc))


def review(pH, pL, L, f, h, c):
    # Agency skips review at indifference; vendor selects low effort at indifference.
    rh, rl = h < pH*(L-f), h < pL*(L-f)
    high_cost, low_cost = c+f*pH*(not rh), f*pL*(not rl)
    high = high_cost < low_cost
    p, reviewing = (pH, rh) if high else (pL, rl)
    real = c*high+h*reviewing
    harm = p*L*(not reviewing)
    sp = min(c+min(h,pH*L), min(h,pL*L))
    penalty = f*p*(not reviewing)
    return dict(high_effort=high, review=reviewing, review_after_high=rh,
                review_after_low=rl, raw_error=p, final_error=p*(not reviewing),
                vendor_real_cost=c*high, expected_penalty=penalty,
                vendor_profit_excluding_fixed=-c*high-penalty,
                agency_review_cost=h*reviewing, agency_net_cost_excluding_fixed=h*reviewing+harm-penalty,
                social_cost=real+harm, public_social_cost=sp, welfare_loss=real+harm-sp)


def substitution(s, H, d, F, R, rho, k):
    sanction = d*(F+rho*R)
    threshold = s/sanction if sanction else None
    feasible = threshold is not None and threshold <= 1
    # Vendor retains quality at indifference; agency tolerates at policy indifference.
    deter = feasible and k*threshold < H
    audit = threshold if deter else 0.
    social_cost = k*audit if deter else H-s
    feasible_best = min(H-s, k*threshold) if feasible else H-s
    return dict(minimum_audit=threshold, deterrence_feasible=feasible,
                selected_audit=audit, substitutes=not deter,
                vendor_cost_saving=0. if deter else s,
                public_harm=0. if deter else H, audit_cost=k*audit,
                agency_cost=k*audit+(0. if deter else H),
                social_cost=social_cost, best_feasible_policy_social_cost=feasible_best,
                policy_welfare_loss=social_cost-feasible_best)


def maximize(f, df, lo, hi, points=2001):
    """Global grid search on [lo, hi] for f, then bisection on its derivative df inside
    the bracket around the best grid point (golden-section search cannot resolve a flat
    maximum below ~1e-8)."""
    step = (hi-lo)/(points-1)
    best = max(range(points), key=lambda i: f(lo+i*step))
    a, b = lo+max(best-1, 0)*step, lo+min(best+1, points-1)*step
    if df(a) <= 0:
        return a
    if df(b) >= 0:
        return b
    for _ in range(90):
        mid = (a+b)/2
        if df(mid) > 0:
            a = mid
        else:
            b = mid
    return (a+b)/2


def lockin_remediation(w, f, r, rR, p, theta, alpha, s0, lam, cI, cR, c, ck, H):
    # Model 8 = Model 1 + Model 2: uncovered defects become amendments priced by lock-in bargaining.
    switch = lambda k: s0+alpha*k/(1+p)
    margin = lambda k: theta*(rR+switch(k)-r)
    best_k = lambda e: theta*alpha*(lam+(1-w)*exp(-e))/(ck*(1+p))
    def payoff(e, k):
        return (-c*e*e/2-ck*k*k/2+lam*theta*(cR+switch(k)-cI)
                + exp(-e)*((1-w)*margin(k)-w*(r+f)))
    # k*(e) is the exact best response, so maximizing the profile over e solves the joint
    # problem; by the envelope theorem the profile's slope is the partial derivative in e.
    profile_slope = lambda e: -c*e+exp(-e)*(w*(r+f)-(1-w)*margin(best_k(e)))
    e = maximize(lambda x: payoff(x, best_k(x)), profile_slope, 0., max(w*(r+f)/c, 0.)+1.)
    k = best_k(e)
    defect, mu = exp(-e), margin(k)
    amendment = cI+theta*(cR+switch(k)-cI)
    repairs = (1-w)*defect
    continuation = lam*amendment+repairs*(r+mu)
    real_cost = c*e*e/2+ck*k*k/2+lam*cI+defect*r
    penalty = defect*w*f
    initial = real_cost+penalty-continuation
    sp = effort(H, c)
    social = c*e*e/2+ck*k*k/2+lam*cI+H*defect
    best = c*sp*sp/2+lam*cI+H*exp(-sp)
    return dict(effort=e, dependence=k, defect_probability=defect, public_effort=sp,
                switching_cost=switch(k), repair_margin=mu, repair_price=r+mu,
                private_defect_loss=w*(r+f)-(1-w)*mu, amendment_price=amendment,
                paid_repair_probability=repairs, continuation_revenue=continuation,
                initial_price=initial, negative_initial_bid=initial < 0,
                vendor_real_cost=real_cost, expected_penalty=penalty,
                agency_gross_payment=initial+continuation,
                vendor_profit=initial+continuation-real_cost-penalty,
                social_cost=social, public_social_cost=best, welfare_loss=social-best)


def workflow_review(t, R, a, c, d, b, cap, L, f, h, kappa):
    # Model 9 = Model 3 + Model 6: vendor picks work n; agency then reviews if it pays.
    # Review costs h plus kappa per corrected error and removes all errors before harm.
    # The agency reviews at indifference (this keeps the vendor's problem attained).
    net = L-f-kappa
    cutoff = math.log(net/h)/a if net >= h else -1.  # agency reviews iff n <= cutoff
    base = lambda n: (t-c)*n-d*n*n/2+R*(1-exp(-a*n))
    dbase = lambda n: t-c-d*n+R*a*exp(-a*n)
    options = []
    if cutoff >= 0:
        top = min(cutoff, cap)
        n = optimum(dbase, top)
        options.append((base(n), 1, n))
    if cutoff < cap:
        lo = max(cutoff, 0.)
        n = lo+optimum(lambda x: dbase(lo+x)+f*a*exp(-a*(lo+x)), cap-lo)
        # n == cutoff is reviewed, and its unreviewed limit is weakly worse than reviewing.
        if n > cutoff:
            options.append((base(n)-f*exp(-a*n), 0, n))
    value, reviewing, n = max(options, key=lambda o: (o[0], o[1]))
    raw = exp(-a*n)
    cost = lambda x, rv: (c+b)*x+d*x*x/2+(h+kappa*exp(-a*x) if rv else L*exp(-a*x))
    with_review = optimum(lambda x: kappa*a*exp(-a*x)-c-b-d*x, cap)
    without = optimum(lambda x: L*a*exp(-a*x)-c-b-d*x, cap)
    public = min([(cost(with_review, 1), 1, with_review), (cost(without, 0), 0, without)],
                 key=lambda o: (o[0], o[1]))
    revenue = t*n+R*(1-raw)
    real = c*n+d*n*n/2
    penalty = f*raw*(not reviewing)
    social = cost(n, reviewing)
    return dict(work=n, review=bool(reviewing), review_cutoff_work=max(cutoff, 0.),
                raw_error=raw, final_error=raw*(not reviewing),
                vendor_revenue_excluding_fixed=revenue, vendor_real_cost=real,
                expected_penalty=penalty, vendor_profit_excluding_fixed=revenue-real-penalty,
                agency_review_cost=(h+kappa*raw)*reviewing, burden=b*n,
                public_work=public[2], public_review=bool(public[1]),
                social_cost=social, public_social_cost=public[0], welfare_loss=social-public[0])


FUNCTIONS = dict(zip(DEFAULTS, [baseline, remediation, workflow, flags, validation, review,
                                substitution, lockin_remediation, workflow_review]))


def solve(model, overrides=None):
    model = str(model)
    p = DEFAULTS[model] | (overrides or {})
    validate(model, p)
    return FUNCTIONS[model](**p)

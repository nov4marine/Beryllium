
        Non-linear demand system: 
        Ci = N + (a * (W ** b)) * (Pb / Pi) ** ei
        Where:
        Ci = Consumption of good i
        N = Base need for good i
        a = Scaling factor for wealth impact
        W = Wealth of the pop
        b = elasticity exponent, 
        determining whether the good is necessity (b < 1), normal (b = 1), luxury (b > 1),
        or inferior (b < 0).
        Pb = Base price of good i
        Pi = Actual price of good i
        ei = Price elasticity of demand for good i,
        0 < ei < 1 for necessities, ei > 1 for luxuries

        Total Consumption = Base Need + Wealth Effect * Price Effect

        Total spending power formula:
        X = s * income + (1 - s) * wealth
        Where:
        X = total spending power
        s = modifier for income vs wealth influence (0 < s < 1) where,
        higher t means income has more influence
        income = after tax and transfer income. Also after savings/reinvestment
        (so income = gross income - taxes + transfers - savings)
        wealth = accumulated wealth/savings

        Structural Savings Formula:
        S = Smin + (Smax - Smin) * (popwealth/wealth benchmark)
        Where:
        S = structural savings rate (portion of income saved, not spent)
        popwealth = wealth of the pop
        wealth benchmark = benchmark wealth level for max savings rate
        Smin = minimum savings rate (for low wealth pops) = 0.05
        Smax = maximum savings rate (for high wealth pops) = 0.30

        --- Capital Market ---
        cost of capital / interest rate formula:
        interest rate = base_rate * (target_pool_size / actual_pool size) ** p
        Where:
        base_rate = baseline interest rate set by central bank = 0.05 (5%)
        target_pool_size = desired size of capital pool expressed as a percentage of GDP = 0.1 (10%)
        actual_pool_size = current size of capital pool expressed as a percentage of GDP
        p = sensitivity exponent = 0.5

        expected rate of return on investment formula:
        expected_return = expected monthly profit of construction / construction cost

        decision to invest if: expected_return > interest_rate + risk_premium (2 or 3%)


        # --- PARAMETER DEFINITION (Place this in a separate file or class variable) ---
        NEEDS_PARAMETERS = {
        # Good: [Base, Scaling Factor (alpha), Elasticity Exponent (beta)]
        "Food":             [15.0, 0.30, 0.8],  # Necessity (beta < 1)
        "Housing":          [30.0, 0.30, 0.7],  # Strong Necessity
        "Consumer Goods":   [20.0, 0.30, 0.8],  # Base necessity component
        "Services":         [1.0,  0.015, 1.05], # Normal Good (beta ~ 1)
        "Amenities":        [1.0,  0.10, 1.5],  # Luxury (beta > 1)
        "Healthcare":       [1.0,  0.10, 0.8],  # Necessity
        "Transportation":   [0.0,  0.15, 1.3],  # Luxury (No base need)
        "Luxury Goods":     [0.0,  0.15, 1.5],  # Strong Luxury (No base need)
        }
        """
        consumption = {}
        for good, params in NEEDS_PARAMETERS.items():
            base_need, alpha, beta = params
            consumption[good] = base_need + (alpha * (self.wealth ** beta))
        self.needs = consumption


class Bank: 
    def __init__(self, nation):
        self.nation = nation
        self.interest_rate = 0.05  # Default interest rate of 5%
        self.funds = 0

    def calculate_interest_rate(self, target_liquidity_ratio=0.1, rho=0.5):
        """Calculate interest rate based on nation's liquidity."""
        target_liquidity = self.nation.gdp * target_liquidity_ratio
        current_liquidity = max(1.0, self.funds)
        liquidity_ratio = target_liquidity / current_liquidity

        i_base = 0.05  # Base interest rate

        self.interest_rate = i_base * (liquidity_ratio ** rho)

        return min(0.25, self.interest_rate)  # Cap interest rate at 25%

    def get_interest_rate(self):
        return self.interest_rate
    
    def allocate_investment(self):
            
            interest_rate = self.calculate_interest_rate()
            risk_premium = 0.03 # 3% buffer for risk
            
            investment_threshold = interest_rate + risk_premium
            
            # List of candidate buildings to build (Factories, Mines, etc.)
            candidate_buildings = self.get_investment_candidates() 
            
            # Sort candidates by highest expected return to prioritize best projects
            candidate_buildings.sort(key=lambda b: b.expected_return, reverse=True)
            
            for building_type in candidate_buildings:
                r_expected = building_type.calculate_expected_return() # Based on average profits
                cost = building_type.construction_cost
                
                # 1. THE DECISION: Is the return high enough?
                if r_expected > investment_threshold:
                    
                    # 2. THE FEASIBILITY CHECK: Is the money available?
                    if self.Investment_Pool >= cost:
                        
                        # 3. EXECUTE INVESTMENT
                        self.Investment_Pool -= cost
                        self.Total_Savings_Invested += cost # Total share value increases
                        
                        # Log the construction start and add the building to the map
                        self.start_construction(building_type)
                        
                        # Optional: Break here if you only allow one major project per tick
                        # break 
                    
                    else:
                        # Investment Pool is empty, construction halts for this tick
                        break 
                
                else:
                    # Expected return is too low (market is saturated or goods are too cheap)
                    # Stop investing in less profitable ventures
                    break
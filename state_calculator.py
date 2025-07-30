import argparse
import json
import math

def calculate_lp_greeks(L, Pa, Pb, P):
    """
    Calculates the Delta and Gamma of a Uniswap v3 LP position.
    Formulas are based on the NABLA V3.0 PDF.
    """
    # Ensure prices are floats for calculation
    L, Pa, Pb, P = float(L), float(Pa), float(Pb), float(P)

    sqrt_L = math.sqrt(L)
    sqrt_Pa = math.sqrt(Pa)
    sqrt_Pb = math.sqrt(Pb)
    sqrt_P = math.sqrt(P)

    delta = 0.0
    gamma = 0.0

    if P <= Pa:
        # Out of range (all in volatile asset)
        delta = sqrt_L * (1/sqrt_Pa - 1/sqrt_Pb)
    elif P >= Pb:
        # Out of range (all in stablecoin)
        delta = 0.0
    else:  # In range: Pa < P < Pb
        # Delta formula
        numerator_delta = sqrt_L * (sqrt_Pb - sqrt_P)
        denominator_delta = 2 * sqrt_P * (sqrt_Pb - sqrt_Pa)
        if denominator_delta != 0:
            delta = numerator_delta / denominator_delta

        # Gamma formula
        numerator_gamma = -sqrt_L * sqrt_Pb
        denominator_gamma = 4 * (P**1.5) * (sqrt_Pb - sqrt_Pa)
        if denominator_gamma != 0:
            gamma = numerator_gamma / denominator_gamma
    
    return {"delta": delta, "gamma": gamma}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate Uniswap v3 LP position greeks.")
    parser.add_argument("--liquidity_L", required=True, type=float, help="Liquidity amount L for the position.")
    parser.add_argument("--price_lower_Pa", required=True, type=float, help="Lower price bound Pa.")
    parser.add_argument("--price_upper_Pb", required=True, type=float, help="Upper price bound Pb.")
    parser.add_argument("--market_price", required=True, type=float, help="Current market price P.")
    
    args = parser.parse_args()
    
    greeks = calculate_lp_greeks(args.liquidity_L, args.price_lower_Pa, args.price_upper_Pb, args.market_price)
    
    print(json.dumps(greeks))
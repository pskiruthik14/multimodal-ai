"""
Item Response Theory (IRT) 2-Parameter Logistic (2PL) Model:
Estimates latent student ability theta and recommends items with optimal discrimination.
"""

import math
from typing import List, Tuple

class IRTEngine:
    """Computes Item Response Theory probability, information, and ability estimation."""

    @staticmethod
    def p_correct(theta: float, a: float, b: float) -> float:
        """
        2PL Logistic Model:
        P(Y = 1 | theta, a, b) = 1 / (1 + exp(-a * (theta - b)))
        where theta is student ability, b is item difficulty, a is discrimination.
        """
        exponent = -a * (theta - b)
        # Avoid overflow
        if exponent > 30:
            return 0.0
        elif exponent < -30:
            return 1.0
        return 1.0 / (1.0 + math.exp(exponent))

    @staticmethod
    def item_information(theta: float, a: float, b: float) -> float:
        """
        Fisher Information for 2PL model:
        I(theta) = a^2 * P(theta) * (1 - P(theta))
        """
        p = IRTEngine.p_correct(theta, a, b)
        return (a ** 2) * p * (1.0 - p)

    @classmethod
    def estimate_ability_eap(
        cls,
        responses: List[Tuple[bool, float, float]], # List of (is_correct, a, b)
        prior_mean: float = 0.0,
        prior_sd: float = 1.0
    ) -> float:
        """
        Expected A Posteriori (EAP) numerical integration over grid [-3.0, +3.0]
        to robustly estimate student ability theta from discrete responses.
        """
        if not responses:
            return prior_mean
            
        num_points = 61
        grid = [prior_mean - 3.0 * prior_sd + i * (6.0 * prior_sd / (num_points - 1)) for i in range(num_points)]
        weights = []
        
        for theta in grid:
            # Gaussian prior weight
            prior_w = math.exp(-0.5 * ((theta - prior_mean) / prior_sd) ** 2)
            # Likelihood
            likelihood = 1.0
            for is_correct, a, b in responses:
                p = cls.p_correct(theta, a, b)
                likelihood *= p if is_correct else (1.0 - p)
            weights.append(prior_w * likelihood)
            
        total_w = sum(weights)
        if total_w < 1e-12:
            return prior_mean
            
        # Expected value
        estimated_theta = sum(theta * w for theta, w in zip(grid, weights)) / total_w
        return round(estimated_theta, 2)

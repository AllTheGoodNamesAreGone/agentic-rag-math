# High-quality manually curated math problems
CURATED_MATH_PROBLEMS = [
    {
        "problem": "Solve the quadratic equation: 3x² - 7x + 2 = 0",
        "solution": """Step 1: Identify coefficients a=3, b=-7, c=2
Step 2: Apply quadratic formula: x = (-b ± √(b²-4ac)) / (2a)
Step 3: Calculate discriminant: Δ = (-7)² - 4(3)(2) = 49 - 24 = 25
Step 4: Since Δ > 0, we have two real solutions
Step 5: x = (7 ± √25) / 6 = (7 ± 5) / 6
Step 6: x₁ = (7 + 5)/6 = 12/6 = 2
Step 7: x₂ = (7 - 5)/6 = 2/6 = 1/3
Final Answer: x = 2 or x = 1/3""",
        "topic": "algebra",
        "difficulty": "intermediate",
        "source": "curated"
    },
    
    {
        "problem": "Find the derivative of f(x) = x⁴ - 3x³ + 2x² - x + 5",
        "solution": """Step 1: Apply power rule: d/dx(xⁿ) = nxⁿ⁻¹
Step 2: d/dx(x⁴) = 4x³
Step 3: d/dx(-3x³) = -3 × 3x² = -9x²
Step 4: d/dx(2x²) = 2 × 2x = 4x
Step 5: d/dx(-x) = -1
Step 6: d/dx(5) = 0 (constant rule)
Step 7: Combine all terms
Final Answer: f'(x) = 4x³ - 9x² + 4x - 1""",
        "topic": "calculus",
        "difficulty": "basic",
        "source": "curated"
    },
    
    {
        "problem": "Evaluate the definite integral: ∫₁³ (2x + 1) dx",
        "solution": """Step 1: Find the antiderivative of 2x + 1
Step 2: ∫(2x + 1)dx = x² + x + C
Step 3: Apply fundamental theorem of calculus: [x² + x]₁³
Step 4: Evaluate at upper limit: (3)² + (3) = 9 + 3 = 12
Step 5: Evaluate at lower limit: (1)² + (1) = 1 + 1 = 2
Step 6: Subtract: 12 - 2 = 10
Final Answer: 10""",
        "topic": "calculus",
        "difficulty": "intermediate",
        "source": "curated"
    },
    
    {
        "problem": "Solve the system of equations: 2x + 3y = 7, x - y = 1",
        "solution": """Step 1: Use substitution method
Step 2: From equation 2, solve for x: x = y + 1
Step 3: Substitute into equation 1: 2(y + 1) + 3y = 7
Step 4: Expand: 2y + 2 + 3y = 7
Step 5: Combine like terms: 5y + 2 = 7
Step 6: Solve for y: 5y = 5, so y = 1
Step 7: Find x: x = y + 1 = 1 + 1 = 2
Step 8: Verify: 2(2) + 3(1) = 4 + 3 = 7 ✓, 2 - 1 = 1 ✓
Final Answer: x = 2, y = 1""",
        "topic": "algebra",
        "difficulty": "basic",
        "source": "curated"
    },
    
    {
        "problem": "Use integration by parts to solve: ∫ x·ln(x) dx",
        "solution": """Step 1: Apply integration by parts formula: ∫u dv = uv - ∫v du
Step 2: Choose u = ln(x), dv = x dx (LIATE rule: Logarithm first)
Step 3: Find du = (1/x) dx, v = x²/2
Step 4: Apply formula: ∫x·ln(x) dx = ln(x)·(x²/2) - ∫(x²/2)·(1/x) dx
Step 5: Simplify: = (x²ln(x))/2 - ∫(x/2) dx
Step 6: Evaluate remaining integral: = (x²ln(x))/2 - (x²/4) + C
Step 7: Factor: = (x²/4)(2ln(x) - 1) + C
Final Answer: (x²/4)(2ln(x) - 1) + C""",
        "topic": "calculus",
        "difficulty": "advanced",
        "source": "curated"
    },
    
    {
        "problem": "Find the limit: lim(x→0) (sin(x)/x)",
        "solution": """Step 1: Recognize this is an indeterminate form 0/0
Step 2: This is a standard limit that equals 1
Step 3: Can be proven using L'Hôpital's rule or geometric reasoning
Step 4: Using L'Hôpital's rule: lim(x→0) (sin(x)/x) = lim(x→0) (cos(x)/1)
Step 5: Evaluate: cos(0)/1 = 1/1 = 1
Final Answer: 1""",
        "topic": "calculus",
        "difficulty": "intermediate",
        "source": "curated"
    },
    
    {
        "problem": "Factor completely: x³ - 8",
        "solution": """Step 1: Recognize this as difference of cubes: a³ - b³
Step 2: Use formula: a³ - b³ = (a - b)(a² + ab + b²)
Step 3: Here a = x, b = 2, so x³ - 8 = x³ - 2³
Step 4: Apply formula: (x - 2)(x² + x·2 + 2²)
Step 5: Simplify: (x - 2)(x² + 2x + 4)
Step 6: Check if x² + 2x + 4 can be factored further
Step 7: Discriminant = 2² - 4(1)(4) = 4 - 16 = -12 < 0, so no real factors
Final Answer: (x - 2)(x² + 2x + 4)""",
        "topic": "algebra",
        "difficulty": "intermediate",
        "source": "curated"
    },
    
    {
        "problem": "Find the area of a triangle with vertices at (0,0), (4,0), and (2,3)",
        "solution": """Step 1: Use the coordinate formula for triangle area
Step 2: Area = (1/2)|x₁(y₂ - y₃) + x₂(y₃ - y₁) + x₃(y₁ - y₂)|
Step 3: Substitute points: (x₁,y₁)=(0,0), (x₂,y₂)=(4,0), (x₃,y₃)=(2,3)
Step 4: Area = (1/2)|0(0 - 3) + 4(3 - 0) + 2(0 - 0)|
Step 5: Simplify: = (1/2)|0 + 12 + 0| = (1/2)|12| = (1/2)(12) = 6
Alternative: Base = 4, Height = 3, Area = (1/2)(4)(3) = 6
Final Answer: 6 square units""",
        "topic": "geometry",
        "difficulty": "basic",
        "source": "curated"
    }
]

# Additional problem categories for comprehensive coverage
ALGEBRA_PROBLEMS = [
    {
        "problem": "Simplify: (2x + 3)(x - 1) - (x + 2)²",
        "solution": """Step 1: Expand first product: (2x + 3)(x - 1) = 2x² - 2x + 3x - 3 = 2x² + x - 3
Step 2: Expand second product: (x + 2)² = x² + 4x + 4
Step 3: Subtract: (2x² + x - 3) - (x² + 4x + 4)
Step 4: Distribute negative: 2x² + x - 3 - x² - 4x - 4
Step 5: Combine like terms: (2x² - x²) + (x - 4x) + (-3 - 4)
Final Answer: x² - 3x - 7""",
        "topic": "algebra",
        "difficulty": "basic",
        "source": "curated"
    }
]

CALCULUS_PROBLEMS = [
    {
        "problem": "Find the critical points of f(x) = x³ - 6x² + 9x + 1",
        "solution": """Step 1: Find the first derivative: f'(x) = 3x² - 12x + 9
Step 2: Set f'(x) = 0: 3x² - 12x + 9 = 0
Step 3: Factor out 3: 3(x² - 4x + 3) = 0
Step 4: Factor quadratic: 3(x - 1)(x - 3) = 0
Step 5: Solve: x - 1 = 0 or x - 3 = 0
Step 6: Critical points: x = 1 and x = 3
Final Answer: Critical points at x = 1 and x = 3""",
        "topic": "calculus",
        "difficulty": "intermediate",
        "source": "curated"
    }
]

# Combine all problems
ALL_CURATED_PROBLEMS = CURATED_MATH_PROBLEMS + ALGEBRA_PROBLEMS + CALCULUS_PROBLEMS
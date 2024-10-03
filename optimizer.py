import sys
import numpy as np
from scipy.optimize import minimize
import time
import random
from external.build.bin import automata_bindings
from itertools import combinations, product

# Define two polynomials

# Create monomials for P(x, y)
monomials_A = [
    automata_bindings.Monomial(1, [2, 0]),  # x^2
    automata_bindings.Monomial(2, [1, 1]),  # 2xy
    automata_bindings.Monomial(1, [0, 2]),  # y^2
]

# Create monomials for Q(x, y)
monomials_B = [
    automata_bindings.Monomial(1, [3, 0]),  # x^3
    automata_bindings.Monomial(1, [0, 3]),  # y^3
]

# Create polynomials from monomials
A = automata_bindings.MultivariablePolynomial(monomials_A)
B = automata_bindings.MultivariablePolynomial(monomials_B).pow(2)

# Perform polynomial multiplication
product_poly = A * B
# print("\nProduct polynomial is")
# product_poly.print()
# print()

# Determine the maximum degree for the variables x and y
max_x_degree = max([mon.exponents[0] for mon in product_poly.monomialVec])
max_y_degree = max([mon.exponents[1] for mon in product_poly.monomialVec])

# Generate all possible monomials for the given degrees
all_possible_monomials = [automata_bindings.Monomial(1, [i, j])
                          for i, j in product(range(max_x_degree + 1), range(max_y_degree + 1))]

# print("All possible monomials are: \n")
# for monomial in all_possible_monomials:
#     monomial.print()
#     print()
#     sys.stdout.flush()
# time.sleep(2)
        
# Excellent results
best_result = None
best_polynomial = None
divisors = []

# Define a function to perform optimization for a given set of monomials
def optimize_for_monomials(selected_poly):
    # Define bounds for the coefficients
    bounds = [(1e-06, 10)] * len(selected_poly.monomialVec)
    # Initial guess (you might want to adjust this based on your problem)
    x0 = [0.1* random.random()] * len(selected_poly.monomialVec) 

    # Define your black-box function
    def blackbox_function(X):
        # Create new polynomial
        divisor_poly = automata_bindings.MultivariablePolynomial(selected_poly)

        # Modify coefficients with new guess
        for i, coefficient in enumerate(X):
            divisor_poly.monomialVec[i].coefficient = coefficient

        try:
            _, remainder = product_poly / divisor_poly
        except RuntimeError as e:
            # print(e)
            # Return terrible result
            return np.finfo(np.float64).max

        # Calculate Norm of coefficients vector
        rem_coeff_vec = [mon.coefficient**2 for mon in remainder.monomialVec]
        norm = np.linalg.norm(rem_coeff_vec)

        return norm

    # Generate 100 candidates and check if their objective values variance is null: flat function, quit
    candidate_values = []
    for _ in range(100):
        # Create polynomial with random-modified coefficients
        random_coeffs = np.random.uniform(1e-06, 10, len(selected_poly.monomialVec))
        
        # Calculate objective
        objective_value = blackbox_function(random_coeffs)
        candidate_values.append(objective_value)

    # Calculate variance
    variance = np.var(candidate_values)
    if variance < 1e-5:  # You can adjust this threshold
        # print("Objective function appears to be flat based on random sampling. Skipping optimization.")
        return None
    
    # Perform optimization using L-BFGS
    try:
        # Call minimize
        result = minimize(blackbox_function, x0, method='L-BFGS-B', bounds=bounds)

        if result.fun <= 1e-10:
            global best_result, best_polynomial
            
            # Best obj value
            best_result = 0.0
            
            # Copy constructor
            best_polynomial = automata_bindings.MultivariablePolynomial(selected_poly)
            # Assign best coefficients
            for i, coefficient in enumerate(result.x):
                best_polynomial.monomialVec[i].coefficient = coefficient

            divisors.append(best_polynomial)

            # print("\nFound an exact divisor in ")
            # best_polynomial.print()
            # print()

        return result
    
    except Exception as e:
        # print(f"Optimization failed for polynomial: ")
        # selected_poly.print()
        # print(f"with error: {e}")
        return None


# Generate all possible subsets of monomials
# for r in range(1, len(all_possible_monomials) + 1):
# for r in range(1, len(product_poly.monomialVec) + 1):
for r in range(1, 3):
    print(f"\n\nProcessing subsets of size {r}...\n\n")

    for my_poly in combinations(all_possible_monomials, r):
        # Copy constructor
        my_poly = automata_bindings.MultivariablePolynomial(my_poly)

        # Solution
        # if my_poly == automata_bindings.MultivariablePolynomial(
        #     [
        #     automata_bindings.Monomial(1, [3, 0]),  # 1
        #     automata_bindings.Monomial(1, [0, 3])   # x
        #     ]
        # ):
        #     breakpoint()

        # print(f"Optimizing for polynomial: ")
        # my_poly.print()

        # Perform optimization
        result = optimize_for_monomials(my_poly)

        # In case of crash or early termination, print message
        if result is None or not result.success:
            # print("Done with combination: ")
            # my_poly.print()
            # print(f"due to {result.message if result is not None else 'None result'}.\n")
            continue
        
        # print(f"Result: {result.fun}\n")

# Perform final analysis
print("Divisors are (molteplicity of 1)\n")
for divisor in divisors:
    divisor.print()
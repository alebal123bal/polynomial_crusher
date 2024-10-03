# polynomial_crusher
Factorize a multivariate polynomial using optimization techniques.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Install Python Dependencies](#2-install-python-dependencies)
  - [3. Compile `automata_bindings` C++ Module](#3-compile-automata_bindings-c++-module)
- [Usage](#usage)
  - [Running the Script](#running-the-script)
- [Understanding the Script](#understanding-the-script)
  - [Polynomial Definitions](#polynomial-definitions)
  - [Optimization Function](#optimization-function)
  - [Divisor Identification](#divisor-identification)
- [Example](#example)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project provides a Python script for dividing multivariate polynomials and identifying their divisors. Leveraging both Python's scientific computing capabilities and a C++ backend (`automata_bindings`), the script performs polynomial division and minimizes the remainder to find divisors of a given polynomial.

## Features

- **Multivariate Polynomial Operations:** Define and manipulate polynomials in multiple variables.
- **Divisor Identification:** Systematically search for and identify divisors of a given multivariate polynomial.
- **Optimization Integration:** Employ SciPy's optimization tools to minimize the remainder during polynomial division.
- **C++ Performance:** Use a C++ compiled module (`automata_bindings`) for efficient polynomial computations.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Operating System:** Linux
- **Python:** Version 3.6 or higher
- **C++ Compiler:** Compatible with your system (e.g., `g++`, `clang++`, or MSVC)
- **Required Python Packages:**
  - `numpy`
  - `scipy`
- **Additional Tools:**
  - `pybind11` (if used for compiling C++ bindings)
  - `cmake` (optional, based on build system)

## Installation

### 1. Clone the Repository

First, clone this repository to your local machine:

```bash
git clone https://github.com/alebal123bal/polynomial_crusher.git
cd polynomial_crusher
```

### 2. Install Python Dependencies

It's recommended to use a virtual environment to manage dependencies.

**Using `venv`:**

```bash
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install --upgrade pip
pip install numpy scipy
```

### 3. Compile `automata_bindings` C++ Module

The `automata_bindings` module is a C++ extension that needs to be compiled before use. Follow these steps to compile it:

1. **Navigate to the C++ Directory:**

   ```bash
   cd automata_bindings
   ```

2. **Install `pybind11` (if not already installed):**

   ```bash
   pip install pybind11
   ```

3. **Compile the Module:**

   Ensure you have a compatible C++ compiler installed and CMake too. Then, compile the module using the following command (modify paths and flags as necessary for your environment):

   ```bash
   mkdir ./external/build
   cd ./external/build
   cmake ..
   make
   ```

   **Notes:**
   - The command above assumes you're using `pybind11` for Python bindings. Adjust the compilation command based on the actual setup of `automata_bindings`.
   - Ensure that all necessary source files (`automata_bindings.cpp` and any dependencies) are present in the `automata_bindings` directory.

4. **Verify Compilation:**

   After successful compilation, a shared object file e.g. `automata_bindings.so` on Linux should be present in the `external/build/bin` directory.

5. **Navigate Back:**

   ```bash
   cd ..
   cd ..
   ```

## Usage

### Running the Script

Ensure you are in the root directory of the project and your virtual environment is activated.

```bash
python optimizer.py
```

Upon execution, the script will:

1. **Define Two Polynomials:**
   - Polynomial A: \( x^2 + 2xy + y^2 \)
   - Polynomial B: \( (x^3 + y^3)^{10} \)

2. **Multiply the Polynomials:**
   - Computes the product \( A \times B \).

3. **Generate Monomials:**
   - Creates all possible monomials up to the maximum degree in each variable present in the product.

4. **Optimize for Divisors:**
   - Searches through subsets of monomials to identify potential divisors by minimizing the remainder of division.

5. **Output Found Divisors:**
   - Prints the divisors with multiplicity one.

## Understanding the Script

### Polynomial Definitions

```python
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
B = automata_bindings.MultivariablePolynomial(monomials_B)
```

- **Monomials:** Individual terms of a polynomial defined by their coefficients and exponents.
- **Polynomials A and B:** Constructed from their respective monomials.

### Optimization Function

```python
def optimize_for_monomials(selected_poly):
    # Define bounds for the coefficients
    bounds = [(1e-06, 10)] * len(selected_poly.monomialVec)
    # Initial guess (you might want to adjust this based on your problem)
    x0 = [0.1 * random.random()] * len(selected_poly.monomialVec)

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
        # Skip optimization if the function appears flat
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

            return result

    except Exception as e:
        # Optimization failed
        return None
```

- **Purpose:** Finds coefficients for a selected set of monomials that best divide the `product_poly` by minimizing the norm of the remainder.
- **Process:**
  - Sets bounds and initial guesses for coefficients.
  - Defines a black-box function that performs division and computes the norm of the remainder.
  - Samples random candidates to check if the objective function is not flat.
  - Uses SciPy's `minimize` with the L-BFGS-B method to find optimal coefficients.
  - If an exact divisor is found (remainder norm ≤ \(1 \times 10^{-10}\)), it is recorded.

### Divisor Identification

```python
# Generate all possible subsets of monomials
for r in range(1, 3):
    print(f"\n\nProcessing subsets of size {r}...\n\n")

    for my_poly in combinations(all_possible_monomials, r):
        # Copy constructor
        my_poly = automata_bindings.MultivariablePolynomial(my_poly)

        # Perform optimization
        result = optimize_for_monomials(my_poly)

        # In case of crash or early termination, continue
        if result is None or not result.success:
            continue

# Perform final analysis
print("Divisors are (multiplicity of 1)\n")
for divisor in divisors:
    divisor.print()
```

- **Subsets Generation:** Iterates through all possible combinations of monomials of size 1 and 2.
- **Optimization:** Attempts to find if each subset can be a divisor of the `product_poly`.
- **Result Compilation:** Collects all successful divisors found during the optimization.

## Example

Upon running the script, you might see output similar to:

```
Processing subsets of size 1...


Processing subsets of size 2...


Divisors are (multiplicity of 1)

[Divisor Polynomial Details]
```

Each divisor polynomial will be printed using the `print()` method defined in the `automata_bindings` module, displaying its monomials and coefficients.

## Troubleshooting

- **`automata_bindings` Module Not Found:**
  - Ensure that the C++ module is correctly compiled and the shared object/PYD file is located in the `external/build/bin` directory.

- **Compilation Errors:**
  - Check that you have a compatible C++ compiler installed.
  - Ensure all necessary source files and dependencies are present.
  - Verify that `pybind11` or any other binding tools required are correctly installed.

- **Optimization Failures:**
  - Adjust the bounds or initial guesses in the `optimize_for_monomials` function.
  - Ensure that the selected monomial subsets are valid divisors.

- **Runtime Errors During Division:**
  - Make sure that the division operation is properly handled in the C++ module.

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**
2. **Create a New Branch**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Commit Your Changes**

   ```bash
   git commit -m "Add Your Feature"
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/YourFeature
   ```

5. **Open a Pull Request**

Ensure that your contributions adhere to the project's coding standards and include appropriate tests and documentation.

## License

This project is licensed under the [MIT License](LICENSE).

---

**Note:** 
def is_prime(n: int) -> bool:
    """
    Determine whether a given integer is a prime number.

    Parameters:
    n (int): The number to check.

    Returns:
    bool: True if n is prime, False otherwise.
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
        
    return True

if __name__ == "__main__":
    # Automatic demonstration
    test_numbers = [-5, 0, 1, 2, 3, 4, 17, 18, 97, 100]
    print("Demonstration of is_prime:")
    for num in test_numbers:
        print(f"{num} is prime? {is_prime(num)}")

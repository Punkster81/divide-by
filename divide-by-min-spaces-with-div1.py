import time

def generate_all_products(max_product=800, include_overflow=True):
    """
    Generate all possible products from {10,4,3,2} up to max_product
    Constraints:
    - Max 2 tens, then can add other numbers (up to 4 total)
    - Max 3 fours, then can add other numbers (up to 4 total)
    - Max 3 threes, then can add other numbers (up to 4 total)  
    - Max 4 twos (up to 4 total)1
    - ABSOLUTE MAX 4 numbers per group (including overflow)
    
    With overflow: extra numbers beyond limits act as *1 (cost 1 space each)
    """
    products = {}
    
    max_overflow = 2 if include_overflow else 0  # Allow up to 2 overflow numbers
    
    for count_10 in range(3 + max_overflow):
        for count_4 in range(4 + max_overflow):
            for count_3 in range(4 + max_overflow):
                for count_2 in range(5):  # Max 4 twos total (can't overflow since group size is 4)
                    combo = [10]*count_10 + [4]*count_4 + [3]*count_3 + [2]*count_2
                    
                    if not combo:
                        continue
                    
                    # ABSOLUTE MAX: 4 numbers total in a group
                    if len(combo) > 4:
                        continue
                    
                    # Calculate overflow
                    overflow_10 = max(0, count_10 - 2)
                    overflow_4 = max(0, count_4 - 3)
                    overflow_3 = max(0, count_3 - 3)
                    overflow_2 = max(0, count_2 - 4)
                    total_overflow = overflow_10 + overflow_4 + overflow_3 + overflow_2
                    
                    # Limit total overflow
                    if total_overflow > max_overflow:
                        continue
                    
                    # Calculate actual product
                    product = 1
                    product *= (10 ** min(count_10, 2))
                    product *= (4 ** min(count_4, 3))
                    product *= (3 ** min(count_3, 3))
                    product *= (2 ** min(count_2, 4))
                    # Overflow numbers multiply by 1 (don't change product)
                    
                    if product > max_product:
                        continue
                    
                    # Store with overflow info
                    if product not in products:
                        products[product] = []
                    products[product].append((combo, total_overflow))
    
    return products

def find_best_groups(target, products):
    """
    Find the best way to sum to target using products
    Returns: (groups, total_spaces_for_numbers, has_overflow) or None
    """
    if target == 0:
        return [], 0, False
    
    if target < 0:
        return None
    
    # dp[i] = (groups, spaces_for_numbers, has_any_overflow)
    dp = [None] * (target + 1)
    dp[0] = ([], 0, False)
    
    for i in range(1, target + 1):
        best = None
        best_spaces = float('inf')
        
        for product, combo_list in products.items():
            if product > i:
                continue
            
            prev = dp[i - product]
            if prev is None:
                continue
            
            prev_groups, prev_spaces, prev_overflow = prev
            
            # Try each combo for this product
            for combo, overflow_count in combo_list:
                # Calculate spaces: regular numbers + overflow (1 space each)
                new_spaces = prev_spaces + len(combo)
                
                if new_spaces < best_spaces:
                    best_spaces = new_spaces
                    best = (prev_groups + [(combo, overflow_count)], new_spaces, prev_overflow or overflow_count > 0)
        
        dp[i] = best
    
    if dp[target] is None:
        return None
    
    return dp[target]

def calculate_spaces(main_groups, outside_multiplier, outside_addition, skip_plus_one):
    """
    Calculate total spaces used:
    - Each number from set = 1 space
    - Overflow numbers = 1 space each
    - Each + between groups = 1 space
    - +1 at end = 1 space (just the +, the 1 doesn't count) - unless skipped due to overflow
    - Outside multiplier = its value in spaces
    - "eye" = 1 space (if iteration canceling wasn't used)
    - Outside addition = its value in spaces
    """
    spaces = 0
    
    # Count numbers in groups
    for combo, overflow in main_groups:
        spaces += len(combo)
    
    # Count + signs between groups
    if len(main_groups) > 1:
        spaces += len(main_groups) - 1
    
    # Add cost of +1 if not skipped (just the + sign, not the 1)
    if not skip_plus_one:
        spaces += 1
    
    # Outside multiplier
    spaces += outside_multiplier
    
    # "eye" space (if iteration canceling wasn't used)
    if not skip_plus_one:
        spaces += 1
    
    # Outside addition
    spaces += outside_addition
    
    return spaces

def find_best_decomposition(target):
    """
    Find the best decomposition optimizing for minimum spaces
    Format: ((groups) + 1) * outside_multiplier + outside_addition
    Or: ((groups)) * outside_multiplier + outside_addition (if single group with overflow)
    """

    start_time = time.time()

    products = generate_all_products()
    
    best_result = None
    best_spaces = float('inf')
    
    for outside_mult in range(1, min(target + 1, 1000)):
        for outside_add in range(0, min(target, 1000)):
            base = target - outside_add
            
            if base <= 0 or base % outside_mult != 0:
                continue
            
            quotient = base // outside_mult
            
            # Case 1: Single group with overflow (no +1 needed)
            # target = ((product)) * outside_mult + outside_add
            inner_target_no_plus = quotient
            
            if inner_target_no_plus >= 0 and inner_target_no_plus in products:
                for combo, overflow_count in products[inner_target_no_plus]:
                    # Only valid if single group with overflow
                    if overflow_count > 0:
                        main_groups = [(combo, overflow_count)]
                        spaces = calculate_spaces(main_groups, outside_mult, outside_add, True)
                        
                        if spaces < best_spaces:
                            best_spaces = spaces
                            best_result = (main_groups, outside_mult, outside_add, True)
            
            # Case 2: Normal decomposition with +1
            inner_target = quotient - 1
            
            if inner_target >= 0:
                result = find_best_groups(inner_target, products)
                
                if result is not None:
                    main_groups, _, has_overflow = result
                    spaces = calculate_spaces(main_groups, outside_mult, outside_add, False)
                    
                    if spaces < best_spaces:
                        best_spaces = spaces
                        best_result = (main_groups, outside_mult, outside_add, False)

    end_time = time.time()
    print(f"Time taken for decomposition: {end_time - start_time} seconds")

    return best_result, best_spaces if best_result else (None, None)

def format_output(main_groups, outside_multiplier, outside_addition, skip_plus_one):

    
    """Format the result as a string"""
    group_strs = []
    for combo, overflow in main_groups:
        group_str = "*".join(map(str, combo))
        group_strs.append(f"({group_str})")
    
    # Build inner expression with (trigger) between groups
    if skip_plus_one:
        inner = "(trigger)".join(group_strs)
    else:
        # Add groups with (trigger) between them, then add the plus one
        if len(group_strs) > 0:
            inner = "(trigger)".join(group_strs) + "(trigger)(plus one free cast of modifier)"
        else:
            inner = "(plus one free cast of modifiers)"
    
    result = f"((({inner})))"
    
    # Add outside multiplier info
    result += f" * (number of modifiers: {outside_multiplier})"
    
    # "eye" appears if iteration canceling wasn't used
    if not skip_plus_one:
        result += " (eye)"
    
    # Add outside addition if present
    if outside_addition > 0:
        result += f" (extra outside multipliers: {outside_addition})"
    
    return result

# Main program
target = int(input("Enter a number: "))

result, spaces = find_best_decomposition(target)

if result:
    main_groups, outside_mult, outside_add, skip_plus_one = result
    output = format_output(main_groups, outside_mult, outside_add, skip_plus_one)
    print(f"{target}: {output}")
    print(f"Total spaces used: {spaces}")
else:
    print(f"Could not decompose {target} with given constraints")

# Test with examples
print("\nTest with 312:")
result, spaces = find_best_decomposition(312)
if result:
    main_groups, outside_mult, outside_add, skip_plus_one = result
    output = format_output(main_groups, outside_mult, outside_add, skip_plus_one)
    print(f"312: {output}")
    print(f"Total spaces used: {spaces}")

print("\nTest with 517:")
result, spaces = find_best_decomposition(517)
if result:
    main_groups, outside_mult, outside_add, skip_plus_one = result
    output = format_output(main_groups, outside_mult, outside_add, skip_plus_one)
    print(f"517: {output}")
    print(f"Total spaces used: {spaces}")

print("\nTest with 2:")
result, spaces = find_best_decomposition(2)
if result:
    main_groups, outside_mult, outside_add, skip_plus_one = result
    output = format_output(main_groups, outside_mult, outside_add, skip_plus_one)
    print(f"2: {output}")
    print(f"Total spaces used: {spaces}")

print("\nTest with 8:")
result, spaces = find_best_decomposition(8)
if result:
    main_groups, outside_mult, outside_add, skip_plus_one = result
    output = format_output(main_groups, outside_mult, outside_add, skip_plus_one)
    print(f"8: {output}")
    print(f"Total spaces used: {spaces}")
def generate_all_products(max_product=800, include_overflow=True):
    """
    Generate all possible products from {10,4,3,2} up to max_product
    
    Two types of combinations:
    1. Normal: Follow hierarchy (max 2 tens, 3 fours, 3 threes, 4 twos)
    2. Overflow: Intentionally place numbers to cause overflow (*1 effect)
       - Can place 10/4/3 in positions where they overflow
       - Examples: (4,2,10), (3,3,10), (4,4,10), (10,10,4,10)
    """
    products = {}
    
    # Generate all possible 1-4 number combinations
    for length in range(1, 5):  # 1 to 4 numbers
        generate_combos_recursive([], length, products, max_product)
    
    return products

def generate_combos_recursive(current, remaining, products, max_product):
    """Recursively generate all valid combinations in descending order"""
    if remaining == 0:
        if not current:
            return
        
        # Calculate product and check for overflow
        combo = current[:]
        product, has_overflow = calculate_product_with_overflow(combo)
        
        if product > max_product:
            return
        
        if product not in products:
            products[product] = []
        
        # Store as tuple: (combo, overflow_count)
        overflow_count = 1 if has_overflow else 0
        products[product].append((combo, overflow_count))
        return
    
    # Determine what numbers we can add (must be <= last number to maintain descending order)
    if len(current) == 0:
        allowed = [10, 4, 3, 2]
    else:
        last_num = current[-1]
        allowed = [n for n in [10, 4, 3, 2] if n <= last_num]
    
    # Try adding each allowed number
    for num in allowed:
        new_combo = current + [num]
        
        # Check if this is a valid combination
        if is_valid_combo(new_combo):
            generate_combos_recursive(new_combo, remaining - 1, products, max_product)

def is_valid_combo(combo):
    """Check if a combo is valid (follows hierarchy or is valid overflow)"""
    if len(combo) > 4:
        return False
    
    count_10 = combo.count(10)
    count_4 = combo.count(4)
    count_3 = combo.count(3)
    count_2 = combo.count(2)
    
    # Count how many of each are in "normal" positions (before overflow)
    # The combo should be in descending order: 10s, then 4s, then 3s, then 2s
    # But we allow "wrong" placements that cause overflow
    
    # Basic limits
    if count_10 > 3:  # Max 2 normal + 1 overflow
        return False
    if count_4 > 4:
        return False
    if count_3 > 4:
        return False
    if count_2 > 4:
        return False
    
    return True

def calculate_product_with_overflow(combo):
    """
    Calculate the actual product considering overflow rules.
    Returns: (product, has_overflow)
    
    Rules:
    - First 2 tens multiply normally
    - First 3 fours multiply normally  
    - First 3 threes multiply normally
    - First 4 twos multiply normally
    - Additional numbers multiply by 1 (overflow)
    - 4th position (index 3): if it's a 10, 4, or 3, it overflows to *1
    """
    product = 1
    has_overflow = False
    
    count_10 = combo.count(10)
    count_4 = combo.count(4)
    count_3 = combo.count(3)
    count_2 = combo.count(2)
    
    # Check for standard overflow (too many of a number)
    if count_10 > 2:
        has_overflow = True
    if count_4 > 3:
        has_overflow = True
    if count_3 > 3:
        has_overflow = True
    if count_2 > 4:
        has_overflow = True
    
    # Check for positional overflow
    # Position 4 (index 3): if it's 10, 4, or 3, it overflows
    if len(combo) == 4 and combo[3] in [10, 4, 3]:
        has_overflow = True
        # This number doesn't contribute to product (it's *1)
        # Recalculate product without the last number if it overflows
        product_combo = combo[:3]  # First 3 numbers
        
        # Recalculate counts without overflow number
        count_10 = product_combo.count(10)
        count_4 = product_combo.count(4)
        count_3 = product_combo.count(3)
        count_2 = product_combo.count(2)
        
        product *= (10 ** min(count_10, 2))
        product *= (4 ** min(count_4, 3))
        product *= (3 ** min(count_3, 3))
        product *= (2 ** min(count_2, 4))
    else:
        # Normal calculation with standard overflow limits
        product *= (10 ** min(count_10, 2))
        product *= (4 ** min(count_4, 3))
        product *= (3 ** min(count_3, 3))
        product *= (2 ** min(count_2, 4))
    
    # Check if combo is not in proper descending order (indicates overflow)
    expected_order = [10]*count_10 + [4]*count_4 + [3]*count_3 + [2]*count_2
    if combo != expected_order and not has_overflow:
        has_overflow = True
    
    return product, has_overflow

def find_best_groups(target, products):
    """
    Find the best way to sum to target using products
    Returns: (groups, total_spaces_for_numbers, has_any_overflow) or None
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
    - Each (trigger) between groups = 1 space
    - +1 at end = 1 space (just the +) - unless skipped due to overflow
    - Outside multiplier = its value in spaces
    - (eye) = 1 space (if iteration canceling wasn't used)
    - Outside addition = its value in spaces
    """
    spaces = 0
    
    # Count numbers in groups
    for combo, overflow in main_groups:
        spaces += len(combo)
    
    # Count (trigger)s between groups
    if len(main_groups) > 1:
        spaces += len(main_groups) - 1
    
    # Add cost of +1 if not skipped (just the + sign)
    if not skip_plus_one:
        spaces += 1
    
    # Outside multiplier
    spaces += outside_multiplier
    
    # (eye) space (if iteration canceling wasn't used)
    if not skip_plus_one:
        spaces += 1
    
    # Outside addition
    spaces += outside_addition
    
    return spaces

def find_best_decomposition(target):
    """
    Find the best decomposition optimizing for minimum spaces
    """
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
            inner_target_no_plus = quotient
            
            if inner_target_no_plus >= 0 and inner_target_no_plus in products:
                for combo, overflow_count in products[inner_target_no_plus]:
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
    
    return best_result, best_spaces if best_result else (None, None)

def format_output(main_groups, outside_multiplier, outside_addition, skip_plus_one):
    """Format the result as a string"""
    group_strs = []
    for combo, overflow in main_groups:
        # Numbers should already be in descending order from generation
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
            inner = "(plus one free cast of modifier)"
    
    result = f"((({inner})))"
    
    # Add outside multiplier info
    result += f" * (number of modifiers:{outside_multiplier})"
    
    # (eye) appears if iteration canceling wasn't used
    if not skip_plus_one:
        result += " (eye)"
    
    # Add outside addition if present
    if outside_addition > 0:
        result += f" (extra outside multipliers (if exist):{outside_addition})"
    
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
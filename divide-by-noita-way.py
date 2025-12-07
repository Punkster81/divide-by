def generate_all_products(max_product=800, include_overflow=True):
    """
    Generate all possible products from {10,4,3,2} up to max_product
    
    Three types of combinations:
    1. Normal: Follow hierarchy (max 2 tens, 3 fours, 3 threes, 4 twos)
    2. Overflow: Intentionally place numbers to cause overflow (*1 effect)
    3. Draw Cancel: Place 10 in 3rd position or 10/4/3 in 4th position
    """
    products = {}
    
    # Generate all possible 1-4 number combinations (descending order)
    for length in range(1, 5):
        generate_combos_recursive([], length, products, max_product)
    
    # Generate draw cancel combinations (non-descending order)
    generate_draw_cancel_combos(products, max_product)
    
    return products

def generate_draw_cancel_combos(products, max_product):
    """Generate specific draw cancel combinations that aren't in descending order"""
    numbers = [10, 4, 3, 2]
    
    # 3-element combos with 10 in 3rd position
    for i, n1 in enumerate(numbers):
        for j, n2 in enumerate(numbers):
            combo = [n1, n2, 10]
            if combo == sorted(combo, reverse=True):
                continue  # Already generated in normal recursion
            
            product, has_overflow, draw_cancel = calculate_product_with_overflow(combo)
            if product <= max_product and draw_cancel:
                if product not in products:
                    products[product] = []
                overflow_count = 1 if has_overflow else 0
                if (combo, overflow_count, draw_cancel) not in products[product]:
                    products[product].append((combo, overflow_count, draw_cancel))
    
    # 4-element combos with 10/4/3 in 4th position
    for i, n1 in enumerate(numbers):
        for j, n2 in enumerate(numbers):
            for k, n3 in enumerate(numbers):
                for last in [10, 4, 3]:  # Only these cause draw cancel in 4th position
                    combo = [n1, n2, n3, last]
                    if combo == sorted(combo, reverse=True):
                        continue  # Already generated in normal recursion
                    
                    product, has_overflow, draw_cancel = calculate_product_with_overflow(combo)
                    if product <= max_product and draw_cancel:
                        if product not in products:
                            products[product] = []
                        overflow_count = 1 if has_overflow else 0
                        if (combo, overflow_count, draw_cancel) not in products[product]:
                            products[product].append((combo, overflow_count, draw_cancel))

def generate_combos_recursive(current, remaining, products, max_product):
    """Recursively generate all valid combinations in descending order"""
    if remaining == 0:
        if not current:
            return
        
        # Calculate product and check for overflow/draw cancel
        combo = current[:]
        product, has_overflow, draw_cancel = calculate_product_with_overflow(combo)
        
        if product > max_product:
            return
        
        if product not in products:
            products[product] = []
        
        # Store as tuple: (combo, overflow_count, draw_cancel)
        overflow_count = 1 if has_overflow else 0
        products[product].append((combo, overflow_count, draw_cancel))
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

def check_draw_cancel(combo):
    """
    Check if combo causes draw canceling.
    Draw canceling occurs when:
    - 10 is in the 3rd position (index 2)
    - 10, 4, or 3 is in the 4th position (index 3)
    
    Draw canceling prevents the need for ADD_TRIGGER + BLOOD_MAGIC combo
    """
    if len(combo) >= 3 and combo[2] == 10:
        return True
    if len(combo) == 4 and combo[3] in [10, 4, 3]:
        return True
    return False

def calculate_product_with_overflow(combo):
    """
    Calculate the actual product considering overflow rules.
    Returns: (product, has_overflow, has_draw_cancel)
    
    For draw cancel combos (not in descending order), calculate based on
    the actual positions that multiply before the draw cancel position.
    
    Rules:
    - First 2 tens multiply normally
    - First 3 fours multiply normally  
    - First 3 threes multiply normally
    - First 4 twos multiply normally
    - Additional numbers multiply by 1 (overflow)
    - Draw cancel: 10 in 3rd pos OR 10/4/3 in 4th pos stops execution
    """
    product = 1
    has_overflow = False
    draw_cancel = check_draw_cancel(combo)
    
    # For draw cancel combos, only count numbers BEFORE the draw cancel position
    if draw_cancel:
        if len(combo) >= 3 and combo[2] == 10:
            # 10 in 3rd position - only first 2 numbers multiply
            effective_combo = combo[:2]
        elif len(combo) == 4 and combo[3] in [10, 4, 3]:
            # Draw cancel in 4th position - only first 3 numbers multiply
            effective_combo = combo[:3]
        else:
            effective_combo = combo
        
        # Count each number type in the effective combo
        count_10 = effective_combo.count(10)
        count_4 = effective_combo.count(4)
        count_3 = effective_combo.count(3)
        count_2 = effective_combo.count(2)
        
        # Apply normal multiplication rules to effective combo
        product *= (10 ** min(count_10, 2))
        product *= (4 ** min(count_4, 3))
        product *= (3 ** min(count_3, 3))
        product *= (2 ** min(count_2, 4))
        
        return product, has_overflow, draw_cancel
    
    # Non-draw-cancel combos use original logic
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
        product_combo = combo[:3]
        
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
    
    return product, has_overflow, draw_cancel

def find_best_groups(target, products):
    """
    Find the best way to sum to target using products
    Returns: (groups, total_spaces_for_numbers, has_any_overflow, has_any_draw_cancel) or None
    """
    if target == 0:
        return [], 0, False, False
    
    if target < 0:
        return None
    
    # dp[i] = (groups, spaces_for_numbers, has_any_overflow, has_any_draw_cancel)
    dp = [None] * (target + 1)
    dp[0] = ([], 0, False, False)
    
    for i in range(1, target + 1):
        best = None
        best_spaces = float('inf')
        
        for product, combo_list in products.items():
            if product > i:
                continue
            
            prev = dp[i - product]
            if prev is None:
                continue
            
            prev_groups, prev_spaces, prev_overflow, prev_draw_cancel = prev
            
            # Try each combo for this product
            for combo, overflow_count, draw_cancel in combo_list:
                new_spaces = prev_spaces + len(combo)
                
                if new_spaces < best_spaces:
                    best_spaces = new_spaces
                    best = (
                        prev_groups + [(combo, overflow_count, draw_cancel)], 
                        new_spaces, 
                        prev_overflow or overflow_count > 0,
                        prev_draw_cancel or draw_cancel
                    )
        
        dp[i] = best
    
    if dp[target] is None:
        return None
    
    return dp[target]

def calculate_spaces(main_groups, outside_multiplier, outside_addition, skip_plus_one):
    """
    Calculate total spaces used:
    - Each number from set = 1 space
    - Each (trigger) between groups = 1 space
    - +1 at end = 1 space (just the +) - unless skipped due to overflow or draw cancel
    - Outside multiplier = its value in spaces
    - (eye) = 1 space (if iteration canceling wasn't used AND no draw cancel)
    - Outside addition = its value in spaces
    """
    spaces = 0
    
    # Count numbers in groups
    for combo, overflow, draw_cancel in main_groups:
        spaces += len(combo)
    
    # Count (trigger)s between groups
    if len(main_groups) > 1:
        spaces += len(main_groups) - 1
    
    # Add cost of +1 if not skipped (just the + sign)
    if not skip_plus_one:
        spaces += 1
    
    # Outside multiplier
    spaces += outside_multiplier
    
    # (eye) space (if iteration canceling wasn't used AND no draw cancel)
    # Draw cancel eliminates the need for ADD_TRIGGER + BLOOD_MAGIC
    has_draw_cancel = any(dc for _, _, dc in main_groups)
    if not skip_plus_one and not has_draw_cancel:
        spaces += 1
    
    # Outside addition
    spaces += outside_addition
    
    return spaces

def find_best_decomposition(target):
    """
    Find the best decomposition optimizing for minimum spaces
    """
    # Special case: for 1-4 modifiers, just use that many modifiers directly
    if target <= 4:
        return ([], 0, target, True), target
    
    products = generate_all_products()
    
    best_result = None
    best_spaces = float('inf')
    
    for outside_mult in range(1, min(target + 1, 1000)):
        for outside_add in range(0, min(target, 1000)):
            base = target - outside_add
            
            if base <= 0 or base % outside_mult != 0:
                continue
            
            quotient = base // outside_mult
            
            # Case 1: Single group with overflow or draw cancel (no +1 needed)
            inner_target_no_plus = quotient
            
            if inner_target_no_plus >= 0 and inner_target_no_plus in products:
                for combo, overflow_count, draw_cancel in products[inner_target_no_plus]:
                    if overflow_count > 0 or draw_cancel:
                        main_groups = [(combo, overflow_count, draw_cancel)]
                        spaces = calculate_spaces(main_groups, outside_mult, outside_add, True)
                        
                        if spaces < best_spaces:
                            best_spaces = spaces
                            best_result = (main_groups, outside_mult, outside_add, True)
            
            # Case 2: Normal decomposition with +1
            inner_target = quotient - 1
            
            if inner_target >= 0:
                result = find_best_groups(inner_target, products)
                
                if result is not None:
                    main_groups, _, has_overflow, has_draw_cancel = result
                    spaces = calculate_spaces(main_groups, outside_mult, outside_add, False)
                    
                    if spaces < best_spaces:
                        best_spaces = spaces
                        best_result = (main_groups, outside_mult, outside_add, False)
    
    return best_result, best_spaces if best_result else (None, None)

def format_spell_ids(main_groups, outside_multiplier, outside_addition, skip_plus_one):
    """Format the result as comma-separated spell IDs"""
    # Spell ID mapping
    spell_map = {
        10: "DIVIDE_10",
        4: "DIVIDE_4",
        3: "DIVIDE_3",
        2: "DIVIDE_2"
    }
    
    spells = []
    
    # Special case: if no main groups, just output modifiers
    if len(main_groups) == 0:
        # Just output all modifiers (outside_addition only)
        for _ in range(outside_addition):
            spells.append("modifier")
        return ",".join(spells)
    
    # Check if any group has draw cancel
    has_draw_cancel = any(dc for _, _, dc in main_groups)
    
    # Build the divide chain groups
    for i, (combo, overflow, draw_cancel) in enumerate(main_groups):
        # Add divide by spells in descending order
        for num in combo:
            spells.append(spell_map[num])
        
        # Add trigger between groups (but not after the last group)
        if i < len(main_groups) - 1:
            spells.append("ADD_TRIGGER")
    
    # Add trigger at the end if we have groups and no draw cancel
    if len(main_groups) > 0 and not has_draw_cancel:
        spells.append("ADD_TRIGGER")
    
    # Add modifiers (repeated outside_multiplier times)
    for _ in range(outside_multiplier):
        spells.append("modifier")
    
    # Add Blood Magic only if:
    # - iteration canceling wasn't used (skip_plus_one is False)
    # - AND there's no draw cancel
    if not skip_plus_one and not has_draw_cancel:
        spells.append("BLOOD_MAGIC")
    
    # Add additional modifiers for outside addition
    for _ in range(outside_addition):
        spells.append("modifier")
    
    return ",".join(spells)

# Main program
if __name__ == "__main__":
    target = int(input("Enter number of modifier copies desired: "))
    
    result, spaces = find_best_decomposition(target)
    
    if result:
        main_groups, outside_mult, outside_add, skip_plus_one = result
        spell_list = format_spell_ids(main_groups, outside_mult, outside_add, skip_plus_one)
        
        # Check if draw cancel is being used
        has_draw_cancel = any(dc for _, _, dc in main_groups) if main_groups else False
        
        print(f"\nTarget: {target} modifier copies")
        print(f"Spell IDs (comma-separated):")
        print(spell_list)
        print(f"\nTotal wand slots used: {spaces}")
        
        if main_groups:
            print(f"\nBreakdown:")
            print(f"  - Divide By chain groups: {[(combo, 'draw_cancel' if dc else ('overflow' if ov else 'normal')) for combo, ov, dc in main_groups]}")
            print(f"  - Modifiers before Blood Magic: {outside_mult}")
            print(f"  - Draw cancel used: {has_draw_cancel}")
            print(f"  - Blood Magic used: {not skip_plus_one and not has_draw_cancel}")
            print(f"  - Additional modifiers after: {outside_add}")
        else:
            print(f"\nBreakdown: Simple case - just {outside_add} modifiers")
    else:
        print(f"Could not find a solution for {target} modifier copies")
    
    # Test with examples
    print("\n" + "="*60)
    print("Test with 312 modifier copies:")
    result, spaces = find_best_decomposition(312)
    if result:
        main_groups, outside_mult, outside_add, skip_plus_one = result
        spell_list = format_spell_ids(main_groups, outside_mult, outside_add, skip_plus_one)
        print(spell_list)
        print(f"Wand slots used: {spaces}")
    
    print("\n" + "="*60)
    print("Test with 517 modifier copies:")
    result, spaces = find_best_decomposition(517)
    if result:
        main_groups, outside_mult, outside_add, skip_plus_one = result
        spell_list = format_spell_ids(main_groups, outside_mult, outside_add, skip_plus_one)
        print(spell_list)
        print(f"Wand slots used: {spaces}")

    print("\n" + "="*60)
    print("Test with 8 modifier copies:")
    result, spaces = find_best_decomposition(8)
    if result:
        main_groups, outside_mult, outside_add, skip_plus_one = result
        spell_list = format_spell_ids(main_groups, outside_mult, outside_add, skip_plus_one)
        print(spell_list)
        print(f"Wand slots used: {spaces}")
    
    print("\n" + "="*60)
    print("Test with 5 modifier copies:")
    result, spaces = find_best_decomposition(5)
    if result:
        main_groups, outside_mult, outside_add, skip_plus_one = result
        spell_list = format_spell_ids(main_groups, outside_mult, outside_add, skip_plus_one)
        print(spell_list)
        print(f"Wand slots used: {spaces}")
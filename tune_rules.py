import numpy as np

def simulate(width=50, height=50, steps=100, seed=42, 
             zombie_survival_min=4, zombie_survival_max=7,
             infection_threshold=1,
             cure_threshold=2):
    
    np.random.seed(seed)
    current_field = np.zeros((height, width), dtype=int)
    entrp = seed % 10000
    if entrp == 0: entrp = 1
    
    # Odd Columns Initialization
    for j in range(width):
        for i in range(height):
            if i != 0 and j != 0:
                if entrp % i == 0 or entrp % j == 0:
                    current_field[i][j] = i % 3
                elif i > j and not (2 * i + j) % 4:
                    current_field[i][j] = 2
                elif j >= i: 
                     if j - i >= 0:
                        current_field[i][j-i] = 1
    
    for j in range(1, width, 2):
        for i in range(height):
            if (i + j + entrp) % 7 == 0:
                current_field[i][j] = 2
    
    history_green = []
    history_red = []
    history_coverage = []
    
    for step in range(steps):
        next_field = np.zeros_like(current_field)
        
        unique, counts = np.unique(current_field, return_counts=True)
        dist = dict(zip(unique, counts))
        total = width * height
        
        green = dist.get(1, 0)
        red = dist.get(2, 0)
        cov = (green + red) / total
        
        history_green.append(green/total)
        history_red.append(red/total)
        history_coverage.append(cov)
        
        for y in range(height):
            for x in range(width):
                count = 0
                zombie_neighbors = 0
                green_neighbors = 0
                
                for j in range(y - 1, y + 2):
                    for i in range(x - 1, x + 2):
                        ny, nx = j % height, i % width
                        val = current_field[ny][nx]
                        if val != 0:
                            count += 1
                        if val == 2:
                            zombie_neighbors += 1
                        if val == 1:
                            green_neighbors += 1
                
                cell_value = current_field[y][x]
                
                if cell_value == 2:
                    count -= 1
                    zombie_neighbors -= 1
                    # Green neighbors don't include self
                    
                    # Cure Rule
                    if green_neighbors >= cure_threshold:
                        next_field[y][x] = 1
                    # Survival Rule
                    elif zombie_survival_min <= count <= zombie_survival_max:
                        next_field[y][x] = 2
                    else:
                        next_field[y][x] = 0
                
                else: # 0 or 1
                    if cell_value == 1:
                        count -= 1
                        green_neighbors -= 1
                    
                    # Infection Rule
                    if zombie_neighbors >= infection_threshold:
                        next_field[y][x] = 2
                    
                    # Normal Life Rule
                    elif cell_value == 1:
                        if count == 2 or count == 3:
                            next_field[y][x] = 1
                        else:
                            next_field[y][x] = 0
                    elif cell_value == 0:
                        if count == 3:
                            next_field[y][x] = 1
                        else:
                            next_field[y][x] = 0
                            
        current_field = next_field
        
    return history_coverage, history_green, history_red

print("Testing Cure Logic...")
print("-" * 50)

configs = [
    {"name": "Cure 1 (Inf>=1, Cure>=2, Surv 4-7)", "inf": 1, "cure": 2, "surv_min": 4, "surv_max": 7},
    {"name": "Cure 2 (Inf>=2, Cure>=2, Surv 4-7)", "inf": 2, "cure": 2, "surv_min": 4, "surv_max": 7},
    {"name": "Cure 3 (Inf>=1, Cure>=3, Surv 4-7)", "inf": 1, "cure": 3, "surv_min": 4, "surv_max": 7},
    {"name": "Cure 4 (Inf>=2, Cure>=1, Surv 4-7)", "inf": 2, "cure": 1, "surv_min": 4, "surv_max": 7},
]

for cfg in configs:
    cov, green, red = simulate(steps=100, 
                        zombie_survival_min=cfg["surv_min"],
                        zombie_survival_max=cfg["surv_max"],
                        infection_threshold=cfg["inf"],
                        cure_threshold=cfg["cure"])
    
    print(f"Config: {cfg['name']}")
    print(f"  Final Coverage: {cov[-1]*100:.1f}%")
    print(f"  Final Green: {green[-1]*100:.1f}%")
    print(f"  Final Red: {red[-1]*100:.1f}%")
    print("-" * 50)

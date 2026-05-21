import os
import pandas as pd
from datetime import datetime
import json

def save_test_results(results, nist_out, diehard_out, gen_name, w, h, seed):
    # Determine folder name
    if gen_name == "Game of Life":
        folder_name = f"{w}x{h}x{seed if seed is not None else 'random'}"
    elif gen_name == "File":
        folder_name = f"File_{w}" # w acts as filename
    else:
        folder_name = f"{gen_name.replace(' ', '_')}_{w}x{seed if seed is not None else 'random'}"
    
    base_dir = os.path.join(os.path.dirname(__file__), "test_results")
    res_dir = os.path.join(base_dir, folder_name)
    os.makedirs(res_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save NN and Stat results
    if results:
        # Bitwise NN
        if results.get('bitwise', {}).get('neural_network', {}).get('details'):
            df_nn = pd.DataFrame(results['bitwise']['neural_network']['details'])
            df_nn.to_csv(os.path.join(res_dir, f"bitwise_nn_{timestamp}.csv"), index=False)
            
        # Bitwise Stat
        if results.get('bitwise', {}).get('statistical', {}).get('details'):
            df_stat = pd.DataFrame(results['bitwise']['statistical']['details'])
            df_stat.to_csv(os.path.join(res_dir, f"bitwise_stat_{timestamp}.csv"), index=False)
            
        # Block NN
        if results.get('block', {}).get('neural_network', {}).get('details'):
            df_nn_b = pd.DataFrame(results['block']['neural_network']['details'])
            df_nn_b.to_csv(os.path.join(res_dir, f"blockwise_nn_{timestamp}.csv"), index=False)
            
        # Block Stat
        if results.get('block', {}).get('statistical', {}).get('details'):
            df_stat_b = pd.DataFrame(results['block']['statistical']['details'])
            df_stat_b.to_csv(os.path.join(res_dir, f"blockwise_stat_{timestamp}.csv"), index=False)
            
    # Save NIST
    if nist_out:
        with open(os.path.join(res_dir, f"nist_{timestamp}.txt"), 'w', encoding='utf-8') as f:
            f.write(nist_out)
            
    # Save Diehard
    if diehard_out:
        with open(os.path.join(res_dir, f"diehard_{timestamp}.txt"), 'w', encoding='utf-8') as f:
            if isinstance(diehard_out, dict):
                f.write(diehard_out.get('summary', ''))
                f.write("\n\n")
                f.write(str(diehard_out.get('details', '')))
            else:
                f.write(str(diehard_out))

    return res_dir

def save_mass_results(metrics, gen_name, iterations):
    base_dir = os.path.join(os.path.dirname(__file__), "mass_test_results")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{gen_name.replace(' ', '_')}_{iterations}iters_{timestamp}"
    res_dir = os.path.join(base_dir, folder_name)
    os.makedirs(res_dir, exist_ok=True)

    with open(os.path.join(res_dir, "mass_summary.json"), 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=4, ensure_ascii=False)
    
    # Save detailed DataFrames if collected
    if 'history' in metrics:
        history = metrics.pop('history')
        df_hist = pd.DataFrame(history)
        df_hist.to_csv(os.path.join(res_dir, "iterations_history.csv"), index=False)

    return res_dir

import sys
import os
import tempfile
import pandas as pd
from io import StringIO
import analysis
from save_utils import save_mass_results

def run_mass_verification(generator_class, gen_kwargs, iterations, window_sizes, use_nn_stat, use_nist, use_diehard, progress_callback=None):
    from stats.sp800_22_tests.sp800_22_tests import runrun
    from stats.DIEHARD.dieharder import run_dieharder

    metrics = {
        'iterations': iterations,
        'generator': generator_class.__name__,
        'nn_stat': {'bitwise_acc': [], 'bitwise_p': [], 'blockwise_acc': [], 'blockwise_p': []},
        'nist': {'pass_ratio': []},
        'diehard': {'pass_ratio': []},
        'history': []
    }

    for i in range(iterations):
        if progress_callback:
            progress_callback(i, iterations)
            
        # Generate sequence
        init_kwargs = {k: v for k, v in gen_kwargs.items() if k not in ['steps', 'extract_mode', 'length']}
        gen = generator_class(**init_kwargs)
        if hasattr(gen, 'current_field'): # Game of life
            steps = gen_kwargs.get('steps', 10)
            extract_mode = gen_kwargs.get('extract_mode', 'flatten')
            bit_string, _ = gen.generate(steps, extract_mode=extract_mode)
            if 'length' in gen_kwargs:
                bit_string = bit_string[:gen_kwargs['length']]
        else:
            bit_string = gen.generate(gen_kwargs.get('length', 20000))
            
        sequence = [int(b) for b in bit_string]
        
        iter_res = {'iteration': i + 1}
        
        if use_nn_stat:
            results = analysis.run_full_analysis(sequence, window_sizes)
            if results:
                # Accumulate
                b_acc = results['bitwise']['neural_network']['overall_accuracy']
                b_p = results['bitwise']['statistical']['overall_p_value']
                bl_acc = results['block']['neural_network']['overall_accuracy']
                bl_p = results['block']['statistical']['overall_p_value']
                
                metrics['nn_stat']['bitwise_acc'].append(b_acc)
                metrics['nn_stat']['bitwise_p'].append(b_p)
                metrics['nn_stat']['blockwise_acc'].append(bl_acc)
                metrics['nn_stat']['blockwise_p'].append(bl_p)
                
                iter_res['bitwise_acc'] = b_acc
                iter_res['bitwise_p'] = b_p
                iter_res['blockwise_acc'] = bl_acc
                iter_res['blockwise_p'] = bl_p
                
        if use_nist:
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
                tmp.write(bit_string)
                tmp_path = tmp.name
            try:
                old_stdout = sys.stdout
                sys.stdout = mystdout = StringIO()
                runrun(tmp_path)
                sys.stdout = old_stdout
                nist_output = mystdout.getvalue()
                
                if "SUMMARY" in nist_output:
                    summary_lines = nist_output.split("SUMMARY")[-1].strip().split('\n')
                    pass_count = sum(1 for line in summary_lines if "PASS" in line)
                    total = sum(1 for line in summary_lines if "PASS" in line or "FAIL" in line or "ERROR" in line)
                else:
                    pass_count = nist_output.count("PASS")
                    total = pass_count + nist_output.count("FAIL")
                ratio = pass_count / total if total > 0 else 0
                metrics['nist']['pass_ratio'].append(ratio)
                iter_res['nist_pass_ratio'] = ratio
            except Exception:
                sys.stdout = old_stdout
                metrics['nist']['pass_ratio'].append(0)
                iter_res['nist_pass_ratio'] = 0
            finally:
                os.unlink(tmp_path)
                
        if use_diehard:
            try:
                diehard_result = run_dieharder(bit_string)
                d_passed = diehard_result.get('passed', 0)
                d_total = diehard_result.get('total', 1)
                ratio = d_passed / d_total if d_total > 0 else 0
                metrics['diehard']['pass_ratio'].append(ratio)
                iter_res['diehard_pass_ratio'] = ratio
            except Exception:
                metrics['diehard']['pass_ratio'].append(0)
                iter_res['diehard_pass_ratio'] = 0
                
        metrics['history'].append(iter_res)
        
    if progress_callback:
        progress_callback(iterations, iterations)
        
    # Calculate averages
    def avg(lst): return sum(lst) / len(lst) if lst else 0
    
    final_metrics = {
        'iterations': iterations,
        'generator': generator_class.__name__,
        'nn_stat_averages': {
            'bitwise_acc': avg(metrics['nn_stat']['bitwise_acc']),
            'bitwise_p': avg(metrics['nn_stat']['bitwise_p']),
            'blockwise_acc': avg(metrics['nn_stat']['blockwise_acc']),
            'blockwise_p': avg(metrics['nn_stat']['blockwise_p'])
        },
        'nist_avg_pass_ratio': avg(metrics['nist']['pass_ratio']),
        'diehard_avg_pass_ratio': avg(metrics['diehard']['pass_ratio']),
        'history': metrics['history']
    }
    
    # Save to file
    res_dir = save_mass_results(final_metrics, generator_class.__name__, iterations)
    return final_metrics, res_dir

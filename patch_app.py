import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Main Sequence tests gathering
content = content.replace(
    'with st.spinner(T["analyzing"]):',
    'with st.spinner(T["analyzing"]):\n                results_data = None\n                nist_output_data = None\n                diehard_output_data = None',
    1 # only first occurrence
)

content = content.replace(
    'results = analysis.run_full_analysis(sequence, window_sizes)\n                    if results:',
    'results = analysis.run_full_analysis(sequence, window_sizes)\n                    results_data = results\n                    if results:',
    1
)

content = content.replace(
    'nist_output = mystdout.getvalue()\n                        st.text(nist_output)',
    'nist_output = mystdout.getvalue()\n                        nist_output_data = nist_output\n                        st.text(nist_output)',
    1
)

content = content.replace(
    'diehard_result = run_dieharder(bitstring)\n                        \n                        st.subheader(diehard_result[\'summary\'])',
    'diehard_result = run_dieharder(bitstring)\n                        diehard_output_data = diehard_result\n                        \n                        st.subheader(diehard_result[\'summary\'])',
    1
)

# Insert saving at the end of the main sequence test block
anchor1 = 'st.warning("Please upload the second file for Avalanche Test")'
replacement1 = anchor1 + '''
                
                if any([results_data, nist_output_data, diehard_output_data]):
                    try:
                        from save_utils import save_test_results
                        save_path = save_test_results(results_data, nist_output_data, diehard_output_data, "File", uploaded_file.name, 0, None)
                        st.success(f"💾 Results saved to {save_path}")
                    except Exception as e:
                        st.error(f"Error saving results: {e}")'''
content = content.replace(anchor1, replacement1, 1)

# 2. Generated Sequence tests gathering
# Look for the second occurrence of with st.spinner(T["analyzing"]):
content = content.replace(
    'with st.spinner(T["analyzing"]):',
    'with st.spinner(T["analyzing"]):\n            results_data = None\n            nist_output_data = None\n            diehard_output_data = None',
)
# We replaced both now. But the first one was already replaced, so it replaces the second one! Wait, the first one was already replaced so it won't match exactly. Let's see. The first one is now `with st.spinner(T["analyzing"]):\n                results_data = None...`. So `with st.spinner(T["analyzing"]):` (followed by newline) will only match the second one.

content = content.replace(
    'results = analysis.run_full_analysis(sequence, window_sizes)\n                if results:',
    'results = analysis.run_full_analysis(sequence, window_sizes)\n                results_data = results\n                if results:'
)

content = content.replace(
    'nist_output = mystdout.getvalue()\n                    st.text(nist_output)',
    'nist_output = mystdout.getvalue()\n                    nist_output_data = nist_output\n                    st.text(nist_output)'
)

content = content.replace(
    'diehard_result = run_dieharder(bitstring)\n                    st.subheader(diehard_result[\'summary\'])',
    'diehard_result = run_dieharder(bitstring)\n                    diehard_output_data = diehard_result\n                    st.subheader(diehard_result[\'summary\'])'
)

anchor2 = 'st.error(f"Diehard Error: {e}")'
replacement2 = anchor2 + '''
            
            if any([results_data, nist_output_data, diehard_output_data]):
                try:
                    from save_utils import save_test_results
                    gen_w = prng_width if selected_gen == "Game of Life" else gen_length
                    gen_h = prng_height if selected_gen == "Game of Life" else 0
                    s = seed_val if selected_gen == "Game of Life" else (seed_val if seed_val is not None else 0)
                    save_path = save_test_results(results_data, nist_output_data, diehard_output_data, selected_gen, gen_w, gen_h, s)
                    st.success(f"💾 Results saved to {save_path}")
                except Exception as e:
                    st.error(f"Error saving results: {e}")'''
content = content.replace(anchor2, replacement2, 1)

# 3. Add Mass Verification Section
mass_ver_code = '''

    # --- Mass Verification Section ---
    st.markdown("---")
    st.header("🔁 " + ("Массовая проверка" if lang_code == "ru" else "Mass Verification"))
    
    col_iter, col_run = st.columns([2, 1])
    with col_iter:
        mass_iterations = st.number_input("Iterations / Итерации", min_value=1, max_value=100000, value=100)
    with col_run:
        run_mass_btn = st.button("🚀 " + ("Запустить массовую проверку" if lang_code == "ru" else "Run Mass Verification"))

    if run_mass_btn:
        with st.spinner("Running Mass Verification..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(current, total):
                progress = min(current / total, 1.0)
                progress_bar.progress(progress)
                status_text.text(f"Iteration {current}/{total}")

            from mass_test import run_mass_verification
            
            gen_kwargs = {}
            if selected_gen == "Game of Life":
                gen_class = GameOfLifePRNG
                gen_kwargs = {
                    'width': prng_width,
                    'height': prng_height,
                    'seed': seed_val,
                    'boundary_mode': boundary_mode_key,
                    'extract_mode': extract_mode_key,
                    'steps': prng_steps
                }
            elif selected_gen == "BBS":
                gen_class = BBSGenerator
                gen_kwargs = {'seed': seed_val, 'length': gen_length}
            elif selected_gen == "AES (CTR)":
                gen_class = AESGenerator
                gen_kwargs = {'seed': seed_val, 'length': gen_length}
            elif selected_gen == "Magma (GOST)":
                gen_class = MagmaGenerator
                gen_kwargs = {'seed': seed_val, 'length': gen_length}
            elif selected_gen == "Kuznechik (GOST)":
                gen_class = KuznechikGenerator
                gen_kwargs = {'seed': seed_val, 'length': gen_length}
            elif selected_gen == "SM4":
                gen_class = SM4Generator
                gen_kwargs = {'seed': seed_val, 'length': gen_length}
            elif selected_gen == "Mersenne Twister (Weak)":
                gen_class = MersenneTwisterGenerator
                gen_kwargs = {'seed': seed_val, 'length': gen_length}
            elif selected_gen == "LFSR (Weak)":
                gen_class = LFSRGenerator
                gen_kwargs = {'seed': seed_val, 'length': gen_length}

            final_metrics, res_dir = run_mass_verification(
                generator_class=gen_class,
                gen_kwargs=gen_kwargs,
                iterations=mass_iterations,
                window_sizes=window_sizes,
                use_nn_stat=test_nn_stat_gen,
                use_nist=test_nist_gen,
                use_diehard=test_diehard_gen,
                progress_callback=update_progress
            )
            
            st.success(f"Mass verification completed! Results saved to {res_dir}")
            
            st.subheader("📊 Averages")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("NN Bitwise Acc", f"{final_metrics['nn_stat_averages']['bitwise_acc']:.2%}")
            col2.metric("Stat Bitwise P-Val", f"{final_metrics['nn_stat_averages']['bitwise_p']:.3f}")
            col3.metric("NIST Pass Ratio", f"{final_metrics['nist_avg_pass_ratio']:.2%}")
            col4.metric("Diehard Pass Ratio", f"{final_metrics['diehard_avg_pass_ratio']:.2%}")
'''
content = content + mass_ver_code

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Patching successful.")

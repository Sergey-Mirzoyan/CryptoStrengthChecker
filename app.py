import streamlit as st
import pandas as pd
import analysis
import avalanche
import os
import tempfile
import sys
import numpy as np
import time

# Add current directory to path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import external test modules
try:
    from stats.sp800_22_tests.sp800_22_tests import runrun
    from stats.DIEHARD.dieharder import run_dieharder
    # Import Generators
    from generators.game_of_life import GameOfLifePRNG
    from generators.bbs import BBSGenerator
    from generators.aes import AESGenerator
    from generators.magma import MagmaGenerator
    from generators.kuznechik import KuznechikGenerator
    from generators.sm4 import SM4Generator
    from generators.mersenne import MersenneTwisterGenerator
    from generators.lfsr import LFSRGenerator
except ImportError as e:
    st.error(f"Error importing modules: {e}")

st.set_page_config(
    page_title="Crypto Strength Checker",
    page_icon="🔒",
    layout="wide"
)

# Localization Dictionary
TRANS = {
    "en": {
        "title": "🔒 Cryptographic Strength Checker",
        "desc": "Analyze the cryptographic strength of binary sequences using various methods.",
        "config": "Configuration",
        "window_sizes": "Window Sizes (comma separated)",
        "upload_main": "Upload Binary File (Main Sequence)",
        "upload_second": "Upload Second File (for Avalanche Test)",
        "run_analysis": "Run Selected Tests",
        "success_load": "File loaded successfully! Length: {} bits",
        "error_file": "Invalid file content. Must be 0s and 1s.",
        "select_tests": "Select Tests to Run",
        "test_nn_stat": "Neural Network & Statistical (Chi-Square)",
        "test_nist": "NIST SP800-22",
        "test_diehard": "Diehard Tests",
        "test_avalanche": "Avalanche Test (Requires 2 files)",
        "results_nn": "🧠 Combined Assessment Method",
        "results_stat": "📊 Statistical Analysis (Chi-Square)",
        "results_nist": "📋 NIST SP800-22 Results",
        "results_diehard": "🎲 Diehard Results",
        "results_avalanche": "❄️ Avalanche Test Results",
        "strong": "STRONG",
        "weak": "WEAK",
        "inconclusive": "INCONCLUSIVE",
        "accuracy": "Accuracy",
        "p_value": "P-Value",
        "analyzed": "Analyzed Bits",
        "tests": "Tests",
        "tests_passed": "Tests Passed",
        "avalanche_ratio": "Avalanche Ratio",
        "ideal_ratio": "Ideal Ratio: 0.5 (50%)",
        "analyzing": "Analyzing... Please wait.",
        "overall": "🏁 Overall Conclusion",
        "avalanche_instr_title": "ℹ️ How to use Avalanche Test",
        "avalanche_instr_text": """
        **Avalanche Effect Test Instructions:**
        1. Generate a sequence using your RNG with a specific seed/key (Sequence A).
        2. Change ONE bit in the seed/key and generate a new sequence (Sequence B).
        3. Upload Sequence A as the 'Main File' and Sequence B as the 'Second File'.
        4. The test calculates the percentage of bits that changed. Ideally, ~50% of bits should change.
        """
    },
    "ru": {
        "title": "🔒 Проверка Криптостойкости",
        "desc": "Анализ криптографической стойкости битовых последовательностей различными методами.",
        "config": "Настройки",
        "window_sizes": "Размеры окна (через запятую)",
        "upload_main": "Загрузить файл (Основная последовательность)",
        "upload_second": "Загрузить второй файл (для Лавинного теста)",
        "run_analysis": "Запустить выбранные тесты",
        "success_load": "Файл успешно загружен! Длина: {} бит",
        "error_file": "Неверный формат файла. Должны быть только 0 и 1.",
        "select_tests": "Выберите тесты",
        "test_nn_stat": "Нейросетевой и Статистический (Хи-квадрат)",
        "test_nist": "NIST SP800-22",
        "test_diehard": "Тесты Diehard",
        "test_avalanche": "Лавинный тест (Нужно 2 файла)",
        "results_nn": "🧠 Комбинированный метод оценки",
        "results_stat": "📊 Статистический анализ (Хи-квадрат)",
        "results_nist": "📋 Результаты NIST SP800-22",
        "results_diehard": "🎲 Результаты Diehard",
        "results_avalanche": "❄️ Результаты Лавинного теста",
        "strong": "СТОЙКАЯ",
        "weak": "СЛАБАЯ",
        "inconclusive": "НЕОПРЕДЕЛЕННО",
        "accuracy": "Точность",
        "p_value": "P-значение",
        "analyzed": "Проанализировано бит",
        "tests": "Тесты",
        "tests_passed": "Тестов пройдено",
        "avalanche_ratio": "Коэффициент лавины",
        "ideal_ratio": "Идеал: 0.5 (50%)",
        "analyzing": "Идет анализ... Пожалуйста, подождите.",
        "overall": "🏁 Общее Заключение",
        "avalanche_instr_title": "ℹ️ Инструкция к Лавинному тесту",
        "avalanche_instr_text": """
        **Инструкция по Лавинному тесту:**
        1. Сгенерируйте последовательность с помощью вашего ГПСЧ с определенным ключом/зерном (Последовательность А).
        2. Измените ОДИН бит в ключе/зерне и сгенерируйте новую последовательность (Последовательность Б).
        3. Загрузите Последовательность А как 'Основной файл', а Последовательность Б как 'Второй файл'.
        4. Тест вычислит процент изменившихся бит. В идеале должно измениться ~50% бит.
        """
    }
}

# Language Selector
lang_code = st.sidebar.selectbox("Language / Язык", ["ru", "en"], index=0)
T = TRANS[lang_code]

st.title(T["title"])
st.markdown(T["desc"])

# Sidebar Configuration
st.sidebar.header(T["config"])
window_sizes_input = st.sidebar.text_input(T["window_sizes"], "8, 16, 32")
try:
    window_sizes = [int(x.strip()) for x in window_sizes_input.split(",")]
except ValueError:
    window_sizes = [8, 16, 32]

# Test Selection
st.sidebar.subheader(T["select_tests"])
use_nn_stat = st.sidebar.checkbox(T["test_nn_stat"], value=True)
use_nist = st.sidebar.checkbox(T["test_nist"], value=False)
use_diehard = st.sidebar.checkbox(T["test_diehard"], value=False)
use_avalanche = st.sidebar.checkbox(T["test_avalanche"])
if use_avalanche:
    st.sidebar.info(T["avalanche_instr_text"])

# File Uploads
uploaded_file = st.sidebar.file_uploader(T["upload_main"], type=["txt", "bin"])
uploaded_file_2 = None
if use_avalanche:
    uploaded_file_2 = st.sidebar.file_uploader(T["upload_second"], type=["txt", "bin"])

if uploaded_file is not None:
    content = uploaded_file.getvalue().decode("utf-8")
    sequence = analysis.read_binary_string(content)
    
    if sequence:
        st.sidebar.success(T["success_load"].format(len(sequence)))
        
        if st.sidebar.button(T["run_analysis"]):
            with st.spinner(T["analyzing"]):
                results_data = None
                nist_output_data = None
                diehard_output_data = None
                
                # 1. Neural Network & Statistical
                if use_nn_stat:
                    results = analysis.run_full_analysis(sequence, window_sizes)
                    results_data = results
                    if results:
                        st.header(T["results_nn"])
                        
                        tab1, tab2 = st.tabs(["Побитовый анализ (Bitwise)", "Блочный анализ (Blockwise)"])
                        
                        with tab1:
                            # NN Results Bitwise
                            nn_results = results['bitwise']['neural_network']
                            col1, col2 = st.columns(2)
                            col1.metric(T["accuracy"], f"{nn_results['overall_accuracy']:.2%}")
                            col2.metric(T["analyzed"], nn_results['total_analyzed'])
                            
                            if nn_results.get('details'):
                                df_nn = pd.DataFrame(nn_results['details'])
                                cols = ['window_size', 'direction', 'bits_analyzed', 'accuracy']
                                st.subheader("NN Summary")
                                st.dataframe(df_nn[cols])
                                
                                flat_nn_bitwise = []
                                for d in nn_results['details']:
                                    for p in d['predictions'][:50]:
                                        flat_nn_bitwise.append({
                                            'window_size': d['window_size'],
                                            'direction': d['direction'],
                                            'window': p['window'],
                                            'predicted': p['predicted'],
                                            'actual': p['actual'],
                                            'correct': p['correct']
                                        })
                                if flat_nn_bitwise:
                                    st.subheader("NN Detailed Predictions (Sample)")
                                    st.dataframe(pd.DataFrame(flat_nn_bitwise))
                            
                            if nn_results['is_strong']:
                                st.success(f"✅ {T['strong']} (Accuracy ≤ 55%)")
                            else:
                                st.error(f"❌ {T['weak']} (Accuracy > 55%)")
                                
                            # Stat Results Bitwise
                            st.subheader(T["results_stat"])
                            stat_results = results['bitwise']['statistical']
                            col1, col2 = st.columns(2)
                            col1.metric(T["p_value"], f"{stat_results['overall_p_value']:.3f}")
                            col2.metric(T["tests"], f"{stat_results['total_tests']}")

                            if stat_results['is_strong']:
                                st.success(f"✅ {T['strong']} (P-Value > 0.05)")
                            else:
                                st.error(f"❌ {T['weak']} (P-Value ≤ 0.05)")

                            if stat_results.get('details'):
                                df_stat = pd.DataFrame(stat_results['details'])
                                cols_stat = ['window_size', 'direction', 'tests', 'avg_chi_square', 'avg_p_value']
                                st.subheader("Statistical Summary")
                                st.dataframe(df_stat[cols_stat])
                                
                                flat_stat_bitwise = []
                                for d in stat_results['details']:
                                    for p in d['predictions'][:50]:
                                        flat_stat_bitwise.append({
                                            'window_size': d['window_size'],
                                            'direction': d['direction'],
                                            'window': p['window'],
                                            'actual': p['actual'],
                                            'chi_square': p['chi_square'],
                                            'p_value': p['p_value']
                                        })
                                if flat_stat_bitwise:
                                    st.subheader("Statistical Detailed Predictions (Sample)")
                                    st.dataframe(pd.DataFrame(flat_stat_bitwise))
                                
                        with tab2:
                            # NN Results Blockwise
                            b_nn_results = results['block']['neural_network']
                            col1, col2 = st.columns(2)
                            col1.metric(T["accuracy"], f"{b_nn_results['overall_accuracy']:.2%}")
                            col2.metric(T["analyzed"], b_nn_results['total_analyzed'])
                            
                            if b_nn_results.get('details'):
                                df_nn_b = pd.DataFrame(b_nn_results['details'])
                                cols_b = ['window_size', 'direction', 'window', 'predicted', 'actual', 'accuracy']
                                df_nn_display_b = df_nn_b[cols_b]
                                st.subheader("NN Details")
                                st.dataframe(df_nn_display_b)
                            
                            if b_nn_results['is_strong']:
                                st.success(f"✅ {T['strong']} (Accuracy ≤ 55%)")
                            else:
                                st.error(f"❌ {T['weak']} (Accuracy > 55%)")
                                
                            # Stat Results Blockwise
                            st.subheader(T["results_stat"])
                            b_stat_results = results['block']['statistical']
                            col1, col2 = st.columns(2)
                            col1.metric(T["p_value"], f"{b_stat_results['overall_p_value']:.3f}")
                            col2.metric(T["tests"], f"{b_stat_results['total_tests']}")

                            if b_stat_results['is_strong']:
                                st.success(f"✅ {T['strong']} (P-Value > 0.05)")
                            else:
                                st.error(f"❌ {T['weak']} (P-Value ≤ 0.05)")

                            if b_stat_results.get('details'):
                                df_stat_b = pd.DataFrame(b_stat_results['details'])
                                cols_stat_b = ['window_size', 'direction', 'window', 'predicted', 'actual', 'chi_square', 'p_value']
                                df_stat_display_b = df_stat_b[cols_stat_b]
                                st.subheader("Statistical Details")
                                st.dataframe(df_stat_display_b)

                # 2. NIST SP800-22
                if use_nist:
                    st.header(T["results_nist"])
                    # Create a temp file for NIST because it reads from file path
                    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
                        tmp.write("".join(map(str, sequence)))
                        tmp_path = tmp.name
                    
                    try:
                        from io import StringIO
                        old_stdout = sys.stdout
                        sys.stdout = mystdout = StringIO()
                        
                        runrun(tmp_path)
                        
                        sys.stdout = old_stdout
                        nist_output = mystdout.getvalue()
                        nist_output_data = nist_output
                        st.text(nist_output)
                        
                        # Simple parsing of "PASS" count
                        if "SUMMARY" in nist_output:
                            summary_lines = nist_output.split("SUMMARY")[-1].strip().split('\n')
                            pass_count = sum(1 for line in summary_lines if "PASS" in line)
                            total_count = sum(1 for line in summary_lines if "PASS" in line or "FAIL" in line or "ERROR" in line)
                        else:
                            pass_count = nist_output.count("PASS")
                            fail_count = nist_output.count("FAIL")
                            total_count = pass_count + fail_count
                        st.metric(T["tests_passed"], f"{pass_count} / {total_count}")
                        
                    except Exception as e:
                        st.error(f"NIST Error: {e}")
                    finally:
                        os.unlink(tmp_path)

                # 3. Diehard
                if use_diehard:
                    st.header(T["results_diehard"])
                    try:
                        # Dieharder expects string of bits
                        bitstring = "".join(map(str, sequence))
                        diehard_result = run_dieharder(bitstring)
                        diehard_output_data = diehard_result
                        
                        st.subheader(diehard_result['summary'])
                        
                        # Display details
                        if 'details' in diehard_result:
                            details = diehard_result['details']
                            if isinstance(details, list):
                                df = pd.DataFrame(details)
                                st.dataframe(df)
                            else:
                                st.write(details)
                                
                    except Exception as e:
                        st.error(f"Diehard Error: {e}")

                # 4. Avalanche Test
                if use_avalanche:
                    st.header(T["results_avalanche"])
                    
                    with st.expander(T["avalanche_instr_title"]):
                        st.markdown(T["avalanche_instr_text"])
                    
                    if uploaded_file_2 is not None:
                        content2 = uploaded_file_2.getvalue().decode("utf-8")
                        sequence2 = analysis.read_binary_string(content2)
                        
                        if sequence2:
                            av_results = avalanche.calculate_avalanche_effect(sequence, sequence2)
                            
                            if av_results['valid']:
                                if av_results.get('truncated', False):
                                    orig_lens = av_results['original_lengths']
                                    st.warning(f"⚠️ Files had different lengths ({orig_lens[0]} vs {orig_lens[1]}). Truncated to {av_results['length']} bits.")
                                
                                st.metric(T["avalanche_ratio"], f"{av_results['avalanche_ratio']:.2%}")
                                st.info(T["ideal_ratio"])
                                
                                if av_results['is_good']:
                                    st.success(f"✅ {T['strong']} (45% - 55%)")
                                else:
                                    st.error(f"❌ {T['weak']}")
                            else:
                                st.error(av_results['error'])
                        else:
                            st.error(T["error_file"])
                    else:
                        st.warning("Please upload the second file for Avalanche Test")
                
                if any([results_data, nist_output_data, diehard_output_data]):
                    try:
                        from save_utils import save_test_results
                        save_path = save_test_results(results_data, nist_output_data, diehard_output_data, "File", uploaded_file.name, 0, None)
                        st.success(f"💾 Results saved to {save_path}")
                    except Exception as e:
                        st.error(f"Error saving results: {e}")

    else:
        st.error(T["error_file"])
else:
    st.info(T["upload_main"])

# --- PRNG Generator Section ---
st.markdown("---")
st.header("🎲 " + ("Генератор ГПСЧ (Game of Life)" if lang_code == "ru" else "PRNG Generator (Game of Life)"))

with st.expander("⚙️ " + ("Настройки Генератора" if lang_code == "ru" else "Generator Settings"), expanded=True):
    # Generator Selection
    gen_options = ["Game of Life", "BBS", "AES (CTR)", "Magma (GOST)", "Kuznechik (GOST)", "SM4", "Mersenne Twister (Weak)", "LFSR (Weak)"]
    selected_gen = st.selectbox("Generator Algorithm / Алгоритм", gen_options)
    
    # Defaults for Game of Life to prevent NameError in Mass Verification
    prng_width = 50
    prng_height = 50
    prng_steps = 10
    boundary_mode_key = "toroid"
    extract_mode_key = "ternary"
    gen_length = 20000
    
    # Common Settings
    seed_input = st.number_input("Seed (Optional)", value=0, help="Leave 0 for random seed")
    if seed_input == 0: seed_input = None
    
    # Specific Settings
    if selected_gen == "Game of Life":
        col1, col2, col3 = st.columns(3)
        with col1:
            prng_width = st.number_input("Width", min_value=10, value=50)
        with col2:
            prng_height = st.number_input("Height", min_value=10, value=50)
        with col3:
            prng_steps = st.number_input("Steps", min_value=1, value=10)

            
        # Boundary Mode Selector
        boundary_options = {
            "toroid": "Toroid (Wrap-around) / Тороид (Замкнутый)",
            "fixed": "Fixed (Bounded) / Ограниченная матрица"
        }
        boundary_mode_key = st.selectbox(
            "Boundary Mode / Границы поля",
            options=list(boundary_options.keys()),
            format_func=lambda x: boundary_options[x]
        )
            
        # Extraction Mode Selector
        extract_mode_options = {
            "flatten": "All Bits (Flatten) / Все биты",
            "best_line": "Best Line (Max Entropy) / Лучшая строка",
            "ternary": "Large Sequence (Ternary) / Большая посл. (Троичная)"
        }
        extract_mode_key = st.sidebar.selectbox(
            "Extraction Mode / Метод извлечения",
            options=list(extract_mode_options.keys()),
            format_func=lambda x: extract_mode_options[x]
        )
            
        prng_fps = st.slider("FPS (Animation Speed)", min_value=1, max_value=60, value=20)
        enable_avalanche_mode = st.checkbox("❄️ " + ("Режим Лавинного Теста" if lang_code == "ru" else "Avalanche Test Mode"))
        
    else:
        # Settings for Stream Ciphers / BBS
        gen_length = st.number_input("Length (bits) / Длина (бит)", min_value=128, value=20000, step=128)
        enable_avalanche_mode = False # Disable for now or implement simpler version
        st.info(f"Selected: {selected_gen}. Generates {gen_length} bits.")



if "gen_bit_string" not in st.session_state:
    st.session_state["gen_bit_string"] = None
if "gen_seq_a" not in st.session_state:
    st.session_state["gen_seq_a"] = None
if "gen_seq_b" not in st.session_state:
    st.session_state["gen_seq_b"] = None

if st.button("🚀 " + ("Сгенерировать" if lang_code == "ru" else "Generate")):
    

    seed_val = seed_input
    bit_string = ""
    
    if selected_gen == "Game of Life":
        if enable_avalanche_mode:
            st.info("Generating two sequences with 1-bit difference in seed...")
            if seed_val is None:
                seed_val = int(time.time() * 1000)
                
            # Sequence A
            prng_a = GameOfLifePRNG(prng_width, prng_height, seed_val, boundary_mode=boundary_mode_key)
            seq_a, history_a = prng_a.generate(prng_steps, return_history=True, extract_mode=extract_mode_key)
            
            # Sequence B
            seed_b = seed_val ^ 1
            prng_b = GameOfLifePRNG(prng_width, prng_height, seed_b, boundary_mode=boundary_mode_key)
            seq_b, history_b = prng_b.generate(prng_steps, return_history=True, extract_mode=extract_mode_key)
            
            st.write(f"Seed A: {seed_val}")
            st.write(f"Seed B: {seed_b}")
            
            if prng_width > 1000 or prng_height > 1000 or prng_width / prng_height > 100 or prng_height / prng_width > 100:
                st.warning("⚠️ " + ("Визуализация отключена для слишком больших или несбалансированных сеток." if lang_code == "ru" else "Visualization is disabled for very large or unbalanced grids."))
            else:
                # Visualization
                st.subheader("📊 " + ("Визуализация До-После" if lang_code == "ru" else "Before/After Visualization"))
                
                def field_to_rgb(field):
                    rgb = np.zeros((field.shape[0], field.shape[1], 3), dtype=np.uint8)
                    rgb[field == 1] = [0, 255, 0] # Green
                    rgb[field == 2] = [255, 0, 0] # Red
                    return rgb
                
                initial_a = history_a[0]
                final_a = history_a[-1]
                initial_b = history_b[0]
                final_b = history_b[-1]
                
                img_width = 250
                
                # Sequence A
                st.markdown("### Sequence A")
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    st.caption(f"До (Step 0)")
                    st.image(field_to_rgb(initial_a), width=img_width, clamp=True, output_format="PNG")
                with col_a2:
                    st.caption(f"После (Step {prng_steps})")
                    st.image(field_to_rgb(final_a), width=img_width, clamp=True, output_format="PNG")
                
                # Sequence B
                st.markdown("### Sequence B")
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    st.caption(f"До (Step 0)")
                    st.image(field_to_rgb(initial_b), width=img_width, clamp=True, output_format="PNG")
                with col_b2:
                    st.caption(f"После (Step {prng_steps})")
                    st.image(field_to_rgb(final_b), width=img_width, clamp=True, output_format="PNG")
                
                # Difference
                st.markdown("### " + ("Разница" if lang_code == "ru" else "Difference"))
                col_diff1, col_diff2 = st.columns(2)
                with col_diff1:
                    st.caption("Initial Difference")
                    diff_initial = (initial_a != initial_b).astype(np.uint8) * 255
                    diff_rgb_initial = np.stack([diff_initial]*3, axis=-1)
                    st.image(diff_rgb_initial, width=img_width, clamp=True, output_format="PNG")
                    
                with col_diff2:
                    st.caption("Final Difference")
                    diff_final = (final_a != final_b).astype(np.uint8) * 255
                    diff_rgb_final = np.stack([diff_final]*3, axis=-1)
                    st.image(diff_rgb_final, width=img_width, clamp=True, output_format="PNG")
                
            bit_string = seq_a
            
            # Calculate Avalanche
            seq_a_list = [int(b) for b in seq_a]
            seq_b_list = [int(b) for b in seq_b]
            
            av_results = avalanche.calculate_avalanche_effect(seq_a_list, seq_b_list)
            
            if av_results['valid']:
                st.metric(T["avalanche_ratio"], f"{av_results['avalanche_ratio']:.2%}")
                if av_results['is_good']:
                    st.success(f"✅ {T['strong']} (45% - 55%)")
                else:
                    st.error(f"❌ {T['weak']}")
            
            
            st.session_state["gen_seq_a"] = seq_a
            st.session_state["gen_seq_b"] = seq_b
            st.session_state["gen_bit_string"] = seq_a

        else:
            # Standard Generation with Animation
            my_prng = GameOfLifePRNG(prng_width, prng_height, seed_val, boundary_mode=boundary_mode_key)
            
            if prng_width > 1000 or prng_height > 1000 or prng_width / prng_height > 100 or prng_height / prng_width > 100:
                st.warning("⚠️ " + ("Визуализация отключена для слишком больших или несбалансированных сеток." if lang_code == "ru" else "Visualization is disabled for very large or unbalanced grids."))
                with st.spinner("Generating..."):
                    bit_string, _ = my_prng.generate(prng_steps, extract_mode=extract_mode_key)
            else:
                st.subheader("Visualization")
                image_placeholder = st.empty()
                
                def get_image(field):
                    rgb_field = np.zeros((prng_height, prng_width, 3), dtype=np.uint8)
                    rgb_field[field == 1] = [0, 255, 0]
                    rgb_field[field == 2] = [255, 0, 0]
                    return rgb_field

                current_field = my_prng.current_field
                anim_width = 400
                image_placeholder.image(get_image(current_field), caption="Step 0", width=anim_width, output_format="PNG")
                time.sleep(1.0 / prng_fps)
                
                for step in range(1, prng_steps + 1):
                    my_prng.step()
                    current_field = my_prng.current_field
                    image_placeholder.image(get_image(current_field), caption=f"Step {step}", width=anim_width, output_format="PNG")
                    time.sleep(1.0 / prng_fps)
                    
                bit_string, _ = my_prng.generate(0, extract_mode=extract_mode_key)
                
            st.session_state["gen_bit_string"] = bit_string
            st.session_state["gen_seq_a"] = None
            st.session_state["gen_seq_b"] = None
    else:
        # Other Generators
        with st.spinner(f"Generating with {selected_gen}..."):
            if selected_gen == "BBS":
                gen = BBSGenerator(seed_val)
            elif selected_gen == "AES (CTR)":
                gen = AESGenerator(seed_val)
            elif selected_gen == "Magma (GOST)":
                gen = MagmaGenerator(seed_val)
            elif selected_gen == "Kuznechik (GOST)":
                gen = KuznechikGenerator(seed_val)
            elif selected_gen == "SM4":
                gen = SM4Generator(seed_val)
            elif selected_gen == "Mersenne Twister (Weak)":
                gen = MersenneTwisterGenerator(seed_val)
            elif selected_gen == "LFSR (Weak)":
                gen = LFSRGenerator(seed_val)
            
            
            bit_string = gen.generate(gen_length)
            st.session_state["gen_bit_string"] = bit_string
            st.session_state["gen_seq_a"] = None
            st.session_state["gen_seq_b"] = None

if st.session_state.get("gen_bit_string"):
    bit_string = st.session_state["gen_bit_string"]
    
    st.success(f"Generated {len(bit_string)} bits!")
    st.text_area("Output Sequence", bit_string[:500] + "..." if len(bit_string) > 500 else bit_string, height=100)
    st.download_button("Download Sequence", bit_string, "generated_sequence.txt")
    
    if st.session_state.get("gen_seq_a") and st.session_state.get("gen_seq_b"):
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("Download Sequence A", st.session_state["gen_seq_a"], "seq_a.txt")
        with col2:
            st.download_button("Download Sequence B", st.session_state["gen_seq_b"], "seq_b.txt")
    
    # Direct testing button
    st.markdown("---")
    st.subheader("🔬 " + ("Тестирование сгенерированной последовательности" if lang_code == "ru" else "Testing Generated Sequence"))
        
    col1, col2, col3 = st.columns(3)
    with col1:
        test_nn_stat_gen = st.checkbox(T["test_nn_stat"], value=True, key="gen_nn_stat")
    with col2:
        test_nist_gen = st.checkbox(T["test_nist"], key="gen_nist")
    with col3:
        test_diehard_gen = st.checkbox(T["test_diehard"], key="gen_diehard")
    
    if st.button("▶️ " + ("Проверить эту последовательность" if lang_code == "ru" else "Test This Sequence")):
        sequence = [int(b) for b in bit_string]
        
        with st.spinner(T["analyzing"]):
            results_data = None
            nist_output_data = None
            diehard_output_data = None
            # Neural Network & Statistical
            if test_nn_stat_gen:
                results = analysis.run_full_analysis(sequence, window_sizes)
                results_data = results
                if results:
                    st.header(T["results_nn"])
                    
                    tab1, tab2 = st.tabs(["Побитовый анализ (Bitwise)", "Блочный анализ (Blockwise)"])
                    
                    with tab1:
                        nn_results = results['bitwise']['neural_network']
                        col1, col2 = st.columns(2)
                        col1.metric(T["accuracy"], f"{nn_results['overall_accuracy']:.2%}")
                        col2.metric(T["analyzed"], nn_results['total_analyzed'])
                        if nn_results.get('details'):
                            df_nn = pd.DataFrame(nn_results['details'])
                            cols = ['window_size', 'direction', 'bits_analyzed', 'accuracy']
                            st.subheader("NN Summary")
                            st.dataframe(df_nn[cols])
                            
                            flat_nn_bitwise = []
                            for d in nn_results['details']:
                                for p in d['predictions'][:50]:
                                    flat_nn_bitwise.append({
                                        'window_size': d['window_size'],
                                        'direction': d['direction'],
                                        'window': p['window'],
                                        'predicted': p['predicted'],
                                        'actual': p['actual'],
                                        'correct': p['correct']
                                    })
                            if flat_nn_bitwise:
                                st.subheader("NN Detailed Predictions (Sample)")
                                st.dataframe(pd.DataFrame(flat_nn_bitwise))
                                
                        if nn_results['is_strong']:
                            st.success(f"✅ {T['strong']} (Accuracy ≤ 55%)")
                        else:
                            st.error(f"❌ {T['weak']} (Accuracy > 55%)")
                        
                        st.subheader(T["results_stat"])
                        stat_results = results['bitwise']['statistical']
                        col1, col2 = st.columns(2)
                        col1.metric(T["p_value"], f"{stat_results['overall_p_value']:.3f}")
                        
                        if stat_results.get('details'):
                            df_stat = pd.DataFrame(stat_results['details'])
                            cols_stat = ['window_size', 'direction', 'tests', 'avg_chi_square', 'avg_p_value']
                            st.subheader("Statistical Summary")
                            st.dataframe(df_stat[cols_stat])
                            
                            flat_stat_bitwise = []
                            for d in stat_results['details']:
                                for p in d['predictions'][:50]:
                                    flat_stat_bitwise.append({
                                        'window_size': d['window_size'],
                                        'direction': d['direction'],
                                        'window': p['window'],
                                        'actual': p['actual'],
                                        'chi_square': p['chi_square'],
                                        'p_value': p['p_value']
                                    })
                            if flat_stat_bitwise:
                                st.subheader("Statistical Detailed Predictions (Sample)")
                                st.dataframe(pd.DataFrame(flat_stat_bitwise))
                                
                        if stat_results['is_strong']:
                            st.success(f"✅ {T['strong']} (P-Value > 0.05)")
                        else:
                            st.error(f"❌ {T['weak']} (P-Value ≤ 0.05)")
                            
                    with tab2:
                        b_nn_results = results['block']['neural_network']
                        col1, col2 = st.columns(2)
                        col1.metric(T["accuracy"], f"{b_nn_results['overall_accuracy']:.2%}")
                        col2.metric(T["analyzed"], b_nn_results['total_analyzed'])
                        
                        if b_nn_results.get('details'):
                            df_nn_b = pd.DataFrame(b_nn_results['details'])
                            cols_b = ['window_size', 'direction', 'window', 'predicted', 'actual', 'accuracy']
                            df_nn_display_b = df_nn_b[cols_b]
                            st.subheader("NN Details")
                            st.dataframe(df_nn_display_b)
                            
                        if b_nn_results['is_strong']:
                            st.success(f"✅ {T['strong']} (Accuracy ≤ 55%)")
                        else:
                            st.error(f"❌ {T['weak']} (Accuracy > 55%)")
                        
                        st.subheader(T["results_stat"])
                        b_stat_results = results['block']['statistical']
                        col1, col2 = st.columns(2)
                        col1.metric(T["p_value"], f"{b_stat_results['overall_p_value']:.3f}")
                        
                        if b_stat_results.get('details'):
                            df_stat_b = pd.DataFrame(b_stat_results['details'])
                            cols_stat_b = ['window_size', 'direction', 'window', 'predicted', 'actual', 'chi_square', 'p_value']
                            df_stat_display_b = df_stat_b[cols_stat_b]
                            st.subheader("Statistical Details")
                            st.dataframe(df_stat_display_b)
                            
                        if b_stat_results['is_strong']:
                            st.success(f"✅ {T['strong']} (P-Value > 0.05)")
                        else:
                            st.error(f"❌ {T['weak']} (P-Value ≤ 0.05)")
            
            # NIST SP800-22
            if test_nist_gen:
                st.header(T["results_nist"])
                with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
                    tmp.write(bit_string)
                    tmp_path = tmp.name
                
                try:
                    from io import StringIO
                    old_stdout = sys.stdout
                    sys.stdout = mystdout = StringIO()
                    runrun(tmp_path)
                    sys.stdout = old_stdout
                    nist_output = mystdout.getvalue()
                    nist_output_data = nist_output
                    st.text(nist_output)
                    
                    if "SUMMARY" in nist_output:
                        summary_lines = nist_output.split("SUMMARY")[-1].strip().split('\n')
                        pass_count = sum(1 for line in summary_lines if "PASS" in line)
                        total_count = sum(1 for line in summary_lines if "PASS" in line or "FAIL" in line or "ERROR" in line)
                    else:
                        pass_count = nist_output.count("PASS")
                        fail_count = nist_output.count("FAIL")
                        total_count = pass_count + fail_count
                    st.metric(T["tests_passed"], f"{pass_count} / {total_count}")
                except Exception as e:
                    st.error(f"NIST Error: {e}")
                finally:
                    os.unlink(tmp_path)
            
            # Diehard
            if test_diehard_gen:
                st.header(T["results_diehard"])
                try:
                    diehard_result = run_dieharder(bit_string)
                    diehard_output_data = diehard_result
                    st.subheader(diehard_result['summary'])
                    if 'details' in diehard_result:
                        details = diehard_result['details']
                        if isinstance(details, list):
                            df = pd.DataFrame(details)
                            st.dataframe(df)
                        else:
                            st.write(details)
                except Exception as e:
                    st.error(f"Diehard Error: {e}")
            
            if any([results_data, nist_output_data, diehard_output_data]):
                try:
                    from save_utils import save_test_results
                    gen_w = prng_width if selected_gen == "Game of Life" else gen_length
                    gen_h = prng_height if selected_gen == "Game of Life" else 0
                    s = seed_input if selected_gen == "Game of Life" else (seed_input if seed_input is not None else 0)
                    save_path = save_test_results(results_data, nist_output_data, diehard_output_data, selected_gen, gen_w, gen_h, s)
                    st.success(f"💾 Results saved to {save_path}")
                except Exception as e:
                    st.error(f"Error saving results: {e}")

    # --- Mass Verification Section ---
    st.markdown("---")
    st.header("🔁 " + ("Массовая проверка" if lang_code == "ru" else "Mass Verification"))
    
    col_iter, col_len, col_run = st.columns([1, 1, 1])
    with col_iter:
        mass_iterations = st.number_input("Iterations / Итерации", min_value=1, max_value=100000, value=100)
    with col_len:
        mass_length = st.number_input("Sequence Length / Длина (бит)", min_value=128, max_value=1000000, value=1000, step=128)
    with col_run:
        st.write("") # spacing
        st.write("")
        run_mass_btn = st.button("🚀 " + ("Запустить массовую проверку" if lang_code == "ru" else "Run Mass Verification"))

    if run_mass_btn:
        with st.spinner("Running Mass Verification for ALL generators..."):
            
            from mass_test import run_mass_verification
            
            generators_to_test = [
                (GameOfLifePRNG, {'width': 50, 'height': max(20, mass_length//50 + 1), 'seed': seed_input, 'boundary_mode': 'toroid', 'extract_mode': extract_mode_key, 'steps': prng_steps, 'length': mass_length}),
                (BBSGenerator, {'seed': seed_input, 'length': mass_length}),
                (AESGenerator, {'seed': seed_input, 'length': mass_length}),
                (MagmaGenerator, {'seed': seed_input, 'length': mass_length}),
                (KuznechikGenerator, {'seed': seed_input, 'length': mass_length}),
                (SM4Generator, {'seed': seed_input, 'length': mass_length}),
                (MersenneTwisterGenerator, {'seed': seed_input, 'length': mass_length}),
                (LFSRGenerator, {'seed': seed_input, 'length': mass_length})
            ]
            
            all_results = []
            
            for gen_class, gen_kwargs in generators_to_test:
                st.subheader(f"Testing {gen_class.__name__}")
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(current, total):
                    progress = min(current / total, 1.0)
                    progress_bar.progress(progress)
                    status_text.text(f"Iteration {current}/{total}")

                final_metrics, res_dir = run_mass_verification(
                    generator_class=gen_class,
                    gen_kwargs=gen_kwargs,
                    iterations=mass_iterations,
                    window_sizes=window_sizes,
                    use_nn_stat=True,
                    use_nist=True,
                    use_diehard=True,
                    progress_callback=update_progress
                )
                
                st.success(f"Saved to {res_dir}")
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("NN Bitwise Acc", f"{final_metrics['nn_stat_averages']['bitwise_acc']:.2%}")
                col2.metric("Stat Bitwise P-Val", f"{final_metrics['nn_stat_averages']['bitwise_p']:.3f}")
                col3.metric("NIST Pass Ratio", f"{final_metrics['nist_avg_pass_ratio']:.2%}")
                col4.metric("Diehard Pass Ratio", f"{final_metrics['diehard_avg_pass_ratio']:.2%}")
                
                all_results.append(final_metrics)
                
            st.success("🎉 Mass verification for all generators completed!")

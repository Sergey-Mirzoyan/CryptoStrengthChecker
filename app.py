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
        "results_nn": "🧠 Neural Network Analysis",
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
        "results_nn": "🧠 Нейросетевой анализ",
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
                
                # 1. Neural Network & Statistical
                if use_nn_stat:
                    results = analysis.run_full_analysis(sequence, window_sizes)
                    if results:
                        # NN Results
                        st.header(T["results_nn"])
                        nn_results = results['neural_network']
                        col1, col2 = st.columns(2)
                        col1.metric(T["accuracy"], f"{nn_results['overall_accuracy']:.2%}")
                        col2.metric(T["analyzed"], nn_results['total_analyzed'])
                        
                        # Detailed NN results table
                        if nn_results.get('details'):
                            df_nn = pd.DataFrame(nn_results['details'])
                            # Keep only relevant columns for display
                            cols = ['window_size', 'direction', 'bits_analyzed', 'accuracy']
                            df_nn_display = df_nn[cols]
                            st.subheader(T["details_nn"] if "details_nn" in T else "NN Details")
                            st.dataframe(df_nn_display)
                        
                        if nn_results['is_strong']:
                            st.success(f"✅ {T['strong']} (Accuracy ≤ 55%)")
                        else:
                            st.error(f"❌ {T['weak']} (Accuracy > 55%)")
                            
                        # Stat Results
                        st.header(T["results_stat"])
                        stat_results = results['statistical']
                        col1, col2 = st.columns(2)
                        col1.metric(T["p_value"], f"{stat_results['overall_p_value']:.3f}")
                        col2.metric(T["tests"], f"{stat_results['total_tests']}")

                        if stat_results['is_strong']:
                            st.success(f"✅ {T['strong']} (P-Value > 0.05)")
                        else:
                            st.error(f"❌ {T['weak']} (P-Value ≤ 0.05)")

                        # Detailed Chi-square results table
                        if stat_results.get('details'):
                            df_stat = pd.DataFrame(stat_results['details'])
                            cols_stat = ['window_size', 'direction', 'tests', 'avg_chi_square', 'avg_p_value']
                            df_stat_display = df_stat[cols_stat]
                            st.subheader(T["details_stat"] if "details_stat" in T else "Statistical Details")
                            st.dataframe(df_stat_display)

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
                        st.text(nist_output)
                        
                        # Simple parsing of "PASS" count
                        pass_count = nist_output.count("PASS")
                        fail_count = nist_output.count("FAIL")
                        st.metric(T["tests_passed"], f"{pass_count} / {pass_count + fail_count}")
                        
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
                st.image(field_to_rgb(initial_a), width=img_width, clamp=True)
            with col_a2:
                st.caption(f"После (Step {prng_steps})")
                st.image(field_to_rgb(final_a), width=img_width, clamp=True)
            
            # Sequence B
            st.markdown("### Sequence B")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.caption(f"До (Step 0)")
                st.image(field_to_rgb(initial_b), width=img_width, clamp=True)
            with col_b2:
                st.caption(f"После (Step {prng_steps})")
                st.image(field_to_rgb(final_b), width=img_width, clamp=True)
            
            # Difference
            st.markdown("### " + ("Разница" if lang_code == "ru" else "Difference"))
            col_diff1, col_diff2 = st.columns(2)
            with col_diff1:
                st.caption("Initial Difference")
                diff_initial = (initial_a != initial_b).astype(np.uint8) * 255
                diff_rgb_initial = np.stack([diff_initial]*3, axis=-1)
                st.image(diff_rgb_initial, width=img_width, clamp=True)
                
            with col_diff2:
                st.caption("Final Difference")
                diff_final = (final_a != final_b).astype(np.uint8) * 255
                diff_rgb_final = np.stack([diff_final]*3, axis=-1)
                st.image(diff_rgb_final, width=img_width, clamp=True)
                
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
            
            st.download_button("Download Sequence A", seq_a, "seq_a.txt")
            st.download_button("Download Sequence B", seq_b, "seq_b.txt")

        else:
            # Standard Generation with Animation
            st.subheader("Visualization")
            image_placeholder = st.empty()
            
            # Initialize PRNG
            my_prng = GameOfLifePRNG(prng_width, prng_height, seed_val, boundary_mode=boundary_mode_key)
            
            def get_image(field):
                rgb_field = np.zeros((prng_height, prng_width, 3), dtype=np.uint8)
                rgb_field[field == 1] = [0, 255, 0]
                rgb_field[field == 2] = [255, 0, 0]
                return rgb_field

            current_field = my_prng.current_field
            anim_width = 400
            image_placeholder.image(get_image(current_field), caption="Step 0", width=anim_width)
            time.sleep(1.0 / prng_fps)
            
            for step in range(1, prng_steps + 1):
                my_prng.step()
                current_field = my_prng.current_field
                image_placeholder.image(get_image(current_field), caption=f"Step {step}", width=anim_width)
                time.sleep(1.0 / prng_fps)
                
            bit_string, _ = my_prng.generate(0, extract_mode=extract_mode_key)
            
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
            
    st.success(f"Generated {len(bit_string)} bits!")
    st.text_area("Output Sequence", bit_string[:500] + "..." if len(bit_string) > 500 else bit_string, height=100)
    st.download_button("Download Sequence", bit_string, "generated_sequence.txt")
    
    # Direct testing button
    st.markdown("---")
    test_generated = st.checkbox("🧪 " + ("Проверить эту последовательность" if lang_code == "ru" else "Test This Sequence"))
    
    if test_generated:
        st.subheader("🔬 " + ("Тестирование сгенерированной последовательности" if lang_code == "ru" else "Testing Generated Sequence"))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            test_nn_stat_gen = st.checkbox(T["test_nn_stat"], value=True, key="gen_nn_stat")
        with col2:
            test_nist_gen = st.checkbox(T["test_nist"], key="gen_nist")
        with col3:
            test_diehard_gen = st.checkbox(T["test_diehard"], key="gen_diehard")
        
        if st.button("▶️ " + ("Запустить тесты" if lang_code == "ru" else "Run Tests")):
            sequence = [int(b) for b in bit_string]
            
            with st.spinner(T["analyzing"]):
                # Neural Network & Statistical
                if test_nn_stat_gen:
                    results = analysis.run_full_analysis(sequence, window_sizes)
                    if results:
                        st.header(T["results_nn"])
                        nn_results = results['neural_network']
                        col1, col2 = st.columns(2)
                        col1.metric(T["accuracy"], f"{nn_results['overall_accuracy']:.2%}")
                        col2.metric(T["analyzed"], nn_results['total_analyzed'])
                        
                        if nn_results['is_strong']:
                            st.success(f"✅ {T['strong']} (Accuracy ≤ 55%)")
                        else:
                            st.error(f"❌ {T['weak']} (Accuracy > 55%)")
                        
                        st.header(T["results_stat"])
                        stat_results = results['statistical']
                        col1, col2 = st.columns(2)
                        col1.metric(T["p_value"], f"{stat_results['overall_p_value']:.3f}")
                        
                        if stat_results['is_strong']:
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
                        st.text(nist_output)
                        
                        pass_count = nist_output.count("PASS")
                        fail_count = nist_output.count("FAIL")
                        st.metric(T["tests_passed"], f"{pass_count} / {pass_count + fail_count}")
                    except Exception as e:
                        st.error(f"NIST Error: {e}")
                    finally:
                        os.unlink(tmp_path)
                
                # Diehard
                if test_diehard_gen:
                    st.header(T["results_diehard"])
                    try:
                        diehard_result = run_dieharder(bit_string)
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

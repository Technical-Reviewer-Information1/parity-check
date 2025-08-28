import streamlit as st
import pandas as pd
import time

# ページ設定
st.set_page_config(
    page_title="パリティチェック学習アプリ",
    page_icon="🔍",
    layout="wide"
)

# カスタムCSS
st.markdown("""
<style>
.step-indicator {
    display: flex;
    justify-content: space-between;
    margin: 20px 0;
    padding: 10px;
    background-color: #f0f2f6;
    border-radius: 10px;
}
.step {
    flex: 1;
    text-align: center;
    padding: 10px;
    margin: 0 5px;
    border-radius: 5px;
    font-weight: bold;
}
.step-completed {
    background-color: #28a745;
    color: white;
}
.step-current {
    background-color: #007bff;
    color: white;
}
.step-pending {
    background-color: #e9ecef;
    color: #6c757d;
}
.bit-button {
    font-family: monospace;
    font-size: 18px;
    font-weight: bold;
}
.success-animation {
    animation: bounce 0.6s;
}
@keyframes bounce {
    0%, 20%, 60%, 100% { transform: translateY(0); }
    40% { transform: translateY(-20px); }
    80% { transform: translateY(-10px); }
}
.error-flash {
    animation: flash 0.8s;
}
@keyframes flash {
    0%, 100% { background-color: transparent; }
    50% { background-color: #ff6b6b; }
}
.stats-card {
    background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    margin: 10px 0;
}
.highlight-bit {
    background-color: #ffeb3b;
    color: #000;
    padding: 5px;
    border-radius: 3px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# セッション状態の初期化
def initialize_session_state():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        # 1次元パリティチェック用の状態
        st.session_state.transmitted_1d = None
        st.session_state.parity_mode_1d = None
        st.session_state.parity_bit_1d = None
        st.session_state.error_data_1d = None
        st.session_state.error_position_1d = -1
        st.session_state.step_1d = 0  # 0: 準備, 1: パリティ計算済み, 2: エラー発生, 3: チェック済み
        # 2次元パリティチェック用の状態
        st.session_state.data_matrix = None
        st.session_state.matrix_with_parity = None
        st.session_state.error_row = -1
        st.session_state.error_col = -1
        st.session_state.step_2d = 0  # 0: 準備, 1: パリティ計算済み, 2: エラー発生, 3: チェック・訂正済み
        # 統計情報
        st.session_state.stats = {
            'total_errors_detected': 0,
            'total_errors_corrected': 0,
            'total_experiments': 0,
            'start_time': time.time()
        }

initialize_session_state()

# ヘルパー関数
def create_step_indicator(steps, current_step):
    step_html = '<div class="step-indicator">'
    for i, step_name in enumerate(steps):
        if i < current_step:
            css_class = "step step-completed"
            icon = "✅"
        elif i == current_step:
            css_class = "step step-current"
            icon = "🔄"
        else:
            css_class = "step step-pending"
            icon = "⏳"
        step_html += f'<div class="{css_class}">{icon} {step_name}</div>'
    step_html += '</div>'
    return step_html

def display_bit_array(bits, clickable=False, prefix="", error_position=-1):
    cols = st.columns(len(bits))
    for i, bit in enumerate(bits):
        with cols[i]:
            if clickable:
                style = "bit-button"
                if i == error_position:
                    style += " error-flash"
                if st.button(f"{bit}", key=f"{prefix}bit_{i}", help=f"ビット{i+1}をクリック"):
                    return i
            else:
                if i == error_position:
                    st.markdown(f'<span class="highlight-bit">{bit}</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<code style="font-size: 18px; font-weight: bold;">{bit}</code>', unsafe_allow_html=True)
    return -1

def show_statistics():
    stats = st.session_state.stats
    elapsed_time = int(time.time() - stats['start_time'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="stats-card">
            <h3>🎯 実験回数</h3>
            <h2>{stats['total_experiments']}</h2>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="stats-card">
            <h3>🔍 検出数</h3>
            <h2>{stats['total_errors_detected']}</h2>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="stats-card">
            <h3>🔧 訂正数</h3>
            <h2>{stats['total_errors_corrected']}</h2>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
        <div class="stats-card">
            <h3>⏱️ 学習時間</h3>
            <h2>{elapsed_time // 60}m {elapsed_time % 60}s</h2>
        </div>
        ''', unsafe_allow_html=True)

# メインタイトル
st.title("🔍 パリティチェック学習ラボ")
st.caption("Created by Dit-Lab.(Daiki ITO)")
st.caption("Supported by Tomoaki ATSUMI")

# アプリの説明
st.markdown("""
## 🎯 ミッション
データ通信で使われる「パリティチェック」という技術をマスターしよう！
実際にビットを操作して、エラーの検出から訂正まで完全攻略！

### 🚀 学習の流れ
1. **1次元パリティチェック**: エラーを見つける技術
2. **2次元パリティチェック**: エラーを見つけて直す技術
""")

# 統計情報の表示
show_statistics()

# ===========================================
# 1次元パリティチェック セクション
# ===========================================

st.markdown("---")
st.markdown("# 🎮 レベル1: 1次元パリティチェック")
st.markdown("**ミッション**: エラーを検出せよ！")

# ステップインジケーター
steps_1d = ["データ準備", "パリティ計算", "エラー発生", "エラー検出"]
st.markdown(create_step_indicator(steps_1d, st.session_state.step_1d), unsafe_allow_html=True)

# ステップ1: データ準備
st.markdown("## 📋 ステップ1: データ準備")

col1, col2 = st.columns([2, 1])
with col1:
    # パリティ方式選択
    parity_mode = st.radio(
        "🎛️ パリティ方式を選択:",
        ["奇数パリティ（「1」の合計を奇数に）", "偶数パリティ（「1」の合計を偶数に）"],
        key="1d_parity_mode",
        index=0 if st.session_state.parity_mode_1d is None else (0 if "奇数" in st.session_state.parity_mode_1d else 1)
    )

with col2:
    st.info("💡 **ヒント**\nパリティビットは、データの誤りを見つけるための「番人」です！")

# 送信データの表示
original_data = "1011001"
st.markdown(f"### 📤 送信データ: `{original_data}` (7ビット)")

# パリティビット計算
if st.button("🧮 パリティビットを計算して追加する", key="calc_parity", type="primary"):
    ones_count = original_data.count('1')
    st.write(f"🔢 データ「{original_data}」には「1」が{ones_count}つ（{'奇数' if ones_count % 2 == 1 else '偶数'}個）あります。")
    
    if "奇数" in parity_mode:
        parity_bit = "0" if ones_count % 2 == 1 else "1"
        st.write(f"🎯 全体で奇数個にするため、パリティビットは「{parity_bit}」です。")
    else:
        parity_bit = "1" if ones_count % 2 == 1 else "0"
        st.write(f"🎯 全体で偶数個にするため、パリティビットは「{parity_bit}」です。")
    
    transmitted_data = original_data + parity_bit
    st.success(f"✅ **送信データ (8ビット):** `{transmitted_data}`")
    
    # セッションステートに保存
    st.session_state.transmitted_1d = transmitted_data
    st.session_state.parity_mode_1d = parity_mode
    st.session_state.parity_bit_1d = parity_bit
    st.session_state.step_1d = 1

# 現在の送信データを表示（計算済みの場合）
if st.session_state.transmitted_1d is not None:
    if st.session_state.step_1d >= 1:
        st.success(f"📡 **送信データ:** `{st.session_state.transmitted_1d}`")

# ステップ2: エラー発生
if st.session_state.step_1d >= 1:
    st.markdown("## ⚡ ステップ2: 通信エラーシミュレーション")
    st.markdown("🎲 **ミッション**: 通信中のノイズを再現！好きなビットを1つクリックして反転させよう！")
    
    # ビット反転インターフェース
    if st.session_state.error_data_1d is None:
        st.session_state.error_data_1d = st.session_state.transmitted_1d
        st.session_state.error_position_1d = -1
    
    st.markdown("### 🎮 インタラクティブビットフリップ")
    clicked_bit = display_bit_array(
        list(st.session_state.error_data_1d), 
        clickable=True, 
        prefix="1d_", 
        error_position=st.session_state.error_position_1d
    )
    
    if clicked_bit != -1:
        # ビット反転
        error_data_list = list(st.session_state.error_data_1d)
        error_data_list[clicked_bit] = "0" if error_data_list[clicked_bit] == "1" else "1"
        st.session_state.error_data_1d = "".join(error_data_list)
        st.session_state.error_position_1d = clicked_bit
        st.session_state.step_1d = 2
        
        st.balloons()
        st.success(f"💥 ビット{clicked_bit + 1}を反転させました！")
    
    st.markdown(f"### 📥 現在の受信データ: `{st.session_state.error_data_1d}`")
    
    if st.session_state.error_position_1d != -1:
        st.info(f"🎯 位置{st.session_state.error_position_1d + 1}のビット「{st.session_state.transmitted_1d[st.session_state.error_position_1d]}」→「{st.session_state.error_data_1d[st.session_state.error_position_1d]}」に変化！")

# ステップ3: エラーチェック
if st.session_state.step_1d >= 2:
    st.markdown("## 🔍 ステップ3: エラー検出")
    
    if st.button("🕵️ 受信データをチェックする", key="check_1d", type="primary"):
        received_data = st.session_state.error_data_1d
        ones_in_received = received_data.count('1')
        
        if "奇数" in st.session_state.parity_mode_1d:
            expected_parity = "奇数"
            actual_parity = "奇数" if ones_in_received % 2 == 1 else "偶数"
        else:
            expected_parity = "偶数"
            actual_parity = "偶数" if ones_in_received % 2 == 0 else "奇数"
        
        st.write(f"🔢 受信データ「{received_data}」には「1」が{ones_in_received}つ（{actual_parity}個）あります。")
        
        if expected_parity != actual_parity:
            st.error(f"🚨 **エラーを検知しました！** 「1」の合計が{actual_parity}個になりました。（{expected_parity}のはず）")
            st.session_state.stats['total_errors_detected'] += 1
        else:
            st.success("✅ エラーは検知されませんでした。")
        
        st.session_state.stats['total_experiments'] += 1
        st.session_state.step_1d = 3
    
    # まとめ
    if st.session_state.step_1d >= 3:
        st.info("📝 **1次元パリティチェックのまとめ**\n"
               "✅ エラーの有無は分かる\n"
               "❌ どのビットが間違っているかは特定できない")

# ===========================================
# 2次元パリティチェック セクション
# ===========================================

st.markdown("---")
st.markdown("# 🎯 レベル2: 2次元パリティチェック")
st.markdown("**ミッション**: エラーを検出し、特定し、訂正せよ！")

# ステップインジケーター
steps_2d = ["データ準備", "パリティ計算", "エラー発生", "エラー訂正"]
st.markdown(create_step_indicator(steps_2d, st.session_state.step_2d), unsafe_allow_html=True)

# ステップ1: データ準備
st.markdown("## 🗃️ ステップ1: 2次元データ準備")
st.markdown("🎨 今度はデータをマトリックス状に配置して、行と列の両方向からチェック！")

# 初期データ
initial_matrix = [
    [1, 1, 0, 1],
    [1, 1, 1, 0],
    [1, 0, 1, 1],
    [0, 1, 0, 0]
]

# セッションステートの初期化（2次元用）
if st.session_state.data_matrix is None:
    st.session_state.data_matrix = [row[:] for row in initial_matrix]
    st.session_state.matrix_with_parity = None
    st.session_state.error_row = -1
    st.session_state.error_col = -1

# データ表示
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📊 データブロック (4×4)")
    matrix_df = pd.DataFrame(
        st.session_state.data_matrix,
        columns=['列1', '列2', '列3', '列4'],
        index=['行1', '行2', '行3', '行4']
    )
    st.dataframe(matrix_df, use_container_width=True)

with col2:
    st.info("💡 **2次元の強み**\n"
           "行と列の交点でエラーの正確な位置を特定できる！")

# パリティ計算済みの場合は結果を表示
if st.session_state.matrix_with_parity is not None:
    st.success("✅ パリティビットが計算されています！")
    df_with_parity = pd.DataFrame(
        st.session_state.matrix_with_parity,
        columns=['列1', '列2', '列3', '列4', '🔍行パリティ'],
        index=['行1', '行2', '行3', '行4', '🔍列パリティ']
    )
    st.dataframe(df_with_parity, use_container_width=True)

# パリティビット計算
if st.button("🧮 行と列のパリティビットを計算する", key="calc_2d_parity", type="primary"):
    matrix = st.session_state.data_matrix
    
    # 行パリティの計算
    row_parities = []
    for row in matrix:
        parity = sum(row) % 2
        row_parities.append(parity)
    
    # 列パリティの計算
    col_parities = []
    for col in range(4):
        parity = sum(matrix[row][col] for row in range(4)) % 2
        col_parities.append(parity)
    
    # パリティを含む行列の作成
    matrix_with_parity = []
    for i in range(4):
        row_with_parity = matrix[i] + [row_parities[i]]
        matrix_with_parity.append(row_with_parity)
    
    # 列パリティ行を追加
    col_parity_row = col_parities + [sum(col_parities) % 2]
    matrix_with_parity.append(col_parity_row)
    
    st.session_state.matrix_with_parity = matrix_with_parity
    st.session_state.step_2d = 1
    
    # アニメーション効果
    with st.spinner('パリティビットを計算中...'):
        time.sleep(1)
    st.balloons()

# ステップ2: エラー発生
if st.session_state.step_2d >= 1:
    st.markdown("## ⚡ ステップ2: エラーシミュレーション")
    st.markdown("🎯 **チャレンジ**: データ部分のビットを1つクリックしてエラーを発生させよう！")
    
    # ビット反転インターフェース（4x4グリッド）
    st.markdown("### 🎮 マトリックスビットフリップ")
    
    for i in range(4):
        cols = st.columns(4)
        for j in range(4):
            with cols[j]:
                current_bit = st.session_state.data_matrix[i][j]
                style_class = ""
                if i == st.session_state.error_row and j == st.session_state.error_col:
                    style_class = "error-flash"
                
                if st.button(f"{current_bit}", key=f"matrix_bit_{i}_{j}", help=f"行{i+1}, 列{j+1}"):
                    # ビット反転
                    st.session_state.data_matrix[i][j] = 1 - current_bit
                    st.session_state.error_row = i
                    st.session_state.error_col = j
                    st.session_state.step_2d = 2
                    
                    st.balloons()
                    st.success(f"💥 行{i+1}, 列{j+1}のビットを反転！")
    
    if st.session_state.error_row != -1:
        st.info(f"🎯 **エラー発生位置**: 行{st.session_state.error_row + 1}, 列{st.session_state.error_col + 1}")

# ステップ3: エラー検出・特定・訂正
if st.session_state.step_2d >= 2:
    st.markdown("## 🔧 ステップ3: エラー検出・特定・訂正")
    
    if st.button("🕵️‍♀️ エラーをチェックして訂正する", key="check_2d", type="primary"):
        with st.spinner('エラーを解析中...'):
            time.sleep(1)
        
        # 新しいパリティ計算
        matrix = st.session_state.data_matrix
        
        # 行パリティチェック
        error_rows = []
        for i in range(4):
            expected_parity = st.session_state.matrix_with_parity[i][4]
            actual_parity = sum(matrix[i]) % 2
            if expected_parity != actual_parity:
                error_rows.append(i)
        
        # 列パリティチェック
        error_cols = []
        for j in range(4):
            expected_parity = st.session_state.matrix_with_parity[4][j]
            actual_parity = sum(matrix[i][j] for i in range(4)) % 2
            if expected_parity != actual_parity:
                error_cols.append(j)
        
        if error_rows and error_cols:
            error_row = error_rows[0]
            error_col = error_cols[0]
            st.error(f"🚨 **エラーを発見！** {error_row + 1}行目と{error_col + 1}列目が交差するビットが怪しい！")
            
            # エラービットをハイライト表示
            highlight_matrix = []
            for i in range(4):
                row = []
                for j in range(4):
                    if i == error_row and j == error_col:
                        row.append(f"🔴{matrix[i][j]}")  # エラービット
                    elif i == error_row or j == error_col:
                        row.append(f"🟡{matrix[i][j]}")  # エラー行・列
                    else:
                        row.append(str(matrix[i][j]))
                highlight_matrix.append(row)
            
            highlight_df = pd.DataFrame(
                highlight_matrix,
                columns=['列1', '列2', '列3', '列4'],
                index=['行1', '行2', '行3', '行4']
            )
            st.dataframe(highlight_df, use_container_width=True)
            
            # エラー訂正
            if st.button("🔧 エラーを訂正する", key="correct_error", type="primary"):
                st.session_state.data_matrix[error_row][error_col] = 1 - st.session_state.data_matrix[error_row][error_col]
                st.success("🎉 **エラービットを特定し、訂正しました！**")
                
                # 統計更新
                st.session_state.stats['total_errors_detected'] += 1
                st.session_state.stats['total_errors_corrected'] += 1
                st.session_state.stats['total_experiments'] += 1
                
                # 訂正後のデータ表示
                corrected_df = pd.DataFrame(
                    st.session_state.data_matrix,
                    columns=['列1', '列2', '列3', '列4'],
                    index=['行1', '行2', '行3', '行4']
                )
                st.dataframe(corrected_df, use_container_width=True)
                
                # 状態リセット
                st.session_state.error_row = -1
                st.session_state.error_col = -1
                st.session_state.step_2d = 3
                
                st.balloons()
        else:
            st.success("✅ エラーは検知されませんでした。")

# ===========================================
# 学習のまとめ
# ===========================================

st.markdown("---")
st.markdown("# 🎓 学習成果まとめ")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🔍 1次元パリティチェック
    - ✅ **検出**: 1ビットエラーを発見
    - ❌ **特定**: エラー位置は不明
    - ❌ **訂正**: 自動修復は不可能
    - ⚡ **特徴**: シンプル・高速
    """)

with col2:
    st.markdown("""
    ### 🎯 2次元パリティチェック
    - ✅ **検出**: 1ビットエラーを発見
    - ✅ **特定**: エラー位置を正確に特定
    - ✅ **訂正**: 自動でエラーを修復
    - 🧠 **特徴**: 複雑だが強力
    """)

# 実世界での応用
st.markdown("### 🌍 実世界での応用例")
applications = [
    ("💾 メモリ", "ECCメモリでデータ保護"),
    ("📡 通信", "インターネット・Wi-Fi"),
    ("💿 ストレージ", "HDD・SSD・CD・DVD"),
    ("📱 QRコード", "汚れや破損に対する耐性"),
    ("🛰️ 宇宙通信", "ノイズの多い環境での通信"),
    ("🏥 医療機器", "生命に関わる重要データの保護")
]

cols = st.columns(3)
for i, (icon, desc) in enumerate(applications):
    with cols[i % 3]:
        st.info(f"{icon}\n{desc}")

# リセット機能（改善版）
st.markdown("---")
st.markdown("## 🔄 リセット・再実験")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔄 1次元リセット", help="1次元パリティチェックをやり直し"):
        st.session_state.transmitted_1d = None
        st.session_state.parity_mode_1d = None
        st.session_state.parity_bit_1d = None
        st.session_state.error_data_1d = None
        st.session_state.error_position_1d = -1
        st.session_state.step_1d = 0
        st.success("✅ 1次元リセット完了！")

with col2:
    if st.button("🔄 2次元リセット", help="2次元パリティチェックをやり直し"):
        st.session_state.data_matrix = [row[:] for row in initial_matrix]
        st.session_state.matrix_with_parity = None
        st.session_state.error_row = -1
        st.session_state.error_col = -1
        st.session_state.step_2d = 0
        st.success("✅ 2次元リセット完了！")

with col3:
    if st.button("📊 統計リセット", help="学習統計をクリア"):
        st.session_state.stats = {
            'total_errors_detected': 0,
            'total_errors_corrected': 0,
            'total_experiments': 0,
            'start_time': time.time()
        }
        st.success("✅ 統計リセット完了！")

with col4:
    if st.button("🌟 完全リセット", help="アプリ全体を初期状態に", type="primary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("✅ 完全リセット完了！")

# 追加の学習コンテンツ
with st.expander("🚀 より高度な学習内容"):
    st.markdown("""
    ### 🎓 上級エラー訂正符号
    - **ハミング符号**: より効率的な1ビットエラー訂正
    - **リード・ソロモン符号**: 複数ビットエラー対応（DVD、QRコード）
    - **LDPC符号**: 現代通信システムの主力
    - **ターボ符号**: 携帯電話で活躍
    
    ### 🧪 実験アイデア
    - 🔍 2ビット同時エラーの動作確認
    - 📏 より大きなマトリックス（8×8）での実験
    - 🎯 奇数パリティでの2次元チェック
    - ⚡ エラー率とパフォーマンスの関係調査
    
    ### 📚 参考資料
    - 情報理論の教科書
    - 通信工学の専門書
    - オンライン講座での深堀り学習
    """)

# フッター
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🎉 パリティチェック学習ラボ 🎉</p>
    <p>高校「情報I」学習者のためのインタラクティブ学習ツール</p>
    <p>楽しく学んで、理解を深めよう！</p>
</div>
""", unsafe_allow_html=True)
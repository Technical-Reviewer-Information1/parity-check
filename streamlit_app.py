import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(
    page_title="パリティチェック学習アプリ",
    page_icon="🔍",
    layout="wide"
)

# メインタイトル
st.title("🔍 パリティチェック 〜データの誤りを見つけて直そう〜")
st.caption("Created by Dit-Lab.(Daiki ITO)")
st.caption("Supported by Tomoaki ATSUMI")

# アプリの説明
st.markdown("""
このアプリでは、データ通信で使われる「パリティチェック」という技術を体験的に学べます。
実際にビットを操作して、エラーの検出から訂正まで体験してみましょう！
""")

# 1次元パリティチェックセクション
with st.expander("体験1：1次元パリティチェック 〜エラーを見つける〜", expanded=True):
    st.subheader("🎯 目的")
    st.markdown("1つのパリティビットを付加することで、1ビットの誤りを検出できるが、場所の特定はできないことを体験する")
    
    # ステップ1: 送信データの準備
    st.markdown("### ステップ1: 送信データの準備")
    
    # パリティ方式選択
    parity_mode = st.radio(
        "パリティ方式を選択してください:",
        ["奇数パリティ（データ内の「1」の合計が奇数になるように調整）", 
         "偶数パリティ（データ内の「1」の合計が偶数になるように調整）"],
        key="1d_parity_mode"
    )
    
    # 送信データの表示
    original_data = "1011001"
    st.markdown(f"**送信データ:** `{original_data}` (7ビット)")
    
    # パリティビット計算
    if st.button("パリティビットを計算して追加する", key="calc_parity"):
        ones_count = original_data.count('1')
        st.write(f"データ「{original_data}」には「1」が{ones_count}つ（{'奇数' if ones_count % 2 == 1 else '偶数'}個）あります。")
        
        if "奇数" in parity_mode:
            parity_bit = "0" if ones_count % 2 == 1 else "1"
            st.write(f"全体で奇数個にするため、パリティビットは「{parity_bit}」です。")
        else:
            parity_bit = "1" if ones_count % 2 == 1 else "0"
            st.write(f"全体で偶数個にするため、パリティビットは「{parity_bit}」です。")
        
        transmitted_data = original_data + parity_bit
        st.success(f"**送信データ (8ビット):** `{transmitted_data}`")
        
        # セッションステートに保存
        st.session_state.transmitted_1d = transmitted_data
        st.session_state.parity_mode_1d = parity_mode
        st.session_state.parity_bit_1d = parity_bit
    
    # ステップ2: 通信エラーの発生
    if 'transmitted_1d' in st.session_state:
        st.markdown("### ステップ2: 通信エラーの発生")
        st.markdown("通信中にノイズでビットが反転するエラーを再現してみよう！下のデータのうち、好きなビットを1つクリックして反転させてください。")
        
        # ビット反転インターフェース
        if 'error_data_1d' not in st.session_state:
            st.session_state.error_data_1d = st.session_state.transmitted_1d
            st.session_state.error_position_1d = -1
        
        cols = st.columns(8)
        error_data_list = list(st.session_state.error_data_1d)
        
        for i in range(8):
            with cols[i]:
                if st.button(f"{error_data_list[i]}", key=f"bit_{i}", help=f"ビット{i+1}"):
                    # ビット反転
                    error_data_list[i] = "0" if error_data_list[i] == "1" else "1"
                    st.session_state.error_data_1d = "".join(error_data_list)
                    st.session_state.error_position_1d = i
        
        st.markdown(f"**現在のデータ:** `{st.session_state.error_data_1d}`")
        if st.session_state.error_position_1d != -1:
            st.info(f"ビット{st.session_state.error_position_1d + 1}を反転させました！")
        
        # ステップ3: 受信側でのチェック
        st.markdown("### ステップ3: 受信側でのチェック")
        if st.button("受信データをチェックする", key="check_1d"):
            received_data = st.session_state.error_data_1d
            ones_in_received = received_data.count('1')
            
            if "奇数" in st.session_state.parity_mode_1d:
                expected_parity = "奇数"
                actual_parity = "奇数" if ones_in_received % 2 == 1 else "偶数"
            else:
                expected_parity = "偶数"
                actual_parity = "偶数" if ones_in_received % 2 == 0 else "奇数"
            
            st.write(f"受信データ「{received_data}」には「1」が{ones_in_received}つ（{actual_parity}個）あります。")
            
            if expected_parity != actual_parity:
                st.error(f"🚨 エラーを検知！「1」の合計が{actual_parity}個になりました。（{expected_parity}のはず）")
            else:
                st.success("✅ エラーは検知されませんでした。")
        
        st.markdown("### まとめ")
        st.info("このように、1次元パリティチェックではエラーの有無はわかりますが、どのビットが間違っているかまでは特定できません。")

# 2次元パリティチェックセクション
with st.expander("体験2：2次元パリティチェック 〜エラーを見つけて直す〜"):
    st.subheader("🎯 目的")
    st.markdown("データを格子状に並べ、行と列それぞれにパリティビットを付加することで、1ビットの誤りを検出し、場所を特定して訂正まで可能なことを体験する")
    
    # ステップ1: 送信データの準備
    st.markdown("### ステップ1: 送信データの準備")
    st.markdown("今度はデータをブロック状に並べて、行と列の両方でチェックしてみよう。（偶数パリティを使用します）")
    
    # 初期データ
    initial_matrix = [
        [1, 1, 0, 1],
        [1, 1, 1, 0],
        [1, 0, 1, 1],
        [0, 1, 0, 0]
    ]
    
    # セッションステートの初期化
    if 'data_matrix' not in st.session_state:
        st.session_state.data_matrix = [row[:] for row in initial_matrix]
        st.session_state.matrix_with_parity = None
        st.session_state.error_row = -1
        st.session_state.error_col = -1
    
    # データ表示
    st.markdown("**データブロック (4x4):**")
    matrix_df = pd.DataFrame(st.session_state.data_matrix)
    st.dataframe(matrix_df, use_container_width=False)
    
    # パリティビット計算
    if st.button("行と列のパリティビットを計算する", key="calc_2d_parity"):
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
        
        # 結果表示
        st.success("パリティビットを計算しました！")
        df_with_parity = pd.DataFrame(
            matrix_with_parity,
            columns=['列1', '列2', '列3', '列4', '行パリティ'],
            index=['行1', '行2', '行3', '行4', '列パリティ']
        )
        st.dataframe(df_with_parity, use_container_width=False)
    
    # ステップ2: 通信エラーの発生
    if st.session_state.matrix_with_parity is not None:
        st.markdown("### ステップ2: 通信エラーの発生")
        st.markdown("先ほどと同じように、データ部分のビットを1つだけクリックしてエラーを発生させてみよう。")
        
        # ビット反転インターフェース（4x4グリッド）
        for i in range(4):
            cols = st.columns(4)
            for j in range(4):
                with cols[j]:
                    current_bit = st.session_state.data_matrix[i][j]
                    if st.button(f"{current_bit}", key=f"matrix_bit_{i}_{j}", help=f"行{i+1}, 列{j+1}"):
                        # ビット反転
                        st.session_state.data_matrix[i][j] = 1 - current_bit
                        st.session_state.error_row = i
                        st.session_state.error_col = j
        
        if st.session_state.error_row != -1:
            st.info(f"行{st.session_state.error_row + 1}, 列{st.session_state.error_col + 1}のビットを反転させました！")
        
        # ステップ3: エラーの検出・特定・訂正
        st.markdown("### ステップ3: エラーの検出・特定・訂正")
        if st.button("エラーをチェックして訂正する", key="check_2d"):
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
                st.error(f"🚨 エラーを発見！{error_row + 1}行目と{error_col + 1}列目が交差するビットが怪しいぞ！")
                
                # エラービットをハイライト表示
                highlight_matrix = []
                for i in range(4):
                    row = []
                    for j in range(4):
                        if i == error_row and j == error_col:
                            row.append(f"**{matrix[i][j]}**")  # エラービットをハイライト
                        elif i == error_row or j == error_col:
                            row.append(f"*{matrix[i][j]}*")  # エラー行・列を斜体
                        else:
                            row.append(str(matrix[i][j]))
                    highlight_matrix.append(row)
                
                highlight_df = pd.DataFrame(
                    highlight_matrix,
                    columns=['列1', '列2', '列3', '列4'],
                    index=['行1', '行2', '行3', '行4']
                )
                st.dataframe(highlight_df, use_container_width=False)
                
                # エラー訂正
                if st.button("エラーを訂正する", key="correct_error"):
                    st.session_state.data_matrix[error_row][error_col] = 1 - st.session_state.data_matrix[error_row][error_col]
                    st.success("✅ エラービットを特定し、訂正しました！")
                    
                    # 訂正後のデータ表示
                    corrected_df = pd.DataFrame(st.session_state.data_matrix)
                    st.dataframe(corrected_df, use_container_width=False)
                    
                    # 状態リセット
                    st.session_state.error_row = -1
                    st.session_state.error_col = -1
            else:
                st.success("✅ エラーは検知されませんでした。")

# 学習のまとめ
st.markdown("---")
st.markdown("## 🎓 学習のまとめ")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 1次元パリティチェック
    - ✅ 1ビットエラーの**検出**が可能
    - ❌ エラーの**場所特定**は不可能
    - ❌ エラーの**訂正**は不可能
    - 💡 簡単で高速な実装
    """)

with col2:
    st.markdown("""
    ### 2次元パリティチェック
    - ✅ 1ビットエラーの**検出**が可能
    - ✅ エラーの**場所特定**が可能
    - ✅ エラーの**訂正**が可能
    - 💡 より複雑だが強力な手法
    """)

st.markdown("""
### 💡 実世界での応用
- **コンピュータメモリ**: ECCメモリでデータ保護
- **通信システム**: インターネットやWi-Fiでのデータ伝送
- **ストレージ**: ハードディスクやSSDでのデータ保護
- **QRコード**: 汚れや破損があっても読み取り可能

パリティチェックは、私たちの身の回りの多くの技術で使われている重要な仕組みです！
""")

# 追加の学習リソース
with st.expander("🔗 さらに学びたい方へ"):
    st.markdown("""
    ### より高度なエラー訂正符号
    - **ハミング符号**: より効率的な1ビットエラー訂正
    - **リード・ソロモン符号**: 複数ビットエラー訂正（CD、DVD、QRコードなど）
    - **LDPC符号**: 現代の通信システムで使用される高性能符号
    
    ### 実験してみよう
    - 2ビット以上のエラーを発生させたときの動作を確認
    - より大きなデータブロック（8x8など）での2次元パリティ
    - 奇数パリティでの2次元パリティチェック
    """)
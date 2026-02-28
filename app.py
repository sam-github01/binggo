import streamlit as st
import time
import random
import base64
import os

# --- 頁面與版面設定 ---
st.set_page_config(page_title="幸運大抽獎", page_icon="🎉", layout="wide")

# --- 自定義 CSS 與 音效函數 ---
def autoplay_audio(file_path):
    """將音效檔轉為 Base64 並透過 HTML 自動播放"""
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <audio autoplay="true">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
            st.markdown(md, unsafe_allow_html=True)

# 設計右側抽獎區的專屬視覺樣式
st.markdown("""
    <style>
    .big-font { font-size: 180px !important; font-weight: bold; color: #E74C3C; text-align: center; margin: 0; line-height: 1.2; }
    .status-text { font-size: 40px !important; text-align: center; color: #2C3E50; font-weight: bold; }
    .draw-box { 
        border: 5px solid #E74C3C; 
        border-radius: 20px; 
        padding: 50px; 
        background-color: #FDFEFE; 
        min-height: 600px; 
        display: flex; 
        flex-direction: column; 
        justify-content: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .history-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
    }
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎊 幸運大抽獎系統")
st.divider()

# --- 狀態管理 (Session State) ---
if 'drawing' not in st.session_state:
    st.session_state.drawing = False
if 'show_result' not in st.session_state:
    st.session_state.show_result = False
if 'final_number' not in st.session_state:
    st.session_state.final_number = None
# 新增：紀錄已抽出的號碼清單
if 'drawn_numbers' not in st.session_state:
    st.session_state.drawn_numbers = []

# --- 版面切割：左側 1 份寬度，右側 2.5 份寬度 ---
col_left, col_right = st.columns([1, 2.5])

# === 左側：控制面板 ===
with col_left:
    st.subheader("⚙️ 抽獎設定")
    min_val = st.number_input("最小號碼", value=1, step=1)
    max_val = st.number_input("最大號碼", value=100, step=1)
    
    # 計算目前還可以抽的號碼池 (總範圍排除已抽出的號碼)
    available_numbers = [num for num in range(min_val, max_val + 1) if num not in st.session_state.drawn_numbers]
    
    st.write("<br>", unsafe_allow_html=True)
    
    # 開始抽獎按鈕
    if st.button("🚀 開始抽獎", use_container_width=True, type="primary"):
        if min_val >= max_val:
            st.error("最大值必須大於最小值！")
        elif not available_numbers:
            # 防呆機制：如果號碼抽完了，跳出警告
            st.warning("此範圍內的號碼已全數抽出！請調整範圍或清除紀錄。")
        else:
            st.session_state.drawing = True
            st.session_state.show_result = False
    
    # 再次抽獎按鈕
    if st.session_state.show_result:
        st.write("<br>", unsafe_allow_html=True)
        if st.button("🔄 繼續下一抽", use_container_width=True):
            st.session_state.show_result = False
            st.session_state.drawing = False
            st.session_state.final_number = None
            st.rerun()

    # --- 顯示抽獎紀錄 ---
    st.markdown('<div class="history-box">', unsafe_allow_html=True)
    st.markdown(f"**📊 剩餘可抽數量：** {len(available_numbers)} 個")
    st.markdown("**📜 已抽出號碼：**")
    
    if st.session_state.drawn_numbers:
        # 將串列中的數字轉成字串，並用逗號隔開顯示
        drawn_str = ", ".join(map(str, st.session_state.drawn_numbers))
        st.info(drawn_str)
        
        # 清除紀錄按鈕
        if st.button("🗑️ 清除所有紀錄", use_container_width=True):
            st.session_state.drawn_numbers = []
            st.session_state.show_result = False
            st.session_state.drawing = False
            st.session_state.final_number = None
            st.rerun()
    else:
        st.write("尚無紀錄")
    st.markdown('</div>', unsafe_allow_html=True)


# === 右側：獨立大畫面的抽獎展示區 ===
with col_right:
    st.markdown('<div class="draw-box">', unsafe_allow_html=True)
    display_placeholder = st.empty()
    
    if st.session_state.drawing:
        # 1. 播放緊張感音樂
        autoplay_audio("drumroll.mp3")
        
        # 2. 執行 3 秒的隨機跳動動畫 (只從「還沒被抽過」的號碼池裡跳動)
        start_time = time.time()
        while time.time() - start_time < 3:
            # 從可用的號碼中隨機挑選作為動畫效果
            random_num = random.choice(available_numbers) 
            with display_placeholder.container():
                st.markdown('<p class="status-text">👉 抽獎進行中...</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="big-font">{random_num}</p>', unsafe_allow_html=True)
            time.sleep(0.08)
        
        # 3. 決定最終號碼，並存入「已抽出清單」
        st.session_state.final_number = random.choice(available_numbers)
        st.session_state.drawn_numbers.append(st.session_state.final_number)
        
        # 狀態切換
        st.session_state.drawing = False
        st.session_state.show_result = True
        st.rerun() # 強制重整頁面以顯示最終結果

    elif st.session_state.show_result:
        # 4. 顯示最終結果與慶祝音效
        with display_placeholder.container():
            st.balloons()
            autoplay_audio("win.mp3")
            st.markdown('<p class="status-text">🎊 恭喜幸運得主 🎊</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="big-font">{st.session_state.final_number}</p>', unsafe_allow_html=True)
    else:
        # 5. 初始待機畫面
        with display_placeholder.container():
            st.markdown('<p class="status-text">準備就緒，請點擊左側開始</p>', unsafe_allow_html=True)
            st.markdown('<p class="big-font">?</p>', unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)

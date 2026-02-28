import streamlit as st
import time
import random
import os

# --- 頁面與版面設定 ---
st.set_page_config(page_title="幸運大抽獎", page_icon="🎉", layout="wide")

# 設計專屬視覺樣式，並隱藏 Streamlit 原生音樂播放器
st.markdown("""
    <style>
    /* 【關鍵黑科技 1】隱藏 Streamlit 的原生音樂播放器介面 */
    [data-testid="stAudio"] {
        display: none !important;
    }
    
    /* 調整主容器上方空白 */
    .block-container { padding-top: 2rem; }
    
    /* 左側歷史紀錄框樣式 */
    .history-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-top: 20px; margin-bottom: 20px; }
    
    /* 抽獎框樣式 */
    .draw-box { 
        border: 5px solid #E74C3C; border-radius: 20px; padding: 50px; background-color: #FDFEFE; 
        min-height: 550px; display: flex; flex-direction: column; justify-content: center; align-items: center; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.1); margin-top: 10px;
    }
    .status-text { font-size: 40px !important; text-align: center; color: #2C3E50; font-weight: bold; margin-bottom: 20px;}
    .big-font { font-size: 180px !important; font-weight: bold; color: #E74C3C; text-align: center; margin: 0; line-height: 1.2; }
    
    /* 放大右側開始抽獎按鈕 */
    div.stButton > button.kind-primary { font-size: 24px; font-weight: bold; height: 60px; }
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
if 'drawn_numbers' not in st.session_state:
    st.session_state.drawn_numbers = []

def render_draw_box(status_text, number_text):
    return f"""
    <div class="draw-box">
        <div class="status-text">{status_text}</div>
        <div class="big-font">{number_text}</div>
    </div>
    """

# --- 版面切割 ---
col_left, col_right = st.columns([1, 2.5])

# === 左側：控制面板 ===
with col_left:
    st.subheader("⚙️ 抽獎設定")
    min_val = st.number_input("最小號碼", value=1, step=1)
    max_val = st.number_input("最大號碼", value=100, step=1)
    
    available_numbers = [num for num in range(min_val, max_val + 1) if num not in st.session_state.drawn_numbers]
    
    st.markdown('<div class="history-box">', unsafe_allow_html=True)
    st.markdown(f"**📊 剩餘可抽數量：** {len(available_numbers)} 個")
    st.markdown("**📜 已抽出號碼：**")
    
    if st.session_state.drawn_numbers:
        drawn_str = ", ".join(map(str, st.session_state.drawn_numbers))
        st.info(drawn_str)
    else:
        st.write("尚無紀錄")
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)
    if st.button("✅ 完成此輪抽獎", use_container_width=True):
        st.session_state.drawn_numbers = []
        st.session_state.show_result = False
        st.session_state.drawing = False
        st.session_state.final_number = None
        st.rerun()

# === 右側：獨立大畫面的抽獎展示區 ===
with col_right:
    if not st.session_state.drawing:
        btn_text = "🚀 繼續抽獎" if st.session_state.show_result else "🚀 開始抽獎"
        
        if st.button(btn_text, use_container_width=True, type="primary"):
            if min_val >= max_val:
                st.error("最大值必須大於最小值！")
            elif not available_numbers:
                st.warning("此範圍內的號碼已全數抽出！請完成此輪抽獎或調整範圍。")
            else:
                st.session_state.drawing = True
                st.session_state.show_result = False
                st.rerun()

    # 【關鍵黑科技 2】建立一個「固定位置」的佔位符給音樂播放器！
    # 這樣系統在切換音樂時，只會替換裡面的音檔(src)，而不會把整個播放器刪掉重做。
    # 這是讓手機瀏覽器保持授權記憶的終極關鍵！
    audio_placeholder = st.empty()
    
    display_placeholder = st.empty()
    
    if st.session_state.drawing:
        # 播放鼓聲
        if os.path.exists("drumroll.mp3"):
            with audio_placeholder:
                st.audio("drumroll.mp3", autoplay=True)
        
        start_time = time.time()
        while time.time() - start_time < 2.5:
            random_num = random.choice(available_numbers) 
            display_placeholder.markdown(render_draw_box("👉 抽獎進行中...", random_num), unsafe_allow_html=True)
            time.sleep(0.08)
        
        st.session_state.final_number = random.choice(available_numbers)
        st.session_state.drawn_numbers.append(st.session_state.final_number)
        
        st.session_state.drawing = False
        st.session_state.show_result = True
        st.rerun() 

    elif st.session_state.show_result:
        # 播放歡呼聲 (在同一個固定位置替換音檔，手機一定播得出來！)
        if os.path.exists("win.mp3"):
            with audio_placeholder:
                st.audio("win.mp3", autoplay=True)
                
        st.balloons()
        display_placeholder.markdown(render_draw_box("🎊 恭喜幸運得主 🎊", st.session_state.final_number), unsafe_allow_html=True)
        
    else:
        display_placeholder.markdown(render_draw_box("準備就緒，請點擊上方按鈕開始", "?"), unsafe_allow_html=True)

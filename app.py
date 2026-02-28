import streamlit as st
import time
import random
import base64
import os

# --- 頁面與版面設定 ---
st.set_page_config(page_title="幸運大抽獎", page_icon="🎉", layout="wide")

# --- 自定義 CSS 與 音效函數 ---
def autoplay_audio(file_path, muted=False):
    """
    優化版音效播放：
    加入靜音參數(muted)，用來在點擊瞬間騙過手機瀏覽器的自動播放限制，取得播放權限！
    """
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            
            # 產生獨一無二的時間戳記
            unique_id = int(time.time() * 1000)
            
            # 如果設定為 muted，就加入靜音屬性
            mute_attr = "muted" if muted else ""
            
            # 直接渲染回純 HTML5 的 audio 標籤
            md = f"""
                <div id="audio_box_{unique_id}" style="display:none;">
                    <audio autoplay="true" playsinline="true" preload="auto" {mute_attr}>
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    </audio>
                </div>
            """
            st.markdown(md, unsafe_allow_html=True)

# 設計專屬視覺樣式
st.markdown("""
    <style>
    /* 調整主容器上方空白 */
    .block-container { padding-top: 2rem; }
    
    /* 左側歷史紀錄框樣式 */
    .history-box {
        background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-top: 20px; margin-bottom: 20px;
    }
    
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

    display_placeholder = st.empty()
    
    if st.session_state.drawing:
        # 1. 播放緊張感音樂
        autoplay_audio("drumroll.mp3")
        
        # 2. 【關鍵黑科技】在按鈕按下的安全時間內，偷偷「靜音」播放一次歡呼聲，解鎖手機權限！
        autoplay_audio("win.mp3", muted=True)
        
        # 3. 縮短跳動時間為 2.5 秒，確保不會超過瀏覽器的有效點擊時限
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
        # 4. 顯示最終結果與慶祝音效 (此時手機已經授權，保證播得出來)
        st.balloons()
        autoplay_audio("win.mp3")
        display_placeholder.markdown(render_draw_box("🎊 恭喜幸運得主 🎊", st.session_state.final_number), unsafe_allow_html=True)
        
    else:
        display_placeholder.markdown(render_draw_box("準備就緒，請點擊上方按鈕開始", "?"), unsafe_allow_html=True)

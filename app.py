import streamlit as st
import time
import random
import base64
import os

# --- 頁面與版面設定 ---
st.set_page_config(page_title="幸運大抽獎", page_icon="🎉", layout="wide")

# --- 自定義 CSS 與 音效函數 ---
def autoplay_audio(file_path):
    """將音效檔轉為 Base64 並透過 HTML 自動播放 (加入強力強制重整機制)"""
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            
            # 產生隨機數字，強迫 Streamlit 判定這是一段「全新」的程式碼
            unique_id = random.randint(1, 10000000)
            
            # 破解技巧：把隨機數字當作純文字塞在隱藏的區塊中。
            # 這樣 HTML 字串保證每次都不一樣，瀏覽器就會乖乖地重新觸發 autoplay！
            md = f"""
                <div style="display:none;">
                    <audio autoplay="autoplay">
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    </audio>
                    <span class="force-update">{unique_id}</span>
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
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    
    /* 抽獎框樣式 */
    .draw-box { 
        border: 5px solid #E74C3C; 
        border-radius: 20px; 
        padding: 50px; 
        background-color: #FDFEFE; 
        min-height: 550px; 
        display: flex; 
        flex-direction: column; 
        justify-content: center;
        align-items: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        margin-top: 10px;
    }
    .status-text { font-size: 40px !important; text-align: center; color: #2C3E50; font-weight: bold; margin-bottom: 20px;}
    .big-font { font-size: 180px !important; font-weight: bold; color: #E74C3C; text-align: center; margin: 0; line-height: 1.2; }
    
    /* 放大右側開始抽獎按鈕 */
    div.stButton > button.kind-primary {
        font-size: 24px;
        font-weight: bold;
        height: 60px;
    }
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

# --- 輔助函數：用來產生右側完整的 HTML 畫面 ---
def render_draw_box(status_text, number_text):
    return f"""
    <div class="draw-box">
        <div class="status-text">{status_text}</div>
        <div class="big-font">{number_text}</div>
    </div>
    """

# --- 版面切割：左側 1 份寬度，右側 2.5 份寬度 ---
col_left, col_right = st.columns([1, 2.5])

# === 左側：控制面板 ===
with col_left:
    st.subheader("⚙️ 抽獎設定")
    min_val = st.number_input("最小號碼", value=1, step=1)
    max_val = st.number_input("最大號碼", value=100, step=1)
    
    # 計算目前還可以抽的號碼池
    available_numbers = [num for num in range(min_val, max_val + 1) if num not in st.session_state.drawn_numbers]
    
    # 顯示抽獎紀錄
    st.markdown('<div class="history-box">', unsafe_allow_html=True)
    st.markdown(f"**📊 剩餘可抽數量：** {len(available_numbers)} 個")
    st.markdown("**📜 已抽出號碼：**")
    
    if st.session_state.drawn_numbers:
        # 將已抽出的號碼用逗號隔開顯示
        drawn_str = ", ".join(map(str, st.session_state.drawn_numbers))
        st.info(drawn_str)
    else:
        st.write("尚無紀錄")
    st.markdown('</div>', unsafe_allow_html=True)

    # 左側最下方：完成此輪抽獎 (清除紀錄功能)
    st.write("<br>", unsafe_allow_html=True)
    if st.button("✅ 完成此輪抽獎", use_container_width=True):
        # 狀態全數重置，並清空已抽出號碼的紀錄
        st.session_state.drawn_numbers = []
        st.session_state.show_result = False
        st.session_state.drawing = False
        st.session_state.final_number = None
        st.rerun()


# === 右側：獨立大畫面的抽獎展示區 ===
with col_right:
    # 只要不是在「抽獎動畫中」，右側上方就會顯示抽獎按鈕
    if not st.session_state.drawing:
        # 根據狀態決定按鈕文字
        btn_text = "🚀 繼續抽獎" if st.session_state.show_result else "🚀 開始抽獎"
        
        if st.button(btn_text, use_container_width=True, type="primary"):
            if min_val >= max_val:
                st.error("最大值必須大於最小值！")
            elif not available_numbers:
                st.warning("此範圍內的號碼已全數抽出！請完成此輪抽獎或調整範圍。")
            else:
                st.session_state.drawing = True
                st.session_state.show_result = False
                st.rerun() # 觸發重新渲染，進入抽獎動畫狀態

    # 建立一個佔位符用來顯示抽獎框
    display_placeholder = st.empty()
    
    if st.session_state.drawing:
        # 1. 播放緊張感音樂
        autoplay_audio("drumroll.mp3")
        #autoplay_audio("win.mp3")
        
        # 2. 執行 3 秒的隨機跳動動畫
        start_time = time.time()
        while time.time() - start_time < 3:
            random_num = random.choice(available_numbers) 
            display_placeholder.markdown(render_draw_box("👉 抽獎進行中...", random_num), unsafe_allow_html=True)
            time.sleep(0.08)
        
        # 3. 決定最終號碼並存入紀錄
        st.session_state.final_number = random.choice(available_numbers)
        st.session_state.drawn_numbers.append(st.session_state.final_number)
        
        # 狀態切換並重整
        st.session_state.drawing = False
        st.session_state.show_result = True
        #autoplay_audio("win.mp3")
        st.rerun() 

    elif st.session_state.show_result:
        # 4. 顯示最終結果與慶祝音效
        st.balloons()
        autoplay_audio("win.mp3")
        display_placeholder.markdown(render_draw_box("🎊 恭喜幸運得主 🎊", st.session_state.final_number), unsafe_allow_html=True)
        # 產生隨機數字，強迫 Streamlit 判定這是一段「全新」的程式碼
        unique_id = random.randint(1, 10000000)
            
        # 破解技巧：把隨機數字當作純文字塞在隱藏的區塊中。
        # 這樣 HTML 字串保證每次都不一樣，瀏覽器就會乖乖地重新觸發 autoplay！
        md = f"""
            <div style="display:none;">
                <audio autoplay="autoplay">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                <span class="force-update">{unique_id}</span>
            </div>
            """
        st.markdown(md, unsafe_allow_html=True)
    else:
        # 5. 初始待機畫面
        display_placeholder.markdown(render_draw_box("準備就緒，請點擊上方按鈕開始", "?"), unsafe_allow_html=True)

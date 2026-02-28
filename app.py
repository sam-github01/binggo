import streamlit as st
import time
import random
import base64

# --- 頁面設定 ---
st.set_page_config(page_title="幸運大抽獎", page_icon="🎉", layout="centered")

# --- 自定義 CSS 與 音效函數 ---
def autoplay_audio(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# 讓畫面更漂亮的 CSS
st.markdown("""
    <style>
    .big-font { font-size:120px !important; font-weight: bold; color: #FF4B4B; text-align: center; }
    .status-text { font-size:30px !important; text-align: center; color: #FAFAFA; }
    .stButton>button { width: 100%; height: 3em; font-size: 20px; background-color: #FF4B4B; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 主程式邏輯 ---
st.title("🎊 幸運大抽獎系統")

# 輸入區域
with st.expander("抽獎設定", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        min_val = st.number_input("最小號碼", value=1, step=1)
    with col2:
        max_val = st.number_input("最大號碼", value=100, step=1)

# 初始化 Session State (用來控制按鈕與再次抽獎)
if 'drawing' not in st.session_state:
    st.session_state.drawing = False

if st.button("🚀 開始抽獎") or st.session_state.drawing:
    if min_val >= max_val:
        st.error("錯誤：最大值必須大於最小值！")
    else:
        st.session_state.drawing = True
        
        # 1. 播放緊張感音樂 (請準備 drumroll.mp3)
        try:
            autoplay_audio("drumroll.mp3")
        except:
            st.warning("提醒：未偵測到 drumroll.mp3 音訊檔")

        # 2. 模擬 3 秒隨機跳號動畫
        placeholder = st.empty() # 建立一個空容器來更新內容
        start_time = time.time()
        
        while time.time() - start_time < 3:
            random_num = random.randint(min_val, max_val)
            with placeholder.container():
                st.markdown(f'<p class="status-text">計算中...</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="big-font">{random_num}</p>', unsafe_allow_html=True)
            time.sleep(0.08) # 控制跳動速度

        # 3. 產出最終結果
        result = random.randint(min_val, max_val)
        placeholder.empty() # 清除動畫內容
        
        # 顯示最終大畫面
        st.balloons() # Streamlit 內建慶祝氣球
        st.markdown(f'<p class="status-text">🎊 恭喜中獎者 🎊</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="big-font">{result}</p>', unsafe_allow_html=True)
        
        # 4. 播放得獎音樂 (請準備 win.mp3)
        try:
            autoplay_audio("win.mp3")
        except:
            pass

        # 再次抽獎按鈕
        if st.button("🔄 再次抽獎"):
            st.session_state.drawing = False
            st.rerun()

# --- 頁尾裝飾 ---
st.divider()
st.caption("Designed with Streamlit | 2026 抽獎活動專用")

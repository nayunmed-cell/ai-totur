import streamlit as st
import google.generativeai as genai

# 1. 页面配置
st.title("🧠 真正有记忆的 AI 助手")

# 2. 配置 API Key (记得替换!)
genai.configure(api_key="AIzaSyCIKfyIAA304m78JQyZMKE3GEHOW3Ce6MM")
model = genai.GenerativeModel('gemini-2.5-flash')

# 3. 初始化聊天历史 (这是一个简单的列表，专门用来存文本)
# 只要网页不关，这个列表就在
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. 在网页上画出历史记录
# 每次刷新，先把它画出来
for msg in st.session_state.messages:
    # 这里的 msg["role"] 是 'user' 或 'assistant'
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 5. 处理新的输入
if prompt := st.chat_input("Hi..."):
    # A. 先把用户的这句话画出来，并存进我们的列表
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # B. 关键步骤：构建 AI 能看懂的“历史档案”
    # 我们要把 Streamlit 的格式 (user/assistant) 转换成 Gemini 的格式 (user/model)
    gemini_history = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})
    
    # C. 调用 AI
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            # 这里的魔法是：我们不直接发一句话
            # 而是开启一个新聊天，把刚才整理好的【全部历史】瞬间塞给它
            # 这样它就“想起”了一切
            chat = model.start_chat(history=gemini_history)
            
            # 因为 history 里已经包含了你刚才说的话，
            # 所以这里我们其实不需要再 send_message(prompt)，
            # 但因为 start_chat 的 history 不包含“当前这一轮的触发”，
            # 我们刚才只是把 prompt 存进了 history 列表里用来构建上下文。
            # 稍等，为了逻辑最简单，我们把 prompt 从 gemini_history 里拿出来发。
            
            # 修正逻辑：
            # 1. 历史记录 = 除了刚才那句 prompt 之外的所有记录
            history_input = gemini_history[:-1] 
            # 2. 启动带有旧记忆的聊天
            chat = model.start_chat(history=history_input)
            # 3. 发送最新的一句话
            response = chat.send_message(prompt)
            
            st.write(response.text)
    
    # D. 把 AI 的回复也存进我们的列表
    st.session_state.messages.append({"role": "assistant", "content": response.text})
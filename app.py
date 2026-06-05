# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 19:06:53 2026

@author: USER
"""

import streamlit as st
import pandas as pd
import os
import json
from google import genai
from google.genai import types

# 頁面設定
st.set_page_config(
    page_title="AI匹克球課程管理系統",
    page_icon="🎓",
    layout="wide" # 改為寬螢幕佈局，左邊選單、右邊內容更專業
)

# ==================== 0. API 與 資料庫設定 ====================
# 💡 如果你有 Gemini API Key，請填入下方引號中。若留空，系統會自動切換為「模擬測試模式」
GEMINI_API_KEY = "" 

# 初始化 Excel 檔案
courses_file = "ai_courses.xlsx"     # 儲存 AI 生成過的課程
students_file = "students.xlsx"       # 儲存學員資料
schedule_file = "schedule.xlsx"       # 儲存課表

for f, cols in [
    (courses_file, ["課程ID", "課程名稱", "主題", "年齡層", "大綱", "流程", "教材"]),
    (students_file, ["姓名", "性別", "年齡"]),
    (schedule_file, ["課程名稱", "日期", "時間", "教師"])
]:
    if not os.path.exists(f):
        pd.DataFrame(columns=cols).to_excel(f, index=False)


# AI 生成函數
def ask_gemini_for_course(topic, age_group, duration, goal):
    """呼叫 Gemini API 生成匹克球課程，若無 API Key 則使用模擬數據"""
    if not GEMINI_API_KEY:
        # 模擬模式：回傳預設的 JSON 結構
        return {
            "課程名稱": f"【{age_group}專屬】{topic}核心強化班",
            "大綱": f"本課程專為{age_group}設計，核心目標為：{goal}。",
            "流程": "1. 熱身運動與關節活動 (10 mins)\n2. 正背面擊球控球基礎練習 (20 mins)\n3. 實戰配對對打與走位引導 (20 mins)\n4. 放鬆伸展與今日表現檢討 (10 mins)",
            "教材": "匹克球拍、高彈性匹克球、標誌錐、移動式網架"
        }
    
    # 實際呼叫 API
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = f"""
        你是一位專業的匹克球(Pickleball)教練。請針對以下需求設計一堂結構完整的課程：
        - 課程主題：{topic}
        - 對象年齡層：{age_group}
        - 上課時間：{duration}
        - 課程目標：{goal}
        
        請嚴格以 JSON 格式回傳，且結構必須完全符合下方欄位（不要包含任何 ```json 或 markdown 標記）：
        {{
            "課程名稱": "好記且吸引人的課程名字",
            "大綱": "一句話總結課程大綱",
            "流程": "詳細的教學流程與時間分配",
            "教材": "這堂課需要準備的球具或輔助道具"
        }}
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        # 解析 JSON
        clean_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(clean_text)
    except Exception as e:
        st.error(f"AI 生成出錯，已自動切換為模擬數據。錯誤訊息: {e}")
        return {
            "課程名稱": f"【生成失敗備用】{topic}訓練班",
            "大綱": goal,
            "流程": "請手動填寫流程",
            "教材": "基礎匹克球裝備"
        }

# ==================== 1. 側邊導覽選單 ====================
st.sidebar.title("🏓 系統導覽選單")
menu = ["🤖 AI 課程生成", "👨‍🎓 學員資料管理", "📅 課表時程管理"]
choice = st.sidebar.selectbox("切換功能頁面", menu)

if not GEMINI_API_KEY:
    st.sidebar.warning("⚠️ 目前處於「AI 模擬測試模式」，若要真正串接 AI，請在程式碼中填入 GEMINI_API_KEY。")

# ==================== 頁面 1：🤖 AI 課程生成 ====================
if choice == "🤖 AI 課程生成":
    st.title("🤖 AI 匹克球課程智能生成")
    st.caption("輸入教學目標，讓 AI 為你量身打造專屬的匹克球教案，並自動儲存至課程庫中。")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 填寫課程需求")
        topic = st.text_input("課程主題", placeholder="例如：第三拍下墜球 (Third Shot Drop) / 網前截擊")
        age_group = st.selectbox("目標年齡層", ["兒童 (6-12歲)", "青少年 (13-18歲)", "成人 (19-50歲)", "樂齡 (50歲以上)"])
        duration = st.text_input("上課時間長度", placeholder="例如：60 分鐘 / 1.5 小時")
        goal = st.text_area("這堂課的教學目標", placeholder="例如：讓學員掌握下墜球的拋物線，並能穩定打入對手廚房區(Kitchen)")
        
        generate_btn = st.button("開始 AI 智能生成 🚀", use_container_width=True)
        
    with col2:
        st.subheader("✨ AI 教案生成結果")
        if generate_btn:
            if not topic or not duration or not goal:
                st.warning("請填寫所有欄位再進行生成！")
            else:
                with st.spinner("AI 教練正在寫教案中，請稍候..."):
                    ai_res = ask_gemini_for_course(topic, age_group, duration, goal)
                    
                    # 顯示結果
                    st.success("🎉 教案生成成功！")
                    st.markdown(f"### 🎯 {ai_res.get('課程名稱', '未命名課程')}")
                    st.markdown(f"**【課程大綱】**\n{ai_res.get('大綱', '')}")
                    st.markdown(f"**【所需教材】**\n{ai_res.get('教材', '')}")
                    st.text_area("**【教學流程與時間分配】**", ai_res.get('流程', ''), height=180)
                    
                    # 寫入 Excel 歷史紀錄
                    old_courses = pd.read_excel(courses_file)
                    new_course_df = pd.DataFrame([{
                        "課程ID": f"C{len(old_courses)+1:03d}",
                        "課程名稱": ai_res.get('課程名稱', '未命名課程'),
                        "主題": topic,
                        "年齡層": age_group,
                        "大綱": ai_res.get('大綱', ''),
                        "流程": ai_res.get('流程', ''),
                        "教材": ai_res.get('教材', '')
                    }])
                    pd.concat([old_courses, new_course_df], ignore_index=True).to_excel(courses_file, index=False)
                    st.toast("課表已同步封存至【歷史課程庫】！")

    st.divider()
    st.subheader("📚 歷史 AI 課程庫")
    df_courses = pd.read_excel(courses_file)
    st.dataframe(df_courses, use_container_width=True)

# ==================== 頁面 2：👨‍🎓 學員資料管理 ====================
elif choice == "👨‍🎓 學員資料管理":
    st.title("👨‍🎓 學員資料管理")
    
    name = st.text_input("學員姓名", key="student_name_input")
    gender = st.selectbox("性別", ["男", "女", "其他"], key="student_gender_select")
    age = st.number_input("年齡", min_value=1, max_value=100, value=18, key="student_age_input")

    if st.button("新增學員", key="add_student_btn"):
        if name.strip() == "":
            st.error("請輸入學員姓名！")
        else:
            new_student = pd.DataFrame({"姓名": [name], "性別": [gender], "年齡": [age]})
            old_df = pd.read_excel(students_file)
            pd.concat([old_df, new_student], ignore_index=True).to_excel(students_file, index=False)
            st.success(f"學員 {name} 新增成功！")
            st.rerun()

    st.subheader("目前學員名冊")
    df_students = pd.read_excel(students_file)
    st.dataframe(df_students, use_container_width=True)

# ==================== 頁面 3：📅 課表時程管理 ====================
elif choice == "📅 課表時程管理":
    st.title("📅 課表時程管理")
    
    # 讀取已經由 AI 生成的課程當作下拉選單選項
    df_courses = pd.read_excel(courses_file)
    if df_courses.empty:
        course_options = ["【提示】請先至 AI 頁面生成課程"]
    else:
        course_options = df_courses["課程名稱"].tolist()

    # 輸入欄位
    course_name = st.selectbox("選擇課程名稱（來自 AI 課程庫）", course_options, key="course_name_select")
    course_date = st.date_input("上課日期", key="course_date_input")
    course_time = st.text_input("上課時間（例如：14:00-16:00）", key="course_time_input")
    teacher = st.text_input("教師姓名", key="teacher_name_input")

    if st.button("新增課程排程", key="add_course_btn"):
        if "請先至" in course_name:
            st.error("無法排課：請先去第一個分頁讓 AI 生成一門課程吧！")
        elif teacher.strip() == "" or course_time.strip() == "":
            st.error("請填寫完整的時間與教師姓名！")
        else:
            new_course = pd.DataFrame({
                "課程名稱": [course_name],
                "日期": [str(course_date)],
                "時間": [course_time],
                "教師": [teacher]
            })
            old_schedule = pd.read_excel(schedule_file)
            pd.concat([old_schedule, new_course], ignore_index=True).to_excel(schedule_file, index=False)
            st.success(f"課程《{course_name}》已成功排入課表！")
            st.rerun()

    st.subheader("目前課表一覽")
    df_schedule = pd.read_excel(schedule_file)
    st.dataframe(df_schedule, use_container_width=True)
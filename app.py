import streamlit as st
import pandas as pd
import os
import json
from google import genai

# ==========================
# 頁面設定
# ==========================
st.set_page_config(
    page_title="AI匹克球課程管理系統",
    page_icon="🏓",
    layout="wide"
)

# ==========================
# API Key
# ==========================

# 本機測試請直接填入你的 API Key
GEMINI_API_KEY = "你的API_KEY"

# 如果部署到 Streamlit Cloud，再改成：
# GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# 建立 Client
client = genai.Client(api_key=GEMINI_API_KEY)

# ==========================
# 建立 Excel
# ==========================

courses_file = "ai_courses.xlsx"

if not os.path.exists(courses_file):
    df = pd.DataFrame(
        columns=[
            "課程ID",
            "課程名稱",
            "主題",
            "年齡層",
            "大綱",
            "流程",
            "教材"
        ]
    )
    df.to_excel(courses_file, index=False)


# ==========================
# Gemini 生成函式
# ==========================

def ask_gemini_for_course(topic, age_group, duration, goal):

    prompt = f"""
你是一位專業匹克球教練。

請設計一份完整課程。

課程主題：
{topic}

對象：
{age_group}

上課時間：
{duration}

課程目標：
{goal}

請只回傳 JSON：

{{
"課程名稱":"",
"大綱":"",
"流程":"",
"教材":""
}}
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text

        # 去掉 markdown
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

        result = json.loads(text)

        return result

    except Exception as e:

        st.error(f"AI生成失敗：{e}")

        return {
            "課程名稱": "生成失敗",
            "大綱": "",
            "流程": "",
            "教材": ""
        }


# ==========================
# 側邊欄
# ==========================

st.sidebar.title("🏓 AI匹克球課程管理系統")

menu = [
    "🤖 AI課程生成"
]

choice = st.sidebar.selectbox(
    "功能選單",
    menu
)

# ==========================
# AI課程生成頁面
# ==========================

if choice == "🤖 AI課程生成":

    st.title("🤖 AI匹克球課程生成")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("課程需求")

        topic = st.text_input(
            "課程主題",
            placeholder="例如：第三拍下墜球"
        )

        age_group = st.selectbox(
            "年齡層",
            [
                "兒童",
                "青少年",
                "成人",
                "樂齡"
            ]
        )

        duration = st.text_input(
            "上課時間",
            placeholder="60分鐘"
        )

        goal = st.text_area(
            "教學目標"
        )

        generate_btn = st.button(
            "開始生成"
        )

    with col2:

        st.subheader("AI生成結果")

        if generate_btn:

            with st.spinner("AI教練正在設計課程..."):

                result = ask_gemini_for_course(
                    topic,
                    age_group,
                    duration,
                    goal
                )

            st.success("生成成功")

            st.markdown(
                f"## {result['課程名稱']}"
            )

            st.write("### 課程大綱")
            st.write(result["大綱"])

            st.write("### 所需教材")
            st.write(result["教材"])

            st.write("### 教學流程")
            st.text_area(
                "",
                result["流程"],
                height=250
            )

            # 儲存到 Excel
            old_df = pd.read_excel(courses_file)

            new_df = pd.DataFrame([{
                "課程ID": f"C{len(old_df)+1:03}",
                "課程名稱": result["課程名稱"],
                "主題": topic,
                "年齡層": age_group,
                "大綱": result["大綱"],
                "流程": result["流程"],
                "教材": result["教材"]
            }])

            df = pd.concat(
                [old_df, new_df],
                ignore_index=True
            )

            df.to_excel(
                courses_file,
                index=False
            )

            st.toast("已加入歷史課程庫")

# ==========================
# 顯示歷史課程
# ==========================

st.divider()

st.subheader("📚 歷史課程庫")

df = pd.read_excel(courses_file)

st.dataframe(
    df,
    use_container_width=True
)
students_file = "students.xlsx"
schedule_file = "schedule.xlsx"

# 學員資料
if not os.path.exists(students_file):
    pd.DataFrame(
        columns=[
            "姓名",
            "性別",
            "年齡"
        ]
    ).to_excel(students_file, index=False)

# 課表
if not os.path.exists(schedule_file):
    pd.DataFrame(
        columns=[
            "課程名稱",
            "日期",
            "時間",
            "教師"
        ]
    ).to_excel(schedule_file, index=False)
    
elif choice == "👨‍🎓 學員資料管理":

    st.title("👨‍🎓 學員資料管理")

    name = st.text_input("姓名")

    gender = st.selectbox(
        "性別",
        [
            "男",
            "女"
        ]
    )

    age = st.number_input(
        "年齡",
        min_value=1,
        max_value=100,
        value=18
    )

    if st.button("新增學員"):

        if name == "":

            st.warning("請輸入姓名")

        else:

            old_df = pd.read_excel(
                students_file
            )

            new_student = pd.DataFrame([{
                "姓名": name,
                "性別": gender,
                "年齡": age
            }])

            df = pd.concat(
                [old_df, new_student],
                ignore_index=True
            )

            df.to_excel(
                students_file,
                index=False
            )

            st.success("新增成功")

    st.divider()

    st.subheader("學員名冊")

    df = pd.read_excel(
        students_file
    )

    st.dataframe(
        df,
        use_container_width=True
    )
    
elif choice == "📅 課表時程管理":

    st.title("📅 課表管理")

    course_df = pd.read_excel(
        courses_file
    )

    if len(course_df) == 0:

        st.warning(
            "請先到 AI課程生成建立課程"
        )

    else:

        course_name = st.selectbox(
            "選擇課程",
            course_df["課程名稱"]
        )

        course_date = st.date_input(
            "上課日期"
        )

        course_time = st.text_input(
            "上課時間",
            placeholder="例如：14:00~16:00"
        )

        teacher = st.text_input(
            "教師姓名"
        )

        if st.button("新增課程"):

            old_df = pd.read_excel(
                schedule_file
            )

            new_course = pd.DataFrame([{
                "課程名稱": course_name,
                "日期": str(course_date),
                "時間": course_time,
                "教師": teacher
            }])

            df = pd.concat(
                [old_df, new_course],
                ignore_index=True
            )

            df.to_excel(
                schedule_file,
                index=False
            )

            st.success("新增成功")

    st.divider()

    st.subheader("目前課表")

    df = pd.read_excel(
        schedule_file
    )

    st.dataframe(
        df,
        use_container_width=True
    )
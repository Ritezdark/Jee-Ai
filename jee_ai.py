import streamlit as st
from openai import OpenAI
from streamlit_local_storage import LocalStorage
import json
import os


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="JEE AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# NVIDIA AI
# ============================================================

if "NVIDIA_API_KEY" in st.secrets:
    NVIDIA_API_KEY = st.secrets["NVIDIA_API_KEY"]
else:
    NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")

if not NVIDIA_API_KEY:
    st.error("NVIDIA_API_KEY is not set.")
    st.stop()

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)

TEXT_MODEL = "openai/gpt-oss-20b"
VISION_MODEL = "meta/llama-3.2-90b-vision-instruct"


# ============================================================
# LOCAL BROWSER STORAGE
# ============================================================

localS = LocalStorage()

MEMORY_KEY = "jee_ai_memory_v1"
PROGRESS_KEY = "jee_ai_progress_v1"
CHAT_KEY = "jee_ai_chat_v1"


def load_local(key, default):

    try:
        value = localS.getItem(key)

        if value is None or value == "":
            return default

        if isinstance(value, str):
            return json.loads(value)

        return value

    except Exception:
        return default


def save_local(key, value):

    try:
        localS.setItem(key, json.dumps(value))
    except Exception:
        pass


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = load_local(
        CHAT_KEY,
        []
    )

if "memory" not in st.session_state:
    st.session_state.memory = load_local(
        MEMORY_KEY,
        []
    )

if "progress" not in st.session_state:
    st.session_state.progress = load_local(
        PROGRESS_KEY,
        {
            "questions_attempted": 0,
            "correct": 0,
            "incorrect": 0,
            "tests": 0,
            "topics": []
        }
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🎯 JEE AI")
    st.caption("Your JEE Study Companion")

    st.divider()

    pages = [
        ("🏠", "Home"),
        ("💬", "Ask Doubt"),
        ("📝", "Evaluate Answer"),
        ("🧠", "JEE Coach"),
        ("🎯", "Practice"),
        ("📊", "My Progress"),
        ("🧠", "My Memory")
    ]

    for icon, name in pages:

        if st.button(
            f"{icon}  {name}",
            key=f"nav_{name}",
            use_container_width=True
        ):
            st.session_state.page = name
            st.rerun()

    st.divider()

    st.caption(
        "🔒 Memory and progress are stored in this browser/device."
    )


# ============================================================
# HOME
# ============================================================

if st.session_state.page == "Home":

    st.title("🎯 JEE AI")
    st.subheader("Your personal JEE command center")

    st.write(
        "Study smarter. Solve better. Prepare harder."
    )

    st.divider()

    # Background / hero image
    if os.path.exists("jee_background.png"):

        st.image(
            "jee_background.png",
            use_container_width=True
        )

    else:

        st.info(
            "jee_background.png was not found on the Desktop."
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("💬 Ask Doubt")

        st.write(
            "Ask Physics, Chemistry or Mathematics doubts "
            "and get step-by-step explanations."
        )

        if st.button(
            "Open Ask Doubt →",
            key="home_doubt",
            use_container_width=True
        ):

            st.session_state.page = "Ask Doubt"
            st.rerun()

    with col2:

        st.subheader("🎯 Practice")

        st.write(
            "Generate JEE Main and JEE Advanced style "
            "questions and practice."
        )

        if st.button(
            "Open Practice →",
            key="home_practice",
            use_container_width=True
        ):

            st.session_state.page = "Practice"
            st.rerun()

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Questions",
            st.session_state.progress.get(
                "questions_attempted",
                0
            )
        )

    with col2:
        st.metric(
            "Correct",
            st.session_state.progress.get(
                "correct",
                0
            )
        )

    with col3:
        st.metric(
            "Memories",
            len(st.session_state.memory)
        )


# ============================================================
# ASK DOUBT
# ============================================================

elif st.session_state.page == "Ask Doubt":

    st.title("💬 Ask Doubt")
    st.caption("Your JEE doubt-solving command center.")

    for message in st.session_state.chat_messages:

        with st.chat_message(
            message.get("role", "user")
        ):
            st.markdown(
                message.get("content", "")
            )

    question = st.chat_input(
        "Ask your JEE question..."
    )

    if question:

        st.session_state.chat_messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        save_local(
            CHAT_KEY,
            st.session_state.chat_messages
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:

                    memory_text = ""

                    if st.session_state.memory:

                        memory_text = (
                            "\nStudent memory:\n"
                            + "\n".join(
                                "- " + x
                                for x in st.session_state.memory
                            )
                        )

                    response = client.chat.completions.create(

                        model=TEXT_MODEL,

                        messages=[
                            {
                                "role": "system",
                                "content": f"""
You are JEE AI, an expert JEE Main and
JEE Advanced mentor.

Explain concepts clearly and step-by-step.

Do not blindly give the final answer.
Teach the reasoning.

Use proper mathematical notation.

Focus on:
- Conceptual clarity
- Exam-oriented thinking
- Useful shortcuts
- Common mistakes

{memory_text}
"""
                            },
                            *st.session_state.chat_messages
                        ],

                        temperature=0.2,
                        max_tokens=1800
                    )

                    answer = (
                        response
                        .choices[0]
                        .message
                        .content
                    )

                    st.markdown(answer)

                    st.session_state.chat_messages.append(
                        {
                            "role": "assistant",
                            "content": answer
                        }
                    )

                    save_local(
                        CHAT_KEY,
                        st.session_state.chat_messages
                    )

                except Exception as e:

                    st.error(
                        f"Something went wrong: {e}"
                    )


# ============================================================
# EVALUATE ANSWER
# ============================================================

elif st.session_state.page == "Evaluate Answer":

    st.title("📝 Evaluate Answer")

    st.write(
        "Upload a photo of your handwritten solution "
        "and let JEE AI evaluate it."
    )

    uploaded = st.file_uploader(
        "Upload your solution",
        type=[
            "png",
            "jpg",
            "jpeg",
            "webp"
        ]
    )

    question = st.text_area(
        "Optional: Enter the original question",
        height=120
    )

    if uploaded:

        st.image(
            uploaded,
            caption="Your solution",
            use_container_width=True
        )

        if st.button(
            "🔍 Evaluate My Answer",
            use_container_width=True
        ):

            with st.spinner(
                "Analyzing your solution..."
            ):

                try:

                    image_bytes = uploaded.getvalue()

                    import base64

                    image_b64 = base64.b64encode(
                        image_bytes
                    ).decode()

                    prompt = f"""
You are an expert JEE Main + Advanced evaluator.

Analyze the student's handwritten solution.

Original question:
{question if question else "Not provided."}

Give:

1. Overall verdict
2. Correct steps
3. Mistakes
4. Exact point where the reasoning went wrong
5. Correct approach
6. Final answer if possible
7. Exam tip

Be strict but constructive.

Do not invent information that cannot be read
from the image.
"""

                    response = client.chat.completions.create(

                        model=VISION_MODEL,

                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": prompt
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url":
                                            f"data:image/jpeg;base64,{image_b64}"
                                        }
                                    }
                                ]
                            }
                        ],

                        temperature=0.2,
                        max_tokens=1800
                    )

                    evaluation = (
                        response
                        .choices[0]
                        .message
                        .content
                    )

                    st.subheader(
                        "🔍 Evaluation"
                    )

                    st.markdown(evaluation)

                except Exception as e:

                    st.error(
                        f"Evaluation failed: {e}"
                    )


# ============================================================
# JEE COACH
# ============================================================

elif st.session_state.page == "JEE Coach":

    st.title("🧠 JEE Coach")

    st.write(
        "Tell me what you are struggling with "
        "and I'll help you build a strategy."
    )

    topic = st.text_input(
        "Topic / Chapter"
    )

    problem = st.text_area(
        "What are you struggling with?",
        height=150
    )

    if st.button(
        "🧠 Coach Me",
        use_container_width=True
    ):

        if not topic and not problem:

            st.warning(
                "Tell me at least the topic or problem."
            )

        else:

            with st.spinner(
                "Building your strategy..."
            ):

                try:

                    memory_text = ""

                    if st.session_state.memory:

                        memory_text = (
                            "\nStudent information:\n"
                            + "\n".join(
                                "- " + x
                                for x in st.session_state.memory
                            )
                        )

                    prompt = f"""
You are a JEE preparation coach.

Student topic:
{topic}

Student problem:
{problem}

Give a practical and structured strategy.

Include:

- What to study
- What to revise
- What questions to solve
- Common mistakes
- Short action plan

Avoid generic motivational fluff.

{memory_text}
"""

                    response = client.chat.completions.create(

                        model=TEXT_MODEL,

                        messages=[
                            {
                                "role": "system",
                                "content":
                                "You are an expert JEE mentor."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],

                        temperature=0.3,
                        max_tokens=1600
                    )

                    st.markdown(
                        response
                        .choices[0]
                        .message
                        .content
                    )

                except Exception as e:

                    st.error(
                        f"Coach error: {e}"
                    )


# ============================================================
# PRACTICE
# ============================================================

elif st.session_state.page == "Practice":

    st.title("🎯 Practice Generator")

    col1, col2 = st.columns(2)

    with col1:

        subject = st.selectbox(
            "Subject",
            [
                "Physics",
                "Chemistry",
                "Mathematics"
            ]
        )

    with col2:

        level = st.selectbox(
            "Level",
            [
                "JEE Main",
                "JEE Advanced"
            ]
        )

    topic = st.text_input(
        "Topic / Chapter",
        placeholder="e.g. Kinematics"
    )

    number = st.slider(
        "Number of questions",
        1,
        5,
        3
    )

    if st.button(
        "🎯 Generate Practice",
        use_container_width=True
    ):

        if not topic:

            st.warning(
                "Enter a topic first."
            )

        else:

            with st.spinner(
                "Generating questions..."
            ):

                try:

                    prompt = f"""
Generate {number} high-quality {level}
questions for JEE aspirants.

Subject: {subject}
Topic: {topic}

Return JSON only:

{{
    "questions": [
        {{
            "question": "...",
            "answer": "...",
            "explanation": "..."
        }}
    ]
}}

Make questions original and exam-oriented.
"""

                    response = client.chat.completions.create(

                        model=TEXT_MODEL,

                        messages=[
                            {
                                "role": "system",
                                "content":
                                "Return valid JSON only."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],

                        temperature=0.4,
                        max_tokens=2500,

                        response_format={
                            "type": "json_object"
                        }
                    )

                    data = json.loads(
                        response
                        .choices[0]
                        .message
                        .content
                    )

                    questions = data.get(
                        "questions",
                        []
                    )

                    for i, q in enumerate(
                        questions
                    ):

                        st.subheader(
                            f"Question {i + 1}"
                        )

                        st.write(
                            q.get(
                                "question",
                                "Question unavailable."
                            )
                        )

                        with st.expander(
                            "Show Answer & Explanation"
                        ):

                            st.markdown(
                                "**Answer:**"
                            )

                            st.write(
                                q.get(
                                    "answer",
                                    "Unavailable"
                                )
                            )

                            st.markdown(
                                "**Explanation:**"
                            )

                            st.write(
                                q.get(
                                    "explanation",
                                    "Unavailable"
                                )
                            )

                    st.session_state.progress[
                        "questions_attempted"
                    ] += len(questions)

                    save_local(
                        PROGRESS_KEY,
                        st.session_state.progress
                    )

                except Exception as e:

                    st.error(
                        f"Practice generation failed: {e}"
                    )


# ============================================================
# MY PROGRESS
# ============================================================

elif st.session_state.page == "My Progress":

    st.title("📊 My Progress")

    progress = st.session_state.progress

    attempted = progress.get(
        "questions_attempted",
        0
    )

    correct = progress.get(
        "correct",
        0
    )

    incorrect = progress.get(
        "incorrect",
        0
    )

    tests = progress.get(
        "tests",
        0
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Questions",
            attempted
        )

    with c2:
        st.metric(
            "Correct",
            correct
        )

    with c3:
        st.metric(
            "Incorrect",
            incorrect
        )

    with c4:
        st.metric(
            "Tests",
            tests
        )

    st.divider()

    total = correct + incorrect

    if total > 0:

        accuracy = (
            correct / total
        ) * 100

        st.subheader("📈 Accuracy")

        st.progress(
            min(accuracy / 100, 1.0)
        )

        st.write(
            f"Accuracy: **{accuracy:.1f}%**"
        )

    else:

        st.info(
            "Your accuracy will appear here "
            "after you start recording results."
        )

    st.divider()

    if st.button(
        "🧹 Reset My Progress",
        use_container_width=True
    ):

        st.session_state.progress = {
            "questions_attempted": 0,
            "correct": 0,
            "incorrect": 0,
            "tests": 0,
            "topics": []
        }

        save_local(
            PROGRESS_KEY,
            st.session_state.progress
        )

        st.success(
            "Progress reset."
        )

        st.rerun()


# ============================================================
# MY MEMORY
# ============================================================

elif st.session_state.page == "My Memory":

    st.title("🧠 My Memory")

    st.caption(
        "These memories are stored locally in this browser/device."
    )

    new_memory = st.text_area(
        "Add something JEE AI should remember",
        placeholder=(
            "Example: I prefer step-by-step explanations."
        ),
        height=100
    )

    if st.button(
        "➕ Add Memory",
        use_container_width=True
    ):

        if new_memory.strip():

            st.session_state.memory.append(
                new_memory.strip()
            )

            save_local(
                MEMORY_KEY,
                st.session_state.memory
            )

            st.success(
                "Memory saved on this device."
            )

            st.rerun()

        else:

            st.warning(
                "Write something first."
            )

    st.divider()

    if st.session_state.memory:

        st.subheader(
            "Saved Memories"
        )

        for i, memory in enumerate(
            st.session_state.memory
        ):

            st.write(
                f"**{i + 1}.** {memory}"
            )

            if st.button(
                "🗑️ Delete",
                key=f"delete_memory_{i}"
            ):

                st.session_state.memory.pop(i)

                save_local(
                    MEMORY_KEY,
                    st.session_state.memory
                )

                st.rerun()

        st.divider()

        if st.button(
            "🗑️ Delete All Memories",
            use_container_width=True
        ):

            st.session_state.memory = []

            save_local(
                MEMORY_KEY,
                []
            )

            st.success(
                "All memories deleted from this browser."
            )

            st.rerun()

    else:

        st.info(
            "No memories saved yet."
        )
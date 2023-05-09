import json
import streamlit as st

# Load questions from the JSON file
with open("questions.json", "r") as f:
    if "data" not in st.session_state:
        st.session_state.data = data = json.load(f)
    data = st.session_state.data


questions = data["questions"]

def find_question_by_id(question_id):
    for question in questions:
        if question["id"] == question_id:
            return question
    return None
def find_question_by_title(title):
    return next((question for question in data["questions"] if question["text"] == title), None)

def show_question(question):
    st.write(question["text"])
    choices = question["choices"]

    user_choice = None
    for choice in choices:
        if st.button(choice["text"], key=f'button_{question["id"]}_{choice["id"]}'):
            user_choice = choice["text"]
            break

    return user_choice

def manage_questions():
    if "current_question_id" not in st.session_state:
        st.session_state.current_question_id = 1

    question = find_question_by_id(st.session_state.current_question_id)
    if question is None:
        return

    user_choice = show_question(question)

    if user_choice is not None:
        st.session_state.answers[st.session_state.current_question_id] = user_choice
        for choice in question["choices"]:
            if choice["text"] == user_choice:
                st.session_state.current_question_id = choice["next_question_id"]
                st.experimental_rerun()
                break
            


def display_answered_questions():
    st.sidebar.title("Answered Questions")
    for question_id, answer in st.session_state.answers.items():
        question = find_question_by_id(question_id)
        if st.sidebar.button(f'{question["text"]}: {answer}', key=f'sidebar_{question["id"]}'):
            st.session_state.current_question_id = question_id
            
            # Delete all answers after the clicked one
            for q_id in range(question_id + 1, len(questions) + 1):
                if q_id in st.session_state.answers:
                    del st.session_state.answers[q_id]

            st.experimental_rerun()


def edit_json():
    # st.sidebar.title("Edit JSON")

    # Add a new question form
    with st.form(key="add_question_form"):
        st.write("Add a new question")
        new_question_title = st.text_input("Enter the new question:")

        submit_new_question = st.form_submit_button("Add question")

        if submit_new_question:
            new_question = {
                "id": len(data["questions"]) + 1,
                "text": new_question_title,
                "choices": []
            }
            data["questions"].append(new_question)

    # Add a new choice form
    with st.form(key="add_choice_form"):
        st.write("Add a new choice to a question")
        question_title = st.selectbox("Select the question to add a choice:", [q["text"] for q in data["questions"]])
        choice_text = st.text_input("Enter the choice text:")
        next_question_title = st.selectbox("Select the next question after this choice:", [q["text"] for q in data["questions"]])

        submit_new_choice = st.form_submit_button("Add choice")

        if submit_new_choice:
            choice = {
                "id": len(find_question_by_title(question_title)["choices"]) + 1,
                "text": choice_text,
                "next_question_id": find_question_by_title(next_question_title)["id"],
            }

            find_question_by_title(question_title)["choices"].append(choice)

    if st.button("Display raw JSON content"):
        st.write("Copy the content below and paste it into your JSON file:")
        st.code(json.dumps(data, indent=4))



# Initialize the session state for "answers"
if "answers" not in st.session_state:
    st.session_state.answers = {}

st.title("Pitch.ai")
display_answered_questions()
# Add the new function call to the main section of your code
action = st.sidebar.radio("Action", ("Answer questions", "Edit questions"))

if action == "Answer questions":
    manage_questions()
elif action == "Edit questions":
    edit_json()

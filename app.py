import streamlit as st
from llm import generate_quiz

st.set_page_config(
    page_title="QUIZ",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title(':sunglasses: QUIZ : :blue[\[ 인공지능 서비스 개발 \]]')

if 'outputs' not in st.session_state:
  st.session_state.outputs = generate_quiz()
outputs = st.session_state.outputs

def check_answer():
  st.session_state.answer_submitted = True
  if st.session_state.selected_answer == outputs[st.session_state.quiz_num]['answer'][0]:
    st.session_state.score += int(100 / len(outputs))
 
def next_quiz():
  st.session_state.quiz_num += 1
  st.session_state.answer_submitted = False
  st.session_state.selected_answer = None

def select_option(i):
  st.session_state.selected_answer = i

default_values = {'quiz_num': 0, 'score': 0, 'selected_answer': None, 'answer_submitted': False}
for key, value in default_values.items():
    st.session_state.setdefault(key, value)

progress_text = f"Quiz number : {st.session_state.quiz_num+1} out of {len(outputs)}"
st.metric(label="Score", value=f"{st.session_state.score} / 100")
st.progress((st.session_state.quiz_num+1)*int(100 / len(outputs)), text=progress_text)

quiz_num = st.session_state.quiz_num
option = outputs[quiz_num]['options']
correct_answer = outputs[quiz_num]['answer'][0]

st.header(f"Q{quiz_num+1}: {outputs[quiz_num]['question']}", divider='rainbow')


print(st.session_state['selected_answer'])
if st.session_state.answer_submitted:
  for i in range(len(option)):
    if correct_answer == i:
      st.success(f'[{i+1}] {option[i]} (Correct)')
    elif st.session_state.selected_answer == i:
      st.error(f'[{i+1}] {option[i]} (Incorrect)')
    else:
      st.write(f'[{i+1}] {option[i]}')

  st.markdown('___')

  st.write(f"- 설명 : {outputs[quiz_num]['explanation']}")
  st.write(f"- 출처 : {outputs[quiz_num]['source passage']}")

else:
  for i in range(len(option)):
    st.button(f'[{i+1}] {option[i]}', key=i, on_click=select_option, args=[i])
      

st.markdown('___')

col1, col2, col3 = st.columns([1,1,1])
with col2:
  if st.session_state.answer_submitted:
    if st.session_state.quiz_num < len(outputs) - 1:
      st.button('다음', on_click=next_quiz, use_container_width=True)
    else:
      st.info(f"""Quiz 끝!  
            점수: {st.session_state.score} / 100 
      """)

  else:
    st.button('제출', on_click=check_answer, use_container_width=True)


__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


import streamlit as st
from llm import generate_quiz

# streamlit 웹페이지 제목, 아이콘, 레이아웃 크기 설정
st.set_page_config(
    page_title="QUIZ",
    page_icon="🧊",
    layout="wide",
)

# 상단 제목 설정
st.title(':sunglasses: QUIZ : :blue[\[ 인공지능 서비스 개발 \]]')

# 프로그램 초기 실행 시 LLM에서 퀴즈 목록을 받아옵니다
# 페이지가 리로딩 되어도 퀴즈데이터를 메모리 유지하기 위해 session_state 사용
if 'outputs' not in st.session_state:
  st.session_state.outputs = generate_quiz()
outputs = st.session_state.outputs

# '제출' 버튼을 눌렀을 때 동작
# 사용자가 선택한 옵션과 문제의 정답을 비교하여 score 값 업데이트
def check_answer():
  st.session_state.answer_submitted = True
  if st.session_state.selected_answer == outputs[st.session_state.quiz_num]['answer'][0]:
    st.session_state.score += int(100 / len(outputs))
 
 # '다음' 버튼을 눌렀을 때 동작
 # 다음 퀴즈로 넘어가고, 사용자 선택 옵션 변수 값을 초기화
def next_quiz():
  st.session_state.quiz_num += 1
  st.session_state.answer_submitted = False
  st.session_state.selected_answer = None

# 사용자가 선택한 옵션 값을 저장하는 함수
def select_option(i):
  st.session_state.selected_answer = i

# 초기 설정값을 세팅해주는 부분
default_values = {'quiz_num': 0, 'score': 0, 'selected_answer': None, 'answer_submitted': False}
for key, value in default_values.items():
    st.session_state.setdefault(key, value)

# 프로그레스바 및 현재 문제 상태를 표시
progress_text = f"Quiz number : {st.session_state.quiz_num+1} out of {len(outputs)}"
st.metric(label="Score", value=f"{st.session_state.score} / 100")
st.progress((st.session_state.quiz_num+1)*int(100 / len(outputs)), text=progress_text)

quiz_num = st.session_state.quiz_num
option = outputs[quiz_num]['options']
correct_answer = outputs[quiz_num]['answer'][0]

# 문제를 표시합니다
st.header(f"Q{quiz_num+1}: {outputs[quiz_num]['question']}", divider='rainbow')

# 문제의 보기 옵션을 버튼 형식으로 보여주고, '제출'버튼을 눌렀을 경우 정답과 비교 후 정답 설명 및 문제의 출처를 표기
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

# '제출', '다음' 버튼을 표시하고 모든 문제를 다 풀었을 경우 '점수'를 보여줌
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


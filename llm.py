import os
import re
import json

from langchain import hub
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFDirectoryLoader

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI

import openai
import streamlit as st

def generate_quiz():
  os.environ["OPENAI_API_KEY"] =  st.secrets["OPENAI_API_KEY"]

  llm = ChatOpenAI(model="gpt-3.5-turbo")
  # PDF 자료를 /doc 폴더에 추가, 이미지는 시간이 너무 오래 걸려서 false 처리함
  loader = PyPDFDirectoryLoader("doc/", extract_images=False)

  docs = loader.load()

  print('docs load')
  # 읽은 데이터를 chunk 크기 만큼 쪼갬, 분리한 단어들을 Embedding 작업을 거친 후 Chroma DB 형태로 저장 
  text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
  splits = text_splitter.split_documents(docs)
  text = " ".join([re.sub('\s+', ' ', d.page_content) for d in docs])
  vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

  # DB에 검색할 변수 정의
  retriever = vectorstore.as_retriever()
  prompt = hub.pull("rlm/rag-prompt")


  def format_docs(docs):
      return "\n\n".join(doc.page_content for doc in docs)

  # llm chain 형식으로 관련 질문에 응답을 제대로 하는지 테스트하기 위한 함수 설정
  rag_chain = (
      {"context": retriever | format_docs, "question": RunnablePassthrough()}
      | prompt
      | llm
      | StrOutputParser()
  )

  # 퀴즈 생성을 위한 프롬프트 작성
  question = """
          Write a set of multiple-choice quiz questions with four options each 
          to review and internalise the following information.

          The quiz should be returned in a JSON format so that it can be displayed and undertaken by the user.
          The answer should be a list of integers corresponding to the indices of the correct answers.
          If there is only one correct answer, the answer should be a list of one integer.
          Also return an explanation for each answer, and a quote from the source text to support the answer.

          The goal of the quiz is to provide a revision exercise, 
          so that the user can internalise the information presented in this passage.
          The quiz questions should only cover information explicitly presented in this passage. 
          The number of questions should be 10
          question and options should be in korean plz.

          Sample quiz question:

          {
              "question": "What is the capital of France?",
              "options": ["Paris", "London", "Berlin", "Madrid"],
              "answer": [0],
              "explanation": "Paris is the capital of France",
              "source passage": "SOME PASSAGE EXTRACTED FROM THE INPUT TEXT"
          }

          Sample quiz set:
          
          {
              "quiz": [
                  {
                      "question": "What is the capital of France?",
                      "options": ["Paris", "London", "Berlin", "Madrid"],
                      "answer": [0],
                      "explanation": "Paris is the capital of France",
                      "source passage": "SOME PASSAGE EXTRACTED FROM THE INPUT TEXT"
                  },
                  {
                      "question": "What is the capital of Spain?",
                      "options": ["Paris", "London", "Berlin", "Madrid"],
                      "answer": [3],
                      "explanation": "Madrid is the capital of Spain",
                      "source passage": "SOME PASSAGE EXTRACTED FROM THE INPUT TEXT"
                  }
              ]
          }

          ======= Source Text =======

          """ + text + """

          ======= Questions =======

      """



  SYSTEM_PROMPTS = {
      "Default": {
          "role": "system",
          "content": """
          You are a helpful, intelligent, thoughtful assistant who is a great communicator.
          
          You can communicate complex ideas and concepts in clear, concise language 
          without resorting to domain-specific jargon unless it is entirely necessary.
          
          When you do are not sure of what the answer should be, or whether it is grounded in fact,
          you communicate this to the user to help them make informed decisions
          about how much to trust your outputs. 
          """
      },
  }

  # chat 형식의 프롬프트 작성 후 퀴즈 생성
  completion = openai.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=[
            SYSTEM_PROMPTS["Default"],
            {
                "role": "user",
                "content": question
            }
        ])

  # 만들어진 퀴즈의 json 형태로 변환을 위해 앞뒤로 불필요한 부분 제거
  print('made quiz')
 
  outputs = completion.choices[0].message.content
  outputs = outputs.replace('\n', '')
  left = outputs.find('{')
  right = outputs.rfind('}')
  outputs = outputs[left:right+1]
  quiz_json = json.loads(outputs)["quiz"]
  print(quiz_json)
  print(len(quiz_json))

  # json 형태의 최종 퀴즈 목록 반환
  return quiz_json

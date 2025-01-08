import pandas as pd
import fitz  # PyMuPDF
import json
import os
from io import BytesIO
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import json
import os
from io import BytesIO


# PDF 파일의 모든 페이지 텍스트를 읽어 반환하는 함수
def read_pdf_with_pymupdf(file_bytes):
    """
    PyMuPDF를 사용하여 PDF의 모든 페이지 텍스트를 읽어 반환합니다.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")  # PDF 파일을 바이트 스트림으로 엽니다
    text_list = []
    for page in doc:
        text = page.get_text()
        excluded_start = text[:180]  # 제외된 앞부분
        excluded_end = text[-100:]   # 제외된 뒷부분
        if len(text) > 190:
            text = text[180:-100]  # 앞 180자와 뒤 10자를 제외
        else:
            text = ""  # 길이가 충분하지 않으면 빈 문자열로 처리
        
        # 로그로 제외된 텍스트 출력
        print(f"제외된 앞부분: {excluded_start}")
        print(f"제외된 뒷부분: {excluded_end}")
        
        text_list.append(text)
    return text_list  # 각 페이지의 텍스트를 리스트로 반환

# 엑셀 데이터에서 특정 행의 시작 페이지와 끝 페이지를 계산하는 함수
def get_page_range(df, index):
    """
    엑셀 데이터에서 특정 행의 시작 페이지와 끝 페이지를 계산합니다.
    """
    start_page = df.loc[index, '페이지']  # 해당 행의 시작 페이지
    if index + 1 < len(df):
        end_page = df.loc[index + 1, '페이지']  # 다음 행의 시작 페이지가 끝 페이지
    else:
        end_page = start_page  # 마지막 행인 경우 시작 페이지와 끝 페이지가 동일
    return start_page, end_page


# 주어진 페이지 범위의 텍스트를 PDF에서 추출하는 함수
def extract_text_from_pdf(pdf_content, start_page, end_page):
    """
    PDF 텍스트에서 주어진 페이지 범위의 내용을 추출합니다.
    """
    start_index = max(0, start_page - 1)  # PDF는 0-based 인덱스를 사용하므로 페이지 번호에 맞춰 인덱스를 조정
    end_index = min(len(pdf_content), end_page)
    return " ".join(pdf_content[start_index:end_index])  # 추출된 텍스트를 하나로 합쳐 반환


# PDF 파일과 엑셀 파일을 처리하는 함수
def process_files(pdf_file, excel_file, page_adjustment):
    # PDF 내용 읽기
    pdf_content = read_pdf_with_pymupdf(pdf_file)
    # 엑셀 파일 읽기
    df = pd.read_excel(excel_file)

    # Study Title 가져오기 (엑셀의 첫 번째 행의 'Study Title' 열 사용)
    study_title = df.loc[0, 'Study Title']

    # JSONL 데이터를 저장할 리스트 초기화
    jsonl_data = []

    # 각 행에 대해 PDF에서 텍스트 추출하여 JSONL 형식으로 저장
    for index, row in df.iterrows():
        start_page, end_page = get_page_range(df, index)
        # 페이지 보정 적용
        start_page += page_adjustment
        end_page += page_adjustment
        title = row['제목']  # 각 행의 제목 가져오기
        
        try:
            # PDF에서 페이지 범위의 텍스트 추출
            pdf_text = extract_text_from_pdf(pdf_content, start_page, end_page)
            
            # 각 메시지를 JSONL 형식으로 구성
            message = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a clinical scientist with expertise in writing clinical trial protocols."
                    },
                    {
                        "role": "user",
                        "content": f"Write a clinical trial protocol section for '{title}' for the study titled: '{study_title}'"
                    },
                    {
                        "role": "assistant",
                        "content": pdf_text.strip() if pdf_text else "Error during processing"
                    }
                ]
            }
            jsonl_data.append(message)  # 생성된 메시지 추가

        except Exception as e:
            message = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a clinical scientist with expertise in writing clinical trial protocols."
                    },
                    {
                        "role": "user",
                        "content": f"Write a clinical trial protocol section for the study titled: '{study_title}'"
                    },
                    {
                        "role": "assistant",
                        "content": "Error during processing"
                    }
                ]
            }
            jsonl_data.append(message)  # 에러 메시지 추가

    return jsonl_data


# Streamlit UI 구성
st.title("PDF & Excel Processor for Clinical Trial Data")

# 파일 업로드
uploaded_pdf = st.file_uploader("PDF 파일 업로드", type="pdf")
uploaded_excel = st.file_uploader("엑셀 파일 업로드", type="xlsx")

# 페이지 보정 슬라이더
page_adjustment = st.slider("페이지 번호 조정", min_value=-3, max_value=3, value=0, step=1)

# 처리 버튼
if st.button("파일 처리"):
    if uploaded_pdf and uploaded_excel:
        with st.spinner("파일 처리 중..."):
            try:
                # PDF 파일을 바이트 스트림으로 읽기
                pdf_file_bytes = uploaded_pdf.read()

                # 파일 처리
                jsonl_data = process_files(pdf_file_bytes, uploaded_excel, page_adjustment)

                # JSONL 파일 저장
                output_jsonl_path = "protocol_data.jsonl"
                with open(output_jsonl_path, "w", encoding="utf-8") as jsonl_file:
                    for entry in jsonl_data:
                        jsonl_file.write(json.dumps(entry, ensure_ascii=False) + "\n")

                # 결과 다운로드 제공
                with open(output_jsonl_path, "rb") as jsonl_file:
                    st.download_button("처리된 JSONL 다운로드", data=jsonl_file, file_name="protocol_data.jsonl")

                st.success("처리가 완료되었습니다!")
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
    else:
        st.warning("두 파일을 모두 업로드해 주세요.")


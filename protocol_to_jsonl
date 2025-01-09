import fitz  # PyMuPDF
import base64
import openai
import streamlit as st
import pandas as pd
from io import BytesIO
from openai import OpenAI
import json
import os


# Set OpenAI API Key (replace with your actual key or manage via environment variable)
openai.api_key = "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"  # (실 사용 시 제거)
client = OpenAI(api_key=openai.api_key)

def pdf_page_to_jpg(pdf_file, page_number):
    """
    Converts a specific page of a PDF to a JPG image.

    Args:
        pdf_file (BytesIO): Uploaded PDF file in memory.
        page_number (int): Page number to convert (1-indexed).

    Returns:
        BytesIO: Image in memory as a BytesIO object.
    """
    pdf_file.seek(0)  # Ensure we're at the start of the file
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    page_index = page_number - 1

    if page_index < 0 or page_index >= len(pdf_document):
        raise ValueError("Invalid page number.")

    page = pdf_document[page_index]
    pix = page.get_pixmap()

    image_data = BytesIO()
    image_data.write(pix.tobytes("jpeg"))
    pdf_document.close()
    image_data.seek(0)
    return image_data


def encode_image(image_data):
    """Encodes image data to base64."""
    return base64.b64encode(image_data.read()).decode("utf-8")

def extract_headings_from_pdf(base64_image):
    """Extract headings using OpenAI API."""
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": [
                {   
                    "type": "text",
                    "text": "Extract all words from this list, sort their number, title, and page number, into a CSV format with three columns: Number, Title, and Page Number. ensure every heading from the beginning to the end is extracted without omission,\n If there's a comma in Title erase it to make sure csv do not be interrupted \n Do not return any words except the 3 columned CSV format"
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        }
    ],
    )
    return response.choices[0].message.content


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
        #print(f"제외된 앞부분: {excluded_start}")
        #print(f"제외된 뒷부분: {excluded_end}")
        
        text_list.append(text)
    return text_list  # 각 페이지의 텍스트를 리스트로 반환

# 엑셀 데이터에서 특정 행의 시작 페이지와 끝 페이지를 계산하는 함수
def get_page_range(df, index):
    """
    Calculate start and end page range for a specific row in the DataFrame.
    """
    start_page = df.iloc[index]['Page Number']  # Current row's start page

    # Check if the next row exists
    if index + 1 < len(df):
        end_page = df.iloc[index + 1]['Page Number']  # Next row's start page
    else:
        end_page = start_page  # Last row's end page is the same as its start page

    return start_page, end_page



# 주어진 페이지 범위의 텍스트를 PDF에서 추출하는 함수
def extract_text_from_pdf(pdf_content, start_page, end_page):
    """
    PDF 텍스트에서 주어진 페이지 범위의 내용을 추출합니다.
    """
    start_index = int(max(0, start_page - 1))  # PDF는 0-based 인덱스를 사용하므로 페이지 번호에 맞춰 인덱스를 조정
    end_index = int(min(len(pdf_content), end_page))
    #print(start_index, end_index)
    #print(len(pdf_content))
    return " ".join(pdf_content[start_index:end_index])  # 추출된 텍스트를 하나로 합쳐 반환


# PDF 파일과 엑셀 파일을 처리하는 함수
def process_files(pdf_file, df, page_adjustment, study_title):
    # PDF 내용 읽기
    pdf_content = read_pdf_with_pymupdf(pdf_file)
    #print(pdf_content)
    # 엑셀 파일 읽기
    #df = pd.read_excel(excel_file)

    # JSONL 데이터를 저장할 리스트 초기화
    jsonl_data = []
    #print(len(df))
    #print(df)
    # 각 행에 대해 PDF에서 텍스트 추출하여 JSONL 형식으로 저장
    for index, row in df.iterrows():
        #print(index)
        start_page, end_page = get_page_range(df, index)
        # 페이지 보정 적용
        start_page += page_adjustment
        end_page += page_adjustment
        title = row['Title']  # 각 행의 제목 가져오기
        
        try:
            # PDF에서 페이지 범위의 텍스트 추출
            pdf_text = extract_text_from_pdf(pdf_content, start_page, end_page)
            #print(pdf_text)
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



def main():
    st.title("Protocol to JSONL Training Converter")

    # File upload
    pdf_file = st.file_uploader("Upload PDF File", type=["pdf"])
    existing_jsonl = st.file_uploader("Upload Existing JSONL File (optional)", type=["jsonl"])

    start_page = st.number_input("Start Page", min_value=1, step=1)
    end_page = st.number_input("End Page", min_value=1, step=1)
    
    page_adjustment = st.slider("Page Adjustment", min_value=-3, max_value=3, value=0, step=1)
    study_title = st.text_input("Study Title", "A Phase III Randomized Trial")

    if pdf_file:
        pdf_file_bytes = pdf_file.read()
        pdf_file_copy = BytesIO(pdf_file_bytes)  # Independent copy

        if st.button("Process File"):
            extracted_data = []

            for page_number in range(start_page, end_page + 1):
                try:
                    # Convert page to image
                    image_data = pdf_page_to_jpg(pdf_file_copy, page_number)

                    # Encode image as base64
                    base64_image = encode_image(image_data)

                    # Extract headings
                    extracted_text = extract_headings_from_pdf(base64_image)
                    rows = [line.split(",") for line in extracted_text.strip().split("\n")]
                    df = pd.DataFrame(rows, columns=["Number", "Title", "Page Number"])
                    extracted_data.append(df)
                except Exception as e:
                    st.error(f"Error processing page {page_number}: {e}")

            if extracted_data:
                # "Page Number" 열을 숫자로 변환, 변환 불가한 값은 NaN으로 처리
                final_df = pd.concat(extracted_data, ignore_index=True)
                final_df["Page Number"] = pd.to_numeric(final_df["Page Number"], errors="coerce")
                chart_1 = final_df.dropna(subset=["Page Number"])
                chart_1 = chart_1.reset_index(drop=True)
                
                st.write("Extracted Data:")
                st.dataframe(chart_1)

                jsonl_data = process_files(pdf_file_bytes, chart_1, page_adjustment, study_title)

                if existing_jsonl:
                    existing_data = []
                    try:
                        existing_jsonl_content = existing_jsonl.read().decode("utf-8").strip().split("\n")
                        for line in existing_jsonl_content:
                            existing_data.append(json.loads(line))
                        
                        jsonl_data = existing_data + jsonl_data  # Merge existing and new data
                        st.success("Merged with existing JSONL file.")
                    except Exception as e:
                        st.error(f"Error reading existing JSONL file: {e}")

                # Save JSONL
                output_jsonl_path = "protocol_data.jsonl"
                with open(output_jsonl_path, "w", encoding="utf-8") as jsonl_file:
                    for entry in jsonl_data:
                        jsonl_file.write(json.dumps(entry, ensure_ascii=False) + "\n")

                # Provide download
                with open(output_jsonl_path, "rb") as jsonl_file:
                    st.download_button("Download Final JSONL", data=jsonl_file, file_name="final_protocol_data.jsonl")

if __name__ == "__main__":
    main()

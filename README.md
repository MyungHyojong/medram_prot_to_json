# Protocol to JSONL Training Converter

## 소개

이 애플리케이션은 Streamlit과 OpenAI API를 사용하여 PDF 파일에서 임상시험 프로토콜 데이터를 추출하고, 이를 JSONL 형식으로 변환하는 도구입니다. 사용자는 PDF에서 제목과 페이지 번호를 추출하고, 이를 기반으로 JSONL 데이터를 생성하여 OpenAI 모델 학습에 사용할 수 있습니다.

https://medrama-proto-json.streamlit.app/
---

## 주요 기능

- **PDF 페이지 이미지 변환**: PDF의 특정 페이지를 JPG 이미지로 변환.
- **이미지에서 제목 추출**: OpenAI API를 사용하여 이미지에서 제목과 페이지 번호를 추출.
- **PDF 텍스트 읽기**: PyMuPDF를 활용하여 PDF에서 텍스트를 추출.
- **JSONL 데이터 생성**: 추출된 텍스트를 JSONL 형식으로 변환하여 저장.
- **기존 JSONL 병합**: 기존 JSONL 파일과 새로운 데이터를 병합하여 관리.
- **직관적인 UI**: Streamlit 기반의 간단한 사용자 인터페이스 제공.

---

## 설치 방법

### 필수 요구 사항
- Python 3.9 이상
- 아래 패키지를 설치:
  ```bash
  pip install streamlit pymupdf openai pandas
  ```

### OpenAI API 키 설정
- Streamlit `secrets.toml` 파일을 설정:
  ```toml
  [openai]
  api_key = "your_openai_api_key"
  ```

---

## 사용법
![Clinical Trial Protocol](https://i.ibb.co/MsBzT0c/i3.png)

1. **파일 업로드**:
   - PDF 파일을 업로드.
   - 기존 JSONL 파일(선택 사항)을 업로드하여 새로운 데이터와 병합 가능.

2. **매개변수 설정**:
   - 시작 페이지 및 종료 페이지 지정.
   - 페이지 조정 값(Page Adjustment) 선택.
   - 연구 제목(Study Title) 입력.

3. **파일 처리**:
   - "Process File" 버튼을 클릭하여 PDF 파일 처리.
   - 페이지별로 제목과 페이지 번호 추출.
   - 추출된 데이터를 테이블로 표시.

4. **JSONL 생성**:
   - 추출된 데이터를 바탕으로 JSONL 파일 생성.
   - 기존 JSONL 파일과 병합(선택 사항).

5. **결과 다운로드**:
   - 최종 JSONL 파일을 다운로드.

---

## 주요 코드 구성

- **`pdf_page_to_jpg`**: PDF의 특정 페이지를 JPG 이미지로 변환.
- **`encode_image`**: 이미지 데이터를 Base64로 인코딩.
- **`extract_headings_from_pdf`**: OpenAI API를 사용하여 이미지에서 제목과 페이지 번호 추출.
- **`read_pdf_with_pymupdf`**: PDF의 모든 페이지에서 텍스트 추출.
- **`process_files`**: PDF 및 추출된 데이터로 JSONL 형식 생성.

---

## 주의사항

1. **OpenAI API 사용량**:
   - OpenAI API 호출은 사용량을 소비하므로 적절한 요금제를 선택하세요.

2. **PDF 품질**:
   - PDF 이미지 품질이 낮을 경우 제목 추출 정확도가 떨어질 수 있습니다.

3. **데이터 보안**:
   - 업로드한 PDF와 생성된 JSONL 데이터가 민감한 정보를 포함할 수 있으므로 데이터 보안을 유지하세요.

---

## 기여 및 피드백

이 프로젝트에 기여하거나 피드백을 제공하려면 [GitHub 저장소 링크](#)를 통해 문의하세요.

---

## 라이선스

이 프로젝트는 MIT 라이선스에 따라 배포됩니다.

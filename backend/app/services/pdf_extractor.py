"""PDF 题目提取服务 —— 从 PDF 文本中识别选择/填空/判断题"""

import re
from typing import List


def extract_text_from_pdf(file_bytes: bytes) -> str:
    import pdfplumber
    import io
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
    return "\n".join(text_parts)


def _normalize_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def _extract_choice_questions(text: str) -> List[dict]:
    questions = []
    pattern = re.compile(
        r'(\d+)\s*[\.、\s]\s*(.*?)'
        r'\nA\s*[\.、]\s*(.*?)'
        r'\nB\s*[\.、]\s*(.*?)'
        r'\nC\s*[\.、]\s*(.*?)'
        r'(?:\nD\s*[\.、]\s*(.*?))?'
        r'(?:\nE\s*[\.、]\s*(.*?))?'
        r'(?:\nF\s*[\.、]\s*(.*?))?'
        r'\n答案\s*[：:]\s*([A-Fa-f]+)',
        re.DOTALL,
    )

    for match in pattern.finditer(text):
        groups = match.groups()
        stem = _normalize_text(groups[1])
        options = [_normalize_text(g) for g in groups[2:8] if g is not None]
        options = [o for o in options if o]
        answer_str = groups[8].strip().upper()

        if not stem or len(options) < 2:
            continue

        if len(answer_str) == 1:
            answer = ord(answer_str) - ord('A')
            q_type = "single"
        else:
            answer = [ord(ch) - ord('A') for ch in answer_str]
            q_type = "multi"

        questions.append({
            "question_text": stem,
            "options": options,
            "answer": answer,
            "analysis": "",
            "type": q_type,
        })
    return questions


def _extract_true_false_questions(text: str) -> List[dict]:
    questions = []
    pattern = re.compile(
        r'(\d+)\s*[\.、\s]\s*(.*?)\s*'
        r'答案\s*[：:]\s*([对错√✓✔×✗✘TFtf])',
        re.DOTALL,
    )

    seen = set()
    for match in pattern.finditer(text):
        stem = _normalize_text(match.group(2))
        ans = match.group(3).strip()
        is_correct = ans in '对√✓✔Tt'

        if not stem or len(stem) < 3 or stem in seen:
            continue
        seen.add(stem)

        questions.append({
            "question_text": stem,
            "options": ["正确", "错误"],
            "answer": 0 if is_correct else 1,
            "analysis": "",
            "type": "tf",
        })


def _extract_fill_blank_questions(text: str) -> List[dict]:
    questions = []
    pattern = re.compile(
        r'(\d+)\s*[\.、\s]\s*(.*?)\s*答案\s*[：:]\s*(.+?)(?=\n\s*\d+\s*[\.、\s]|\Z)',
        re.DOTALL,
    )

    for match in pattern.finditer(text):
        stem = _normalize_text(match.group(2))
        answer = _normalize_text(match.group(3))

        if not stem or not answer or len(stem) < 3:
            continue
        has_blank = any(marker in stem for marker in ['____', '___', '___', '（  ）', '()'])
        if not has_blank and len(stem) < 10:
            continue

        questions.append({
            "question_text": stem,
            "options": [],
            "answer": answer,
            "analysis": "",
            "type": "fill",
        })


def extract_questions_from_pdf(file_bytes: bytes) -> dict:
    text = extract_text_from_pdf(file_bytes)
    choices = _extract_choice_questions(text)
    tf = _extract_true_false_questions(text)
    fill = _extract_fill_blank_questions(text)

    return {
        "choice_questions": choices,
        "true_false_questions": tf,
        "fill_blank_questions": fill,
        "total": len(choices) + len(tf) + len(fill),
        "raw_text_preview": text[:500],
    }

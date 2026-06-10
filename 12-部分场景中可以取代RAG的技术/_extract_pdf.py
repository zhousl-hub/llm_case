# -*- coding: utf-8 -*-
import fitz
import os

pdf_path = r"D:\data\data\code\llm_case\12-部分场景中可以取代RAG的技术\可能替代RAG的技术(5).pdf"
out_html = r"D:\data\data\code\llm_case\12-部分场景中可以取代RAG的技术\可能替代RAG的技术(5).html"
out_txt = r"D:\data\data\code\llm_case\12-部分场景中可以取代RAG的技术\可能替代RAG的技术(5).txt"

doc = fitz.open(pdf_path)
print("pages:", len(doc))

html_parts = [
    '<!DOCTYPE html><html><head><meta charset="utf-8">'
    "<title>可能替代RAG的技术</title></head><body>"
]
text_parts = []
for i, page in enumerate(doc):
    html_parts.append(f'<div class="page" data-page="{i + 1}">')
    html_parts.append(page.get_text("html"))
    html_parts.append("</div>")
    text_parts.append(f"=== PAGE {i + 1} ===\n")
    text_parts.append(page.get_text())
    text_parts.append("\n")

html_parts.append("</body></html>")
with open(out_html, "w", encoding="utf-8") as f:
    f.write("".join(html_parts))

with open(out_txt, "w", encoding="utf-8") as f:
    f.write("\n".join(text_parts))

print("html:", out_html, os.path.getsize(out_html))
print("txt:", out_txt, os.path.getsize(out_txt))
print("--- preview ---")
print("".join(text_parts)[:5000])

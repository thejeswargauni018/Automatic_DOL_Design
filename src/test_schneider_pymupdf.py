import pymupdf


PDF_PATH = "data/schneider_source_document.pdf"

print("\n================================")
print("SCHNEIDER PYMUPDF TEST")
print("================================")

pdf = pymupdf.open(PDF_PATH)

for page_number in [15, 16]:

    print("\n================================")
    print(f"PAGE {page_number}")
    print("================================")

    page = pdf[page_number - 1]

    text = page.get_text("text")

    print(text)


pdf.close()
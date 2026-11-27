import pymupdf


PDF_PATH = "data/schneider_source_document.pdf"

print("\n================================")
print("SCHNEIDER TABLE COORDINATES")
print("================================")

pdf = pymupdf.open(PDF_PATH)

for page_number in [15, 16]:

    print("\n================================")
    print(f"PAGE {page_number}")
    print("================================")

    page = pdf[page_number - 1]

    words = page.get_text("words")

    # Print words located around the table header
    # and first few data rows.
    for word in words:

        x0, y0, x1, y1, text = word[:5]

        if 250 < y0 < 430:

            print(
                f"x={x0:7.1f}  "
                f"y={y0:7.1f}  "
                f"text={text}"
            )

pdf.close()
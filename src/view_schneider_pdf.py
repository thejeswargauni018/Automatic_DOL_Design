import fitz
import os


PDF_PATH = "data/schneider_source_document.pdf"
OUTPUT_DIR = "output/schneider_pages"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("\n================================")
print("SCHNEIDER PDF PAGE PREVIEW")
print("================================")

pdf = fitz.open(PDF_PATH)

print("Total pages:", len(pdf))

# Render every page at a readable resolution
for page_number, page in enumerate(pdf):

    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))

    output_path = os.path.join(
        OUTPUT_DIR,
        f"page_{page_number + 1}.png"
    )

    pix.save(output_path)

print("\nPages converted successfully.")

print(
    "Images saved in:",
    OUTPUT_DIR
)
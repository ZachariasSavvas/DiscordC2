import os
import argparse

def hide_exe_in_pdf(exe_path, cover_pdf_path, output_pdf_path, marker="HIDDEN_EXE:"):
    """Hide an .exe file in a PDF by appending it after the %%EOF marker."""
    if not os.path.exists(exe_path):
        print(f"Error: .exe file not found at {exe_path}")
        return
    if not os.path.exists(cover_pdf_path):
        print(f"Error: Cover PDF not found at {cover_pdf_path}")
        return

    # Read the .exe and cover PDF
    with open(exe_path, "rb") as f:
        exe_data = f.read()
    with open(cover_pdf_path, "rb") as f:
        pdf_data = f.read()

    # Find the %%EOF marker
    eof_index = pdf_data.rfind(b"%%EOF")
    if eof_index == -1:
        print("Error: %%EOF marker not found in cover PDF")
        return

    # Create the output PDF
    with open(output_pdf_path, "wb") as f:
        # Write original PDF content
        f.write(pdf_data)
        # Append marker and .exe data
        f.write(b"\n" + marker.encode() + b"\n")
        f.write(exe_data)
    print(f"Success: .exe hidden in {output_pdf_path}")

def generate_extractor(extractor_path, marker="HIDDEN_EXE:"):
    """Generate a Python script to extract the .exe from the PDF."""
    extractor_code = f"""import os

def extract_exe(pdf_path, output_exe_path, marker="{marker}"):
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {{pdf_path}}")
        return
    with open(pdf_path, "rb") as f:
        data = f.read()
    marker_bytes = marker.encode()
    marker_index = data.find(marker_bytes)
    if marker_index == -1:
        print(f"Error: Marker '{{marker}}' not found in PDF")
        return
    exe_data = data[marker_index + len(marker_bytes) + 1:]
    with open(output_exe_path, "wb") as f:
        f.write(exe_data)
    print(f"Success: .exe extracted to {{output_exe_path}}")
    # Optionally run the .exe
    os.system(output_exe_path)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Extract .exe from PDF")
    parser.add_argument("pdf_path", help="Path to the PDF with hidden .exe")
    parser.add_argument("output_exe_path", help="Path to save the extracted .exe")
    args = parser.parse_args()
    extract_exe(args.pdf_path, args.output_exe_path)
"""
    with open(extractor_path, "w") as f:
        f.write(extractor_code)
    print(f"Extractor script generated: {extractor_path}")

def main():
    parser = argparse.ArgumentParser(description="Hide .exe in PDF using steganography")
    parser.add_argument("exe_path", help="Path to the .exe file to hide")
    parser.add_argument("cover_pdf_path", help="Path to the cover PDF file")
    parser.add_argument("output_pdf_path", help="Path to save the output PDF")
    parser.add_argument("--extractor", help="Path to save the extractor script", default="extract_exe.py")
    args = parser.parse_args()

    hide_exe_in_pdf(args.exe_path, args.cover_pdf_path, args.output_pdf_path)
    generate_extractor(args.extractor)

if __name__ == "__main__":
    main()
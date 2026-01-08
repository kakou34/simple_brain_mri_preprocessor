import subprocess

def run_hdbet_batch(input_folder, output_folder, device="cuda"):
    """
    Runs HD-BET on an entire folder.
    -device: GPU ID (usually 0 on HPC)
    """
    # HD-BET will automatically look for .nii.gz files in input_folder
    cmd = [
        "hd-bet",
        "-i", input_folder,
        "-o", output_folder,
        "-device", device,
        "--disable_tta",
        "--save_bet_mask",
        "--no_bet_image"
    ]
    
    print(f"Starting HD-BET batch processing on {input_folder}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"HD-BET Batch failed: {result.stderr}")
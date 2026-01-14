import argparse
import os
import shutil
import ants
import nibabel as nib
from src.extraction import run_hdbet_batch
from src.registration import run_fsl_registration, run_ants_registration
from src.bias_correction import run_n4_bias_correction


def main():
    parser = argparse.ArgumentParser(description="Simple Brain MRI Preprocessor")
    parser.add_argument(
        "--input", required=True, help="Folder containing raw T1w .nii.gz files"
    )
    parser.add_argument("--output", required=True, help="Folder for final results")
    parser.add_argument("--atlas", required=True, help="Fixed image (e.g., MNI152)")
    parser.add_argument("--atlas_mask", required=True, help="Mask of the fixed image")
    parser.add_argument(
        "--reg_tool", default="FSL", help="Registration tool to use: FSL or ANTs"
    )
    parser.add_argument(
        "--use_mask", action="store_true", help="Use brain masks during registration"
    )
    parser.add_argument(
        "--cleanup", action="store_true", help="Remove temporary files after processing"
    )
    parser.add_argument("--device", default="cuda", help="cuda or cpu")
    args = parser.parse_args()

    # 1. Create temporary directories
    mask_temp = os.path.join(args.output, "temp_hdbet_masks")
    bias_temp = os.path.join(args.output, "temp_bias_corrected")
    os.makedirs(mask_temp, exist_ok=True)
    os.makedirs(bias_temp, exist_ok=True)

    # PHASE 1: Batch Brain Extraction
    print(">>> Starting Phase 1: Batch Brain Extraction (HD-BET)")
    run_hdbet_batch(args.input, mask_temp)

    # PHASE 2: Bias Correction & Registration
    raw_files = [f for f in os.listdir(args.input) if f.endswith(".nii.gz")]

    for f in raw_files:
        subject_id = f.replace(".nii.gz", "")
        moving_path = os.path.join(args.input, f)
        moving_mask_path = os.path.join(mask_temp, f"{subject_id}_bet.nii.gz")

        # --- Bias Field Correction ---
        corrected_path = os.path.join(bias_temp, f"{subject_id}_n4.nii.gz")
        run_n4_bias_correction(moving_path, moving_mask_path, corrected_path)

        

        # Registration Paths
        reg_path = os.path.join(args.output, f"tmp_reg_{subject_id}.nii.gz")
        reg_mask_path = os.path.join(args.output, f"tmp_reg_mask_{subject_id}.nii.gz")

        try:
            if args.reg_tool.lower() == "fsl":
                # Use corrected_path instead of moving_path
                reg_path, reg_mask_path = run_fsl_registration(
                    corrected_path,
                    moving_mask_path,
                    args.atlas,
                    args.atlas_mask,
                    reg_path,
                    reg_mask_path,
                    args.use_mask,
                )

                # Skull-strip
                img = nib.load(reg_path)
                mask = nib.load(reg_mask_path)
                stripped_data = img.get_fdata() * (mask.get_fdata() > 0.5)

                final_img = nib.Nifti1Image(stripped_data, img.affine, img.header)
                out_name = os.path.join(args.output, f"{subject_id}_preproc.nii.gz")
                nib.save(final_img, out_name)

                # Local Cleanup of intermediate reg files
                os.remove(reg_path)
                os.remove(reg_mask_path)

            elif args.reg_tool.lower() == "ants":
                # Use corrected_path instead of moving_path
                reg_img, reg_mask = run_ants_registration(
                    corrected_path,
                    moving_mask_path,
                    args.atlas,
                    args.atlas_mask,
                    args.use_mask,
                )

                final_stripped = reg_img * reg_mask
                out_name = os.path.join(args.output, f"{subject_id}_preproc.nii.gz")
                ants.image_write(final_stripped, out_name)
            else:
                raise ValueError(
                    "Unsupported registration tool. Choose 'FSL' or 'ANTs'."
                )
        except Exception as e:
            print(f"Error processing {subject_id}: {e}")

    # FINAL CLEANUP: Outside the loop
    if args.cleanup:
        print(">>> Cleaning up temporary directories...")
        shutil.rmtree(mask_temp)
        shutil.rmtree(bias_temp)

    print(">>> Pipeline finished successfully.")


if __name__ == "__main__":
    main()

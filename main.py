import argparse
import os
import shutil
import ants
from src.extraction import run_hdbet_batch
from src.registration import run_fsl_registration, run_ants_registration
import nibabel as nib

def main():
    parser = argparse.ArgumentParser(description="Simple Brain MRI Preprocessor")
    parser.add_argument("--input", required=True, help="Folder containing raw T1w .nii.gz files")
    parser.add_argument("--output", required=True, help="Folder for final results")
    parser.add_argument("--atlas", required=True, help="Fixed image (e.g., MNI152)")
    parser.add_argument("--atlas_mask", required=True, help="Mask of the fixed image")
    parser.add_argument("--reg_tool", default="FSL", help="Registration tool to use: FSL or ANTs")
    parser.add_argument("--use_mask", action="store_true", help="Use brain masks during registration")
    parser.add_argument("--cleanup", action="store_true", help="Remove brain mask files after processing")
    parser.add_argument("--device", default="cuda", help="cuda or cpu")
    args = parser.parse_args()

    # Create temporary directory for masks
    mask_temp = os.path.join(args.output, "temp_hdbet_masks")
    os.makedirs(mask_temp, exist_ok=True)

    # PHASE 1: Batch HD-BET on Raw Scans
    print(">>> Starting Phase 1: Batch Brain Extraction")
    run_hdbet_batch(args.input, mask_temp)

    # PHASE 2: Registration
    raw_files = [f for f in os.listdir(args.input) if f.endswith(".nii.gz")]
    
    for f in raw_files:
        moving_path = os.path.join(args.input, f)
        moving_mask_path = os.path.join(mask_temp, f.replace(".nii.gz", "_bet.nii.gz"))
        
        reg_path = os.path.join(args.output, "tmp_reg.nii.gz")
        reg_mask_path = os.path.join(args.output, "tmp_reg_mask.nii.gz")

        if args.reg_tool.lower() == "fsl":
            # 1. Run FSL Pipeline
            reg_path, reg_mask_path = run_fsl_registration(moving_path, moving_mask_path, args.atlas, args.atlas_mask, reg_path, reg_mask_path, args.use_mask)
             # 2. Skull-strip (using nibabel for FSL compatibility)
            img = nib.load(reg_path)
            mask = nib.load(reg_mask_path)
            
            # Simple multiplication
            stripped_data = img.get_fdata() * (mask.get_fdata() > 0.5)
            
            final_img = nib.Nifti1Image(stripped_data, img.affine, img.header)
            out_name = os.path.join(args.output, f.replace(".nii.gz", "_preproc.nii.gz"))
            nib.save(final_img, out_name)

            # Cleanup temp files
            os.remove(reg_path)
            os.remove(reg_mask_path)


        elif args.reg_tool.lower() == "ants":
            # 1. Run ANTs Pipeline
            reg_img, reg_mask = run_ants_registration(moving_path, moving_mask_path, args.atlas, args.atlas_mask, args.use_mask)
            # 2. Skull-strip
            final_stripped = reg_img * reg_mask

            out_name = os.path.join(args.output, f.replace(".nii.gz", "_preproc.nii.gz"))   
            ants.image_write(final_stripped, out_name)

        else:
            raise ValueError(f"Unsupported registration tool: {args.reg_tool}. Choose from FSL or ANTs.")

        # Cleanup
        if args.cleanup:
            shutil.rmtree(mask_temp)
        print(">>> Pipeline finished successfully.")

if __name__ == "__main__":
    main()
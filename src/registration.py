import ants
import os
import subprocess

def run_ants_registration(fixed_path, fixed_mask_path, moving_path, moving_mask_path, use_mask=False):
    """
    Performs mask-guided registration using ANTs.
    """
    # 1. Load images as ANTs objects
    fixed_img = ants.image_read(fixed_path)
    moving_img = ants.image_read(moving_path)
    
    fixed_mask = ants.image_read(fixed_mask_path)
    moving_mask = ants.image_read(moving_mask_path)

    # 2. Perform Registration
    # 'QuickRigid' or 'TRNA' (Translation, Rigid, Native, Affine) are good for MNI
    print(f"Running ANTs registration for {os.path.basename(moving_path)}...")
    
    if use_mask:
        reg_results = ants.registration(
            fixed=fixed_img,
            moving=moving_img,
            type_of_transform="Affine",  # Rigid + Affine
            mask=fixed_mask,           # Guiding the metric on the atlas
            moving_mask=moving_mask,   # Guiding the metric on the subject
            verbose=True
        )
    else:
        reg_results = ants.registration(
            fixed=fixed_img,
            moving=moving_img,
            type_of_transform="Affine",  # Rigid + Affine
            verbose=True
        )

    # 3. Apply the transform to the moving mask
    # We need the mask in atlas space for skull-stripping
    reg_mask = ants.apply_transforms(
        fixed=fixed_img,
        moving=moving_mask,
        transformlist=reg_results['fwdtransforms'],
        interpolator='nearestNeighbor' # Masks must use nearest neighbor
    )

    reg_image = reg_results['warpedmovout']

    return reg_image, reg_mask


def run_fsl_registration(moving_path, moving_mask_path, fixed_path, fixed_mask_path, output_path, output_mask_path, use_mask=False):
    """
    Performs mask-guided registration using FSL FLIRT.
    """
    for p in [moving_path, moving_mask_path, fixed_path, fixed_mask_path]:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Missing file for FSL: {p}")
        
    # 1. Reorient to standard (matches MNI orientation)
    # We do this to both the image and the mask
    tmp_moving = moving_path.replace(".nii.gz", "_reorient.nii.gz")
    tmp_mask = moving_mask_path.replace(".nii.gz", "_reorient.nii.gz")
    
    subprocess.run(["fslreorient2std", moving_path, tmp_moving], check=True)
    subprocess.run(["fslreorient2std", moving_mask_path, tmp_mask], check=True)

    # 2. Registration (FLIRT)
    # -inweight and -refweight focus the cost function on the brain only
    matrix_path = output_path.replace(".nii.gz", ".mat")

    if use_mask:
        flirt_cmd = [
            "flirt",
            "-in", tmp_moving,
            "-ref", fixed_path,
            "-out", output_path,
            "-omat", matrix_path,          # Save the transformation matrix
            "-inweight", tmp_mask,
            "-refweight", fixed_mask_path,
            "-bins", "256",
            "-cost", "corratio",
            "-dof", "12",                  # Affine (12 Degrees of Freedom)
            "-interp", "spline"
        ]
    else:
        flirt_cmd = [
            "flirt",
            "-in", tmp_moving,
            "-ref", fixed_path,
            "-out", output_path,
            "-omat", matrix_path,          # Save the transformation matrix
            "-bins", "256",
            "-cost", "corratio",
            "-dof", "12",                  # Affine (12 Degrees of Freedom)
            "-interp", "spline"
        ]
    
    print(f"Running FSL FLIRT for {os.path.basename(moving_path)}...")
    subprocess.run(flirt_cmd, check=True)

    # 3. Apply the same transformation to the Mask
    # We use -applyxfm and -init to ensure the mask follows the image exactly
    mask_apply_cmd = [
        "flirt",
        "-in", tmp_mask,
        "-ref", fixed_path,
        "-out", output_mask_path,
        "-applyxfm",
        "-init", matrix_path,
        "-interp", "nearestneighbour"  # Critical: Use NN for binary masks
    ]
    subprocess.run(mask_apply_cmd, check=True)

    # Cleanup temporary reoriented files
    os.remove(tmp_moving)
    os.remove(tmp_mask)
    
    return output_path, output_mask_path


import ants
import os

def run_n4_bias_correction(image_path, mask_path, output_path):
    """
    Applies N4 Bias Field Correction using ANTs.
    The mask helps the algorithm estimate the bias field based only on brain voxels.
    """
    print(f"Applying N4 Bias Correction: {os.path.basename(image_path)}")
    
    # Load image and mask
    img = ants.image_read(image_path)
    mask = ants.image_read(mask_path)
    
    # N4BiasFieldCorrection is more robust when a mask is provided
    # shrink_factor=4 is standard for speed/accuracy balance in T1w
    corrected_img = ants.n4_bias_field_correction(img, mask=mask, shrink_factor=4)
    
    # Save to temporary folder
    ants.image_write(corrected_img, output_path)
    
    return output_path
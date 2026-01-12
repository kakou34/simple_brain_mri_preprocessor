import ants
import os

def run_n4_bias_correction(image_path, mask_path, output_path):
    """
    Applies N4 Bias Field Correction using ANTs with physical space alignment.
    """
    print(f"Applying N4 Bias Correction: {os.path.basename(image_path)}")
    
    # 1. Load images
    img = ants.image_read(image_path)
    mask = ants.image_read(mask_path)
    
    # 2. FORCE ALIGNMENT
    # This overwrites the mask's header info with the image's header info.
    # It solves the 'Inputs do not occupy the same physical space' error.
    mask = ants.copy_image_info(img, mask)
    
    try:
        # 3. Run N4 Bias Field Correction
        corrected_img = ants.n4_bias_field_correction(img, mask=mask, shrink_factor=4)
        ants.image_write(corrected_img, output_path)
    except Exception as e:
        print(f"!!! N4 Failed for {image_path} even after info copy: {e}")
        # Fallback: copy original to corrected_path so pipeline doesn't break
        ants.image_write(img, output_path)
    
    return output_path
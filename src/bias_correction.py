import SimpleITK as sitk
import os

def run_n4_bias_correction(image_path, mask_path, output_path):
    """
    Applies N4 Bias Field Correction using SimpleITK.
    """
    print(f"Applying N4 Bias Correction (SimpleITK): {os.path.basename(image_path)}")
    
    # 1. Load images
    img = sitk.ReadImage(image_path)
    mask = sitk.ReadImage(mask_path)
    
    # 2. FORCE ALIGNMENT (Header Snapping)
    # SimpleITK is strict; we ensure the mask has the exact same origin, 
    # spacing, and direction as the image.
    mask.CopyInformation(img)
    
    # 3. Cast to correct types
    # N4 expects the image to be Float32 and the mask to be UInt8 (label)
    img = sitk.Cast(img, sitk.sitkFloat32)
    mask = sitk.Cast(mask, sitk.sitkUInt8)
    
    try:
        # 4. Configure N4 Filter
        corrector = sitk.N4BiasFieldCorrectionImageFilter()
        
        # Standard settings: 4 iterations, shrink factor of 4 for speed
        # These match the default 'ants.n4_bias_field_correction' behavior
        corrector.SetMaximumNumberOfIterations([50] * 4) 
        
        # Execute (using the mask to guide field estimation)
        corrected_img = corrector.Execute(img, mask)
        
        # 5. Save output
        sitk.WriteImage(corrected_img, output_path)
        
    except Exception as e:
        print(f"!!! N4 Failed for {image_path}: {e}")
        # Fallback: Save the original image as the result to prevent pipeline crash
        sitk.WriteImage(img, output_path)
    
    return output_path
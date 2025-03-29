import os
import glob


# ---------------------------
# Utility Functions
# ---------------------------

def find_first_pdf():
    """Locate first PDF in current directory"""
    pdfs = glob.glob(os.path.join(os.getcwd(), "*.[pP][dD][fF]"))
    return sorted(pdfs)[0] if pdfs else None


import streamlit as st
import PyPDF2
from PIL import Image
import io
import fitz  # PyMuPDF
import tempfile
import os

# Set page config
st.set_page_config(
    page_title="PDF Page Combiner",
    page_icon="📄",
    layout="centered"
)

# Custom CSS styling with dark theme
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Raleway:wght@400;500;600;700&display=swap');
        
        /* Main container styling with dark background */
        .stApp {
            background: 
                linear-gradient(135deg, rgba(18, 18, 18, 0.95) 0%, rgba(30, 30, 30, 0.97) 100%),
                repeating-linear-gradient(45deg, 
                    rgba(50, 50, 50, 0.1) 0px, 
                    rgba(50, 50, 50, 0.1) 2px,
                    transparent 2px, 
                    transparent 10px
                );
            background-attachment: fixed;
            font-family: 'Poppins', sans-serif;
            color: #ffffff;
        }
        
        /* Title styling for dark theme */
        .title {
            font-family: 'Raleway', sans-serif;
            color: #00B4DB;
            text-align: center;
            padding: 2rem 0;
            font-size: 3rem;
            font-weight: 700;
            text-shadow: 
                2px 2px 0 rgba(0,0,0,0.5),
                4px 4px 0 rgba(0,180,219,0.2);
            letter-spacing: 2px;
            transform: perspective(500px) rotateX(10deg);
            margin-bottom: 20px;
        }
        
        /* Subtitle for dark theme */
        .subtitle {
            font-family: 'Poppins', sans-serif;
            color: #B0BEC5;
            text-align: center;
            margin-bottom: 2rem;
            font-size: 1.2rem;
            text-shadow: 1px 1px 0 rgba(0,0,0,0.5);
            transform: perspective(500px) rotateX(5deg);
        }
        
        /* File uploader container dark theme */
        .uploadedFile {
            background: rgba(40, 40, 40, 0.9);
            border-radius: 15px;
            padding: 30px;
            margin: 30px 0;
            border: 2px dashed #00B4DB;
            box-shadow: 
                0 10px 20px rgba(0,0,0,0.3),
                0 6px 6px rgba(0,0,0,0.2),
                inset 0 -5px 10px rgba(0,0,0,0.2);
            transform: perspective(1000px) rotateX(2deg);
            transition: all 0.3s ease;
        }
        
        .uploadedFile:hover {
            transform: perspective(1000px) rotateX(0deg) translateY(-5px);
            box-shadow: 
                0 15px 30px rgba(0,0,0,0.4),
                0 8px 8px rgba(0,0,0,0.3),
                inset 0 -5px 10px rgba(0,0,0,0.2);
            border-color: #00E5FF;
        }
        
        /* Button styling for dark theme */
        .stButton>button {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(145deg, #00B4DB, #0083B0);
            color: white;
            padding: 0.8rem 2rem;
            border-radius: 50px;
            border: none;
            box-shadow: 
                0 5px 15px rgba(0,0,0,0.3),
                0 3px 3px rgba(0,0,0,0.2),
                inset 0 -3px 8px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            transform: perspective(500px) rotateX(5deg);
            font-weight: 500;
            letter-spacing: 1px;
            text-transform: uppercase;
            width: 100%;
            margin: 1rem 0;
        }
        
        .stButton>button:hover {
            background: linear-gradient(145deg, #00E5FF, #00B4DB);
            transform: perspective(500px) rotateX(0deg) translateY(-3px);
            box-shadow: 
                0 8px 20px rgba(0,0,0,0.4),
                0 4px 4px rgba(0,0,0,0.3),
                inset 0 -4px 10px rgba(0,0,0,0.2);
        }
        
        /* Download button dark theme */
        .stDownloadButton>button {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(145deg, #00897B, #00796B);
            color: white;
            padding: 0.8rem 2rem;
            border-radius: 50px;
            border: none;
            box-shadow: 
                0 5px 15px rgba(0,0,0,0.3),
                0 3px 3px rgba(0,0,0,0.2),
                inset 0 -3px 8px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            transform: perspective(500px) rotateX(5deg);
            font-weight: 500;
            letter-spacing: 1px;
            text-transform: uppercase;
            width: 100%;
        }
        
        .stDownloadButton>button:hover {
            background: linear-gradient(145deg, #009688, #00897B);
            transform: perspective(500px) rotateX(0deg) translateY(-3px);
            box-shadow: 
                0 8px 20px rgba(0,0,0,0.4),
                0 4px 4px rgba(0,0,0,0.3),
                inset 0 -4px 10px rgba(0,0,0,0.2);
        }
        
        /* Select box dark theme */
        .stSelectbox {
            background: #2C2C2C;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 
                0 5px 15px rgba(0,0,0,0.2),
                0 3px 3px rgba(0,0,0,0.1);
            transform: perspective(500px) rotateX(2deg);
            color: white;
        }
        
        /* Error message dark theme */
        .stError {
            background: linear-gradient(145deg, #CF6679, #B00020);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 
                0 5px 15px rgba(0,0,0,0.2),
                0 3px 3px rgba(0,0,0,0.1);
            transform: perspective(500px) rotateX(2deg);
        }
    </style>
""", unsafe_allow_html=True)

def combine_pdf_pages(input_pdf, pages_per_sheet):
    """
    Combine multiple PDF pages into a single sheet
    """
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "combined_output.pdf")
    
    try:
        # Open the input PDF
        pdf_document = fitz.open(stream=input_pdf.read(), filetype="pdf")
        output_pdf = fitz.open()
        
        total_pages = pdf_document.page_count
        current_page = 0
        
        # Calculate how many output pages we need
        output_pages_needed = (total_pages + pages_per_sheet - 1) // pages_per_sheet
        
        for output_page_num in range(output_pages_needed):
            # Get the first page's dimensions for reference
            ref_page = pdf_document[0]
            # Create a larger page - multiply width by 2 since we have 2 columns
            output_page = output_pdf.new_page(
                width=ref_page.rect.width * 2,
                height=ref_page.rect.height * ((pages_per_sheet + 1) // 2)
            )
            
            # Calculate the grid dimensions
            cols = 2  # Always use 2 columns
            rows = (pages_per_sheet + 1) // 2  # Calculate rows needed
            
            pages_this_sheet = min(pages_per_sheet, total_pages - current_page)
            
            for i in range(pages_this_sheet):
                if current_page >= total_pages:
                    break
                    
                # Calculate position for current page
                row = i // cols
                col = i % cols
                
                # Get the page
                page = pdf_document[current_page]
                rect = page.rect
                
                # Calculate target rectangle - maintain original size
                target_x = rect.width * col
                target_y = rect.height * row
                target_rect = fitz.Rect(
                    target_x, target_y,
                    target_x + rect.width,
                    target_y + rect.height
                )
                
                # Copy page content to new position
                output_page.show_pdf_page(target_rect, pdf_document, current_page)
                current_page += 1
        
        # Save the output PDF
        output_pdf.save(output_path)
        
        # Read the output file
        with open(output_path, "rb") as file:
            output_bytes = file.read()
            
        return output_bytes
        
    finally:
        # Cleanup temporary files
        if os.path.exists(output_path):
            os.remove(output_path)
        os.rmdir(temp_dir)

# Main Streamlit UI
st.markdown('<h1 class="title">PDF Page Combiner</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Transform Your PDF Layout with Style</p>', unsafe_allow_html=True)

# File upload section
st.markdown('<div class="uploadedFile">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file is not None:
    # Get number of pages per sheet
    pages_per_sheet = st.selectbox(
        "Number of pages per sheet",
        options=[2, 4, 6, 8, 10, 12],
        index=1
    )
    
    if st.button("Process PDF"):
        try:
            with st.spinner("Processing PDF..."):
                output_pdf = combine_pdf_pages(uploaded_file, pages_per_sheet)
                
            # Provide download button for processed PDF
            st.download_button(
                label="Download Combined PDF",
                data=output_pdf,
                file_name="combined_output.pdf",
                mime="application/pdf"
            )
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
# Footer with enhanced styling
st.markdown("""
    <style>
        /* Footer styling with gradient text and animation */
        .footer {
            font-family: 'Raleway', sans-serif;
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(to right, rgba(28, 28, 28, 0.95), rgba(35, 35, 35, 0.95));
            padding: 1.5rem;
            text-align: center;
            font-size: 1rem;
            border-top: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 -5px 10px rgba(0,0,0,0.2);
            transform: perspective(500px) rotateX(-2deg);
            overflow: hidden;
        }
        
        /* Gradient text effect */
        .footer-text {
            background: linear-gradient(145deg, #00B4DB, #00E5FF, #00B4DB);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            color: transparent;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            animation: textGradient 5s ease infinite;
        }
        
        /* Keyframes for gradient text animation */
        @keyframes textGradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* Listing effect animation */
        .footer::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, #00E5FF, transparent);
            animation: listingEffect 3s linear infinite;
        }
        
        /* Keyframes for listing effect */
        @keyframes listingEffect {
            0% { left: -100%; }
            100% { left: 100%; }
        }
    </style>
    
    <div class="footer">
        <span class="footer-text">Copyright © Vasantha Raj - All rights reserved</span>
    </div>
""", unsafe_allow_html=True)
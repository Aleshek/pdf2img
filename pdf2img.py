import os
import argparse
import logging
import time
from pathlib import Path
from PIL import ImageGrab
import pyautogui
import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim
import subprocess
import sys
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pdf_to_images')

class PDFScreenCapture:
    def __init__(self):
        """Initialize the PDF screen capture tool"""
        self.pdf_process = None
        
    def open_pdf(self, pdf_path, startup_delay=5):
        """
        Open the PDF file with the default viewer
        
        Args:
            pdf_path (str): Path to the PDF file
            startup_delay (int): Delay in seconds to wait for the PDF to open
            
        Returns:
            bool: True if successful, False otherwise
        """
        pdf_path = os.path.abspath(pdf_path)
        logger.info(f"Opening PDF: {pdf_path}")
        
        try:
            if platform.system() == 'Windows':
                # On Windows, use os.startfile
                os.startfile(pdf_path)
                self.pdf_process = None  # Can't get process handle with startfile
            elif platform.system() == 'Darwin':  # macOS
                self.pdf_process = subprocess.Popen(['open', pdf_path])
            else:  # Linux and others
                self.pdf_process = subprocess.Popen(['xdg-open', pdf_path])
            
            logger.info(f"Waiting {startup_delay} seconds for PDF to load...")
            time.sleep(startup_delay)
            
            # Try to focus the window (especially helpful on Windows)
            self._focus_pdf_window(pdf_path)
            
            return True
        except Exception as e:
            logger.error(f"Error opening PDF: {e}")
            return False
    
    def _focus_pdf_window(self, pdf_path):
        """
        Try to focus the PDF viewer window
        
        Args:
            pdf_path (str): Path to the PDF file
        """
        try:
            # Get filename from path
            pdf_filename = os.path.basename(pdf_path)
            
            # Try to find and focus window by clicking alt-tab
            pyautogui.keyDown('alt')
            pyautogui.press('tab')
            time.sleep(0.5)
            pyautogui.keyUp('alt')
            time.sleep(0.5)
            
            # Maximum viewport - make sure PDF is fully visible
            pyautogui.hotkey('f11')  # Fullscreen in many PDF viewers
            time.sleep(1)
            
        except Exception as e:
            logger.warning(f"Could not focus PDF window: {e}")
    
    def close_pdf(self):
        """
        Close the PDF viewer
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Try to close with keyboard shortcut first
            pyautogui.hotkey('alt', 'f4')  # Standard Windows close shortcut
            
            # If we have a process handle, terminate it
            if self.pdf_process:
                self.pdf_process.terminate()
                self.pdf_process = None
            
            return True
        except Exception as e:
            logger.error(f"Error closing PDF: {e}")
            return False
    
    def capture_screenshots(self, num_pages, output_dir=None, delay=1):
        """
        Capture screenshots of PDF pages
        
        Args:
            num_pages (int): Number of pages to capture
            output_dir (str): Directory to save screenshots
            delay (float): Delay between screenshots in seconds
            
        Returns:
            list: Paths to saved screenshots
        """
        # Create output directory if not provided
        if not output_dir:
            output_dir = "pdf_images"
        
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Will capture {num_pages} screenshots with {delay}s delay")
        logger.info("Make sure the PDF is visible and properly positioned")
        logger.info("Starting capture in 2 seconds...")
        time.sleep(2)
        
        screenshots = []
        
        # Take screenshots
        for i in range(num_pages):
            # Take screenshot
            logger.info(f"Taking screenshot {i+1}/{num_pages}")
            screenshot = ImageGrab.grab()
            
            # Save screenshot
            screenshot_path = os.path.join(output_dir, f"page_{i+1:03d}.png")
            screenshot.save(screenshot_path)
            screenshots.append(screenshot_path)
            
            logger.info(f"Screenshot saved to: {screenshot_path}")
            
            # Give user time to navigate to next page
            if i < num_pages - 1:
                logger.info(f"Move to the next page. Waiting {delay} seconds...")
                time.sleep(delay)
        
        return screenshots
    
    def compare_images(self, img1_path, img2_path, threshold=0.95):
        """
        Compare two images and determine if they are similar
        
        Args:
            img1_path (str): Path to first image
            img2_path (str): Path to second image
            threshold (float): Similarity threshold (0-1)
            
        Returns:
            bool: True if images are similar, False otherwise
        """
        try:
            # Load images
            img1 = cv2.imread(img1_path)
            img2 = cv2.imread(img2_path)
            
            # Convert to grayscale
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            
            # Resize images to same dimensions if needed
            if gray1.shape != gray2.shape:
                gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))
            
            # Calculate SSIM (structural similarity index)
            score, _ = ssim(gray1, gray2, full=True)
            
            logger.info(f"Image similarity score: {score}")
            return score > threshold
            
        except Exception as e:
            logger.error(f"Error comparing images: {e}")
            return False
    
    def auto_capture_pdf(self, max_pages=500, output_dir=None, delay=1, 
                         similarity_threshold=0.95, consecutive_similar_required=2):
        """
        Automatically capture PDF pages with end-of-document detection
        
        Args:
            max_pages (int): Maximum number of pages to capture
            output_dir (str): Directory to save screenshots
            delay (float): Delay between screenshots in seconds
            similarity_threshold (float): Threshold for image similarity (0-1)
            consecutive_similar_required (int): Number of consecutive similar pages to confirm end
            
        Returns:
            list: Paths to saved screenshots
        """
        # Create output directory if not provided
        if not output_dir:
            output_dir = "pdf_images"
        
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Will capture up to {max_pages} screenshots with auto-detection of end")
        logger.info("Make sure the PDF is visible and properly positioned")
        logger.info("Starting capture in 2 seconds...")
        time.sleep(2)
        
        screenshots = []
        similar_count = 0
        
        # Take screenshots
        for i in range(max_pages):
            # Take screenshot
            logger.info(f"Taking screenshot {i+1}")
            screenshot = ImageGrab.grab()
            
            # Save screenshot
            screenshot_path = os.path.join(output_dir, f"page_{i+1:03d}.png")
            screenshot.save(screenshot_path)
            screenshots.append(screenshot_path)
            
            logger.info(f"Screenshot saved to: {screenshot_path}")
            
            # Check if this page is similar to previous page(s)
            if i > 0:
                is_similar = self.compare_images(screenshots[i-1], screenshots[i], similarity_threshold)
                
                if is_similar:
                    similar_count += 1
                    logger.info(f"Page {i+1} is similar to page {i} ({similar_count}/{consecutive_similar_required})")
                    
                    if similar_count >= consecutive_similar_required:
                        logger.info(f"Detected end of document at page {i+1-consecutive_similar_required}")
                        # Remove the duplicate screenshots
                        for j in range(consecutive_similar_required):
                            os.remove(screenshots[i-j])
                            screenshots.pop()
                        
                        break
                else:
                    similar_count = 0
            
            # Turn to next page using spacebar
            if i < max_pages - 1:
                logger.info("Turning to next page...")
                pyautogui.press('space')
                time.sleep(delay)  # Wait for page to render
        
        return screenshots

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(
        description="Capture PDF pages as images by taking screenshots",
        epilog="This script will open the PDF file, capture screenshots, and optionally close the PDF when done."
    )
    
    parser.add_argument("pdf_path", help="Path to the PDF file to process")
    parser.add_argument("--output-dir", default="pdf_images", help="Directory to save images")
    parser.add_argument("--screenshot", type=int, help="Take N screenshots, manually changing pages")
    parser.add_argument("--auto-capture", action="store_true", help="Automatically capture PDF pages with end detection")
    parser.add_argument("--max-pages", type=int, default=500, help="Maximum pages to capture in auto mode")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between screenshots in seconds")
    parser.add_argument("--similarity", type=float, default=0.95, help="Similarity threshold for auto-detection (0-1)")
    parser.add_argument("--similar-pages", type=int, default=2, help="Number of similar pages to confirm end of document")
    parser.add_argument("--startup-delay", type=int, default=5, help="Delay in seconds to wait for PDF to open")
    parser.add_argument("--no-close", action="store_true", help="Don't close the PDF viewer when done")
    
    args = parser.parse_args()
    
    try:
        # Initialize screen capture tool
        capturer = PDFScreenCapture()
        
        # Open the PDF file
        if not os.path.exists(args.pdf_path):
            logger.error(f"PDF file not found: {args.pdf_path}")
            return 1
            
        if not capturer.open_pdf(args.pdf_path, args.startup_delay):
            logger.error("Failed to open PDF")
            return 1
        
        # Manual screenshot or auto-capture
        if args.screenshot:
            screenshots = capturer.capture_screenshots(
                num_pages=args.screenshot,
                output_dir=args.output_dir,
                delay=args.delay
            )
            logger.info(f"Captured {len(screenshots)} PDF pages as images in {args.output_dir}")
            
        elif args.auto_capture:
            screenshots = capturer.auto_capture_pdf(
                max_pages=args.max_pages,
                output_dir=args.output_dir,
                delay=args.delay,
                similarity_threshold=args.similarity,
                consecutive_similar_required=args.similar_pages
            )
            logger.info(f"Automatically captured {len(screenshots)} PDF pages as images in {args.output_dir}")
            
        else:
            logger.error("Either --screenshot or --auto-capture argument is required")
            # Close PDF before exiting
            if not args.no_close:
                capturer.close_pdf()
            return 1
            
        # Close the PDF viewer
        if not args.no_close:
            logger.info("Closing PDF viewer...")
            capturer.close_pdf()
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

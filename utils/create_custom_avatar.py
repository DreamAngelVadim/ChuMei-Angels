"""
Utility to help create custom avatar with different styles
"""
import cv2
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
import config


def create_avatar(style="anime", hair_color="purple", eye_color="purple"):
    """
    Create custom avatar with specified style
    
    Args:
        style: Style of avatar ('anime', 'realistic', 'cute')
        hair_color: Hair color name
        eye_color: Eye color name
    """
    width, height = config.WINDOW_WIDTH, config.WINDOW_HEIGHT
    
    # Color mappings
    hair_colors = {
        "purple": (120, 70, 180),
        "pink": (180, 120, 255),
        "blue": (200, 150, 100),
        "red": (80, 80, 200),
        "blonde": (100, 200, 255),
        "black": (30, 30, 30),
        "white": (230, 230, 230),
        "green": (150, 200, 100)
    }
    
    eye_colors = {
        "purple": (100, 50, 150),
        "blue": (200, 100, 50),
        "green": (100, 150, 50),
        "brown": (50, 80, 120),
        "red": (50, 50, 200),
        "pink": (150, 100, 255)
    }
    
    hair = hair_colors.get(hair_color.lower(), hair_colors["purple"])
    eyes = eye_colors.get(eye_color.lower(), eye_colors["purple"])
    
    print(f"Creating avatar: style={style}, hair={hair_color}, eyes={eye_color}")
    
    # Create idle image
    idle_img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Gradient background
    for i in range(height):
        intensity = i / height
        if style == "anime":
            # Purple to pink gradient
            r = int(180 + intensity * 75)
            g = int(120 - intensity * 50)
            b = int(200 - intensity * 50)
        elif style == "realistic":
            # Darker, more realistic background
            r = int(40 + intensity * 60)
            g = int(30 + intensity * 50)
            b = int(50 + intensity * 60)
        else:  # cute
            # Pastel colors
            r = int(220 + intensity * 35)
            g = int(200 + intensity * 35)
            b = int(230 + intensity * 25)
        
        idle_img[i, :] = [b, g, r]
    
    center_x, center_y = width // 2, height // 2
    face_radius = 200
    
    # Draw face
    skin_tone = (200, 180, 255) if style == "anime" else (180, 160, 220)
    cv2.circle(idle_img, (center_x, center_y), face_radius, skin_tone, -1)
    cv2.circle(idle_img, (center_x, center_y), face_radius, (150, 120, 200), 3)
    
    # Draw hair based on style
    if style == "anime":
        # Anime-style long hair
        cv2.ellipse(idle_img, (center_x, center_y - 80), (220, 180), 0, 180, 360, hair, -1)
        cv2.ellipse(idle_img, (center_x - 150, center_y), (50, 200), 20, 0, 360, hair, -1)
        cv2.ellipse(idle_img, (center_x + 150, center_y), (50, 200), -20, 0, 360, hair, -1)
        
        # Hair highlights
        highlight = tuple(min(c + 50, 255) for c in hair)
        cv2.ellipse(idle_img, (center_x - 50, center_y - 100), (40, 80), 20, 0, 180, highlight, -1)
        
    elif style == "realistic":
        # More realistic hair
        cv2.ellipse(idle_img, (center_x, center_y - 60), (200, 160), 0, 180, 360, hair, -1)
        cv2.ellipse(idle_img, (center_x - 130, center_y + 20), (60, 180), 15, 0, 360, hair, -1)
        cv2.ellipse(idle_img, (center_x + 130, center_y + 20), (60, 180), -15, 0, 360, hair, -1)
        
    else:  # cute
        # Cute short hair with bangs
        cv2.ellipse(idle_img, (center_x, center_y - 70), (200, 150), 0, 180, 360, hair, -1)
        cv2.ellipse(idle_img, (center_x - 100, center_y), (70, 150), 20, 0, 360, hair, -1)
        cv2.ellipse(idle_img, (center_x + 100, center_y), (70, 150), -20, 0, 360, hair, -1)
        
        # Cute hair accessories
        cv2.circle(idle_img, (center_x - 120, center_y - 80), 20, (150, 200, 255), -1)
        cv2.circle(idle_img, (center_x + 120, center_y - 80), 20, (150, 200, 255), -1)
    
    # Draw eyes
    eye_y = center_y - 40
    left_eye_x = center_x - 60
    right_eye_x = center_x + 60
    
    if style == "anime":
        # Large anime eyes
        cv2.ellipse(idle_img, (left_eye_x, eye_y), (30, 40), 0, 0, 360, (255, 255, 255), -1)
        cv2.ellipse(idle_img, (right_eye_x, eye_y), (30, 40), 0, 0, 360, (255, 255, 255), -1)
        cv2.circle(idle_img, (left_eye_x, eye_y + 5), 20, eyes, -1)
        cv2.circle(idle_img, (right_eye_x, eye_y + 5), 20, eyes, -1)
        cv2.circle(idle_img, (left_eye_x - 8, eye_y - 2), 8, (255, 255, 255), -1)
        cv2.circle(idle_img, (right_eye_x - 8, eye_y - 2), 8, (255, 255, 255), -1)
        
        # Eyelashes
        cv2.ellipse(idle_img, (left_eye_x, eye_y - 35), (32, 15), 0, 0, 180, (50, 30, 80), 2)
        cv2.ellipse(idle_img, (right_eye_x, eye_y - 35), (32, 15), 0, 0, 180, (50, 30, 80), 2)
        
    else:
        # More realistic eyes
        cv2.ellipse(idle_img, (left_eye_x, eye_y), (25, 30), 0, 0, 360, (255, 255, 255), -1)
        cv2.ellipse(idle_img, (right_eye_x, eye_y), (25, 30), 0, 0, 360, (255, 255, 255), -1)
        cv2.circle(idle_img, (left_eye_x, eye_y), 15, eyes, -1)
        cv2.circle(idle_img, (right_eye_x, eye_y), 15, eyes, -1)
        cv2.circle(idle_img, (left_eye_x - 5, eye_y - 3), 5, (255, 255, 255), -1)
        cv2.circle(idle_img, (right_eye_x - 5, eye_y - 3), 5, (255, 255, 255), -1)
    
    # Draw nose
    nose_y = center_y + 20
    cv2.line(idle_img, (center_x, nose_y - 10), (center_x + 5, nose_y + 5), (180, 150, 220), 2)
    
    # Draw mouth (closed, smiling)
    mouth_y = center_y + 60
    cv2.ellipse(idle_img, (center_x, mouth_y - 10), (40, 20), 0, 0, 180, (200, 100, 150), 3)
    
    # Blush
    blush_color = (180, 140, 255) if style == "anime" else (200, 160, 220)
    cv2.circle(idle_img, (center_x - 110, center_y + 30), 25, blush_color, -1)
    cv2.circle(idle_img, (center_x + 110, center_y + 30), 25, blush_color, -1)
    
    # Add text
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = config.CHARACTER_NAME
    text_size = cv2.getTextSize(text, font, 2, 3)[0]
    text_x = (width - text_size[0]) // 2
    cv2.putText(idle_img, text, (text_x, height - 100), font, 2, (255, 255, 255), 3)
    
    subtitle = f"{style.title()} AI Streamer"
    sub_size = cv2.getTextSize(subtitle, font, 1, 2)[0]
    sub_x = (width - sub_size[0]) // 2
    cv2.putText(idle_img, subtitle, (sub_x, height - 50), font, 1, (200, 200, 255), 2)
    
    # Create talking version
    talking_img = idle_img.copy()
    
    # Draw open mouth
    cv2.ellipse(talking_img, (center_x, mouth_y), (30, 40), 0, 0, 360, (100, 50, 80), -1)
    cv2.ellipse(talking_img, (center_x, mouth_y), (30, 40), 0, 0, 360, (200, 100, 150), 3)
    
    # Add tongue for more expression
    cv2.ellipse(talking_img, (center_x, mouth_y + 15), (15, 10), 0, 0, 180, (150, 100, 180), -1)
    
    # Save images
    Path("assets").mkdir(exist_ok=True)
    cv2.imwrite(config.AVATAR_IMAGE_PATH, idle_img)
    cv2.imwrite(config.AVATAR_MOUTH_OPEN_PATH, talking_img)
    
    print(f"✓ Avatar images saved:")
    print(f"  - {config.AVATAR_IMAGE_PATH}")
    print(f"  - {config.AVATAR_MOUTH_OPEN_PATH}")
    
    # Display preview
    cv2.imshow("Idle", idle_img)
    cv2.imshow("Talking", talking_img)
    print("\nPress any key to close preview...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    print("=" * 60)
    print("🎨 Avatar Creator")
    print("=" * 60)
    
    print("\nAvailable styles: anime, realistic, cute")
    print("Available hair colors: purple, pink, blue, red, blonde, black, white, green")
    print("Available eye colors: purple, blue, green, brown, red, pink")
    
    style = input("\nChoose style (default: anime): ").strip() or "anime"
    hair = input("Choose hair color (default: purple): ").strip() or "purple"
    eyes = input("Choose eye color (default: purple): ").strip() or "purple"
    
    print()
    create_avatar(style, hair, eyes)
    
    print("\n✨ Done! You can now run: python main.py")


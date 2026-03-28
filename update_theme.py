import os
import re

base_dir = r"c:\Users\91953\Desktop\stock prediction"
templates_dir = os.path.join(base_dir, "templates")
css_file = os.path.join(base_dir, "static", "css", "style.css")

replacements = [
    (r'rgba\(233,\s*30,\s*99,', r'rgba(0, 229, 255,'), # #e91e63 to #00E5FF in rgba
    (r'--primary-rose', r'--primary-accent'),
    (r'--dark-rose', r'--dark-accent'),
    (r'text-rose', r'text-accent'),
    (r'bg-rose', r'bg-accent'),
    (r'#e91e63', r'#00E5FF'),
    (r'#ad1457', r'#00B8D4'),
]

# Process HTML files
for root, _, files in os.walk(templates_dir):
    for file in files:
        if file.endswith(".html"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Apply general replacements
            for old, new in replacements:
                content = re.sub(old, new, content)
            
            # Specific fixes for about.html background-image
            if file == "about.html":
                content = re.sub(
                    r'style="background-image:\s*url\([^)]+\);\s*background-size:\s*cover;\s*background-position:\s*center;"',
                    r'style="position: relative;"',
                    content
                )
                # Ensure the background-image inline style is removed, wait the exact string was:
                # style="background-image: url('{% static 'images/about_brain_tech_bg.png' %}'); background-size: cover; background-position: center;"
                # Also remove the dark gradient overlay that was hiding the bird image if needed, or keep it. It's:
                # <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(135deg, rgba(160, 27, 44, 0.4) 0%, rgba(10, 10, 10, 0.9) 100%); z-index: 1;"></div>
                # Let's change the red tint in the gradient to teal
                content = re.sub(r'rgba\(160,\s*27,\s*44,', r'rgba(0, 184, 212,', content)
                
            # Specific fix for result.html red/green bubbles (optional but good)
            # result.html uses text-danger and text-success, which is fine.

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

# Process CSS file
with open(css_file, "r", encoding="utf-8") as f:
    css_content = f.read()

for old, new in replacements:
    css_content = re.sub(old, new, css_content)

# Remove hero_bg.png from style.css
css_content = re.sub(
    r"background:\s*linear-gradient\([^)]+\),\s*url\('[^']+'\);",
    r"background: radial-gradient(circle at center, rgba(0, 229, 255, 0.05) 0%, transparent 70%);",
    css_content
)
# Make body background more premium deep navy instead of dark grey
css_content = re.sub(
    r"background:\s*radial-gradient\(circle at top right, #1a1a1a, #050505\);",
    r"background: radial-gradient(circle at top right, #0B1021, #050505);",
    css_content
)

# Update some chat bubble colors
css_content = re.sub(
    r"radial-gradient\(circle at center, #1a0a1a 0%, #050505 100%\)",
    r"radial-gradient(circle at center, #0B1021 0%, #050505 100%)",
    css_content
)

with open(css_file, "w", encoding="utf-8") as f:
    f.write(css_content)

print("Theme updated successfully.")

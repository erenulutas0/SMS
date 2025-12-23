from PIL import Image

img = Image.open("icon.png")
# Convert to RGBA to handle transparency if present, though generated might be RGB
img = img.convert("RGBA")

# Create a white background if it's transparent, or just save.
# But for ICO, we typically want transparent. The generated one likely has white bg.
# Let's try to make white transparent if possible, or just save as is for now.
# Since the prompt said "white background", it's probably solid.
# We'll just save it as ICO.
# Correct format is ICO
img.save("app_icon.ico", format="ICO", sizes=[(256, 256)])
print("Converted to app_icon.ico")

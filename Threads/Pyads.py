import qrcode
import numpy as np
from PIL import Image, ImageDraw
import requests
from io import BytesIO

# ============================
# 🔗 Step 1: User Input for Threads Profile URL
# ============================
#threads_username = "threads"
threads_username = input("Enter your Threads username: ")  # User can input their Threads username
threads_url = f"https://www.threads.net/@{threads_username}/"

# ============================
# 📸 Step 2: Create QR Code
# ============================
qr = qrcode.QRCode(
    version=5,
    error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction for logo
    box_size=10,
    border=4,
)
qr.add_data(threads_url)
qr.make(fit=True)

# Convert QR code to an image
qr_image = qr.make_image(fill="black", back_color="white").convert("RGBA")
qr_width, qr_height = qr_image.size

# ============================
# 🎨 Step 3: Apply Threads Gradient to QR Code
# ============================
gradient = Image.new("RGBA", (qr_width, qr_height), (255, 255, 255, 255))
draw = ImageDraw.Draw(gradient)

# Threads gradient colors
colors = [
    (255, 195, 0),   # Yellow
    (255, 87, 34),   # Orange
    (233, 30, 99),   # Pink
    (156, 39, 176),  # Purple
    (63, 81, 181)    # Blue
]

# Apply gradient effect
for y in range(qr_height):
    r, g, b = [
        int(colors[0][i] * (1 - y / qr_height) + colors[-1][i] * (y / qr_height))
        for i in range(3)
    ]
    draw.line([(0, y), (qr_width, y)], fill=(r, g, b), width=1)

# Merge the gradient into the QR code
qr_array = np.array(qr_image)
gradient_array = np.array(gradient)

for y in range(qr_height):
    for x in range(qr_width):
        if qr_array[y, x, 0] < 128:  # If it's a black pixel
            qr_array[y, x] = gradient_array[y, x]  # Apply gradient color

final_qr = Image.fromarray(qr_array)

# ============================
# 🎭 Step 4: Create a Circular Threads Logo
# ============================
logo_size = qr_width // 3  # Adjust logo size
circle_mask = Image.new("L", (logo_size, logo_size), 0)
mask_draw = ImageDraw.Draw(circle_mask)
mask_draw.ellipse((0, 0, logo_size, logo_size), fill=255)  # Make it a perfect circle

# Create circular logo with gradient
logo = Image.new("RGBA", (logo_size, logo_size), (255, 255, 255, 0))
draw = ImageDraw.Draw(logo)

# Draw Threads-style gradient background
for y in range(logo_size):
    r, g, b = [
        int(colors[0][i] * (1 - y / logo_size) + colors[-1][i] * (y / logo_size))
        for i in range(3)
    ]
    draw.line([(0, y), (logo_size, y)], fill=(r, g, b), width=1)

# Apply circular mask to the entire logo
logo.putalpha(circle_mask)

# ============================
# 📸 Step 5: Insert User Profile Picture (Inside the Circular Logo)
# ============================
user_img_url = f"https://scontent-arn2-1.cdninstagram.com/v/t51.2885-19/450786907_1174411147130821_4003196044560483250_n.jpg?stp=dst-jpg_s320x320_tt6&_nc_ht=scontent-arn2-1.cdninstagram.com&_nc_cat=1&_nc_oc=Q6cZ2QETJhRf7zZgdOTy3joxShsDgmMyBD2HNrYl7ii0rRl7tr5CiZo_kJGaT-iQERAaMfc&_nc_ohc=i8pfDdzo-OcQ7kNvgH50tbX&_nc_gid=NJghJ7N17agDzmNgFpOZ-Q&edm=APs17CUBAAAA&ccb=7-5&oh=00_AYGdfuoL7L7SAFpRTYsfCgubqoSGMbTynVMYUU_htZM0uw&oe=67F2D5C5&_nc_sid=10d13b"  # User provides the URL

try:
    # Fetch the user image from the URL
    response = requests.get(user_img_url)
    user_img = Image.open(BytesIO(response.content)).convert("RGBA")
    
    # Resize the image
    user_img = user_img.resize((logo_size - 20, logo_size - 20), Image.LANCZOS)

    # Create a circular mask for the profile picture
    user_mask = Image.new("L", (logo_size - 20, logo_size - 20), 0)
    user_mask_draw = ImageDraw.Draw(user_mask)
    user_mask_draw.ellipse((0, 0, logo_size - 20, logo_size - 20), fill=255)

    # Apply circular mask to user image
    user_img.putalpha(user_mask)

    # Paste user image onto the logo (centered)
    user_img_position = ((logo_size - user_img.width) // 2, (logo_size - user_img.height) // 2)
    logo.paste(user_img, user_img_position, mask=user_img)

except Exception as e:
    print(f"⚠️ Error loading user profile image from URL: {e}")
    print("Using only Threads logo.")

# ============================
# 🖼️ Step 6: Overlay Circular Logo on QR Code
# ============================
logo_position = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
final_qr.paste(logo, logo_position, mask=logo)

# Save the final QR code
final_qr.save("../SocialHubX_qr.png")

print("✅ QR code with circular Threads logo and user image saved as 'SocialHubX QR Code'.")
final_qr.show()  # Display the QR code

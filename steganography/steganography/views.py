from django.http import HttpResponse
from django.shortcuts import render
import cv2 # for image processing
import numpy as np
import os
import string
from django.core.files.storage import default_storage    #It will help to "Save, read, and delete files using Django's default storage backend."
from django.core.files.base import ContentFile  # Saves binary or text data directly, without creating an actual file.

def home(request):
    if request.method == "POST":
        d = {chr(i): i for i in range(255)}     # It will convert character into pixcel from
        c = {i: chr(i) for i in range(255)}     # It will convert pixcel into character from

        def encode(img_file, msg, password):
            img_array = np.frombuffer(img_file.read(), np.uint8)         # It will convert image into numpy array
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)               # It will convert numpy array into image
            if img is None:
                return None

            msg = password + msg + "###"  # Add password and end marker
            n, m, z = 0, 0, 0
            for char in msg:
                img[n, m, z] = d[char]      # Stores the mapped value of char in the img array.
                n += 1    # Moves to the next row
                m += 1    # Moves to the next column
                z = (z + 1) % 3    # Cycles z through (0 → 1 → 2 → 0) (for RGB).

            _, buffer = cv2.imencode('.png', img)       # Convert `img` into PNG format using OpenCV's `imencode` function.  
                                      # This function returns two values:  
                                      # 1. `retval` (a boolean flag indicating whether the encoding was successful or not).  
                                      # 2. `buffer` (a NumPy array containing the encoded image as a byte stream).  
                                      # We use `_` to ignore `retval` because we only need the encoded image data.
            return buffer   # Return the encoded image as a byte array. This can be used for various purposes such as:  
               # - Writing the image to a file using `.tofile()` 

        def decode(img_file, password):
            img_array = np.frombuffer(img_file.read(), np.uint8)       # It will convert image into numpy array
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)            # It will convert numpy array into image 
            if img is None:
                return "Error loading image"

            message = ""
            n, m, z = 0, 0, 0

            while True:
                char = c[img[n, m, z]]          # Stores the mapped value of imgage array in the char
                message += char
                if message.endswith("###"):
                    break
                n += 1
                m += 1
                z = (z + 1) % 3

            if message.startswith(password):
                return message[len(password):-3]
            else:
                return "Incorrect passcode"

        if 'encode_button' in request.POST:
            msg = request.POST.get("message")
            img = request.FILES.get("image")
            password = request.POST.get("passcode")

            if img and msg and password:
                encoded_image = encode(img, msg, password)
                if encoded_image is not None:
                    file_name = default_storage.save('encrypted_image.png', ContentFile(encoded_image.tobytes()))   ## Save encoded image as a file in Django's default storage || Converts the encoded image into a file-like object.
                    file_url = default_storage.url(file_name)       # Get the URL of the saved file for access or retrieval  
                    return render(request, "index.html", {"image": file_url, "success": "Image encrypted successfully!"})
                else:
                    return render(request, "index.html", {"error": "Error encoding image"})

        elif 'decode_button' in request.POST:
            img = request.FILES.get("image")
            password = request.POST.get("pass")

            if img and password:
                message = decode(img, password)
                if message == "Incorrect passcode":
                    return render(request, "index.html", {"message": "Incorrect passcode"})
                else:
                    return render(request, "index.html", {"message": message})

    return render(request, "templates/index.html")


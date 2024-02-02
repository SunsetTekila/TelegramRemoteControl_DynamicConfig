from PIL import Image

def encode_image(img_path, message, output_path):
    img = Image.open(img_path)

    binary_message = ''.join(format(ord(char), '08b') for char in message)
    data_index = 0

    img_data = list(img.getdata())

    new_img_data = []
    for pixel in img_data:
        if data_index < len(binary_message):
            new_pixel = list(pixel)
            for i in range(3):  # RGB channels
                new_pixel[i] = new_pixel[i] & ~1 | int(binary_message[data_index], 2)
                data_index += 1
            new_img_data.append(tuple(new_pixel))
        else:
            new_img_data.append(pixel)

    new_img = Image.new('RGB', img.size)
    new_img.putdata(new_img_data)
    new_img.save(output_path)

def decode_image(img_path):
    img = Image.open(img_path)

    binary_message = ''
    img_data = list(img.getdata())

    for pixel in img_data:
        for color in pixel:
            binary_message += bin(color)[-1]

    message = ''.join(chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message), 8))
    return message

# Приклад використання
input_image_path = 'input_image.jpg'
output_image_path = 'output_image.jpg'
secret_message = 'Hello, Steganography!'

# Закодувати повідомлення в зображенні
encode_image(input_image_path, secret_message, output_image_path)

# Декодувати повідомлення з зображення
decoded_message = decode_image(output_image_path)
print("Decoded Message:", decoded_message)

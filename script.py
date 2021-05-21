from PIL import Image, ImageEnhance
import fitz
import os
import argparse

# Heuristically check if current pixel is dark blue ink on the enchanced image
# def check_dark_blue_ink(col):
#     if col[2] == 255:
#         return col[2] > col[1] and col[2] > col[0]
#     return col[2] > col[0] and col[2] > col[1] and (col[2] - col[0] > 60 or col[2] - col[1] > 60) and (col[0] < 180 and col[1] < 180)

# Heuristically check if current pixel is blue ink on the enchanced image
def check_blue_ink(col):
    return (col[0] < 180 and col[0] > 130) and col[1] > 80
    # return (col[2] - col[0] > 40 or col[2] - col[1] > 40)

# Heuristically check if current pixel is black ink on the enchanced image
def check_black_ink(col):
    return (col[2] < 40)

# Make it blackish
def modulate_color_black(color):
    return (color[0], color[1], int((color[2]/255) * (20)))

# Make it bluish
def modulate_color_blue(color):
    return (int(max(min(color[0] * 2, 140), 170)), color[1], int(color[2] * 1.5) if color[2] < 125 else color[2] )

# checks the (pixel_range + 1) x (pixel_range + 1) pixels around colored pixel and tests if they are ink pixel by heuristics
def check_surroundings(x, y, color, check_ink):
    test_ink = 0
    for test_x in range(x - pixel_range, x + pixel_range + 1):
        for test_y in range(y - pixel_range, y + pixel_range + 1):
            for fun in check_ink:
                if fun(color):
                    test_ink += 1
                    if (test_ink >= min_ink):
                        return modulate_ink(color)
                    break
    return (255, 0, 255)


parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input-ink', nargs='+', default="blue", choices=['blue', 'dark_blue', 'black'], help="input ink color to be used for detection, supports multiple inks at once")
parser.add_argument('-o', '--output-ink', nargs='?', default="black", choices=['blue', 'black'], help="output ink color of the generated copy")
args = parser.parse_args()

check_ink = []

if("blue" in args.input_ink):
    check_ink.append(check_blue_ink)
if("black" in args.input_ink):
    check_ink.append(check_black_ink)
# if("dark_blue" in args.input_ink):
#     check_ink.append(check_dark_blue_ink)

print(check_ink)

if(args.output_ink == "blue"):
    modulate_ink = modulate_color_blue
elif(args.output_ink == "black"):
    modulate_ink = modulate_color_black

if not os.path.exists("./after-pdf"):
    os.makedirs("./after-pdf")

pdfs = os.listdir('./before-pdf')

for pdf in pdfs:

    pdf_file = fitz.open('./before-pdf/' + pdf)

    i = 0

    final_images = []

    print("Opening PDF: %s\nTotal Pages: %s" % (pdf, len(pdf_file)))

    for (i, page) in enumerate(pdf_file):

        images = page.getImageList()[0]

        xref = images[0]

        print("Extracting Image no: %s" % (i + 1))

        pix = fitz.Pixmap(pdf_file, xref)

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples).convert("HSV")

        print("Converting Image no: %s" % (i + 1))

        # filter = ImageEnhance.Color(img)
        # img = filter.enhance(2)

        # for after applying saturation, detection checks this image
        img.convert('RGB').save('./hmm.png')

        out = Image.new(mode="HSV", size=(img.width, img.height))

        pixel_range = 0
        min_ink = 1

        for x in range(img.width):
            for y in range(img.height):
                out.putpixel((x,y), check_surroundings(x, y, img.getpixel((x, y)), check_ink))

        out = out.convert('RGB')

        final_images.append(out)
        print("Completed processing Image no: %s" % (i + 1))

        # for checking output
        out.save('./kek.png')

    final_images[0].save("./after-pdf/" + pdf,
                         save_all=True, append_images=final_images[1:])
    print("Completed Processing PDF: %s" % (pdf))

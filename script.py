from PIL import Image, ImageEnhance
import fitz
import os
import argparse

# Heuristically check if current pixel is blue ink on the enchanced image
def check_blue_ink(col):
    if col[2] == 255:
        return col[2] > col[1] and col[2] > col[0]
    return col[2] > col[0] and col[2] > col[1] and (col[2] - col[0] > 60 or col[2] - col[1] > 60) and (col[0] < 180 and col[1] < 180)

# Heuristically check if current pixel is black ink on the enchanced image
def check_black_ink(col):
    return (col[0] < 100 and col[1] < 100 and col[2] < 100)

# Make it blackish
def modulate_color_black(color):
    return (color[0]//2, color[1]//2, color[2]//6)

# Make it bluish
def modulate_color_blue(color):
    return (min(int(color[0] * 1.25), 180), min(int(color[1] * 1.25), 180), min(color[2] * 2, 255))

# checks the (pixel_range + 1) x (pixel_range + 1) pixels around colored pixel and tests if they are ink pixel by heuristics
def check_surroundings(x, y, color):
    test_ink = 0
    for test_x in range(x - pixel_range, x + pixel_range + 1):
        for test_y in range(y - pixel_range, y + pixel_range + 1):
            if check_blue_ink(color) or check_black_ink(color):
                test_ink += 1
                if (test_ink >= min_ink):
                    out.putpixel((x, y), modulate_ink(color))
                    return
    out.putpixel((x, y), (255, 255, 255))


parser = argparse.ArgumentParser()
# parser.add_argument('-i', '--input-ink', nargs='?', default="blue", choices=['blue', 'black'], help="input ink color to be used for detection, dark blue ink may give better results with black detection mode")
parser.add_argument('-o', '--output-ink', nargs='?', default="black", choices=['blue', 'black'], help="output ink color of the generated copy")
args = parser.parse_args()

# if(args.input_ink == "blue"):
#     check_ink = check_blue_ink
# elif(args.input_ink == "black"):
#     check_ink = check_black_ink

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

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        print("Converting Image no: %s" % (i + 1))

        filter = ImageEnhance.Color(img)
        img = filter.enhance(2)

        # for testing hmm
        img.save('./hmm.png')

        out = Image.new(mode="RGB", size=(img.width, img.height))

        pixel_range = 1
        min_ink = 3

        for x in range(img.width):
            for y in range(img.height):
                check_surroundings(x, y, img.getpixel((x, y)))

        final_images.append(out)
        print("Completed processing Image no: %s" % (i + 1))

        # for testing kek
        out.save('./kek.png')

    final_images[0].save("./after-pdf/" + pdf,
                         save_all=True, append_images=final_images)
    print("Completed Processing PDF: %s" % (pdf))

from PIL import Image, ImageEnhance
import fitz
import os

# Heuristically check if current pixel is blue ink
def check_ink(col):
    return (col[2] > 190 and (col[2] - col[0] > 40 or col[2] - col[1] > 40))

# Make it very dark
def modulate_color(color):
    return (color[0]//2, color[1]//2, color[2]//6)

# checks the (pixel_range + 1) x (pixel_range + 1) pixels around colored pixel and tests if they are ink pixel by heuristics
def check_surroundings(x, y, color):
    test_ink = 0
    for test_x in range(x - pixel_range, x + pixel_range + 1):
        for test_y in range(y - pixel_range, y + pixel_range + 1):
            if check_ink(color):
                test_ink += 1
                if (test_ink >= min_ink):
                    out.putpixel((x, y), modulate_color(color))
                    return
    out.putpixel((x, y), (255, 255, 255))


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

        print("Converting Image no: %s" % (i))

        filter = ImageEnhance.Color(img)
        img = filter.enhance(4)

        out = Image.new(mode="RGB", size=(img.width, img.height))

        pixel_range = 1
        min_ink = 3

        for x in range(img.width):
            for y in range(img.height):
                check_surroundings(x, y, img.getpixel((x, y)))

        final_images.append(out)
        print("Completed processing Image no: %s" % (i))

    final_images[0].save("./after-pdf/" + pdf, save_all=True, append_images=final_images)
    print("Completed Processing PDF: %s" % (pdf))

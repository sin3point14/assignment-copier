# Assignment-Copier

Converts images of handwritten assignments to black and white while increasing and distorting the font, hence reducing similarity with the original assignment and slightly blurring the text. Works good, even if there are diagrams since this isn't based off OCR.
Currently works for blue ink.
Required python3


### How to use?

- `pip3 install -r requirements.txt`
- `mkdir before-pdf`
- Put all input PDFs into the above made directory
- `python3 script.py`
- Find converted PDFs in after-pdf

#### TODO

- Add support for black ink
- Add support for direct image conversion

### Screenshots

Before:
![Before](samples/before.png)

After:
![After](samples/after.png)
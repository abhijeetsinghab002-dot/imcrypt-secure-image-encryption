# ImCrypt — Secure Image Encryption

ImCrypt is a beginner-friendly Python desktop application that encrypts image files so only someone holding the matching key can restore them.

## Features

- AES-256-GCM and ChaCha20-Poly1305 authenticated encryption
- Fresh random 96-bit nonce and 256-bit key for every image
- Exact restoration of PNG, JPG/JPEG, WebP, GIF and BMP files
- Wrong-key and tampering detection
- Separate `.imc` encrypted file and restricted `.key` file
- Tkinter graphical interface

The complete image file is encrypted as binary data. Unlike pixel modification, this avoids JPEG quality loss and preserves the original file exactly.

## Install and run on Windows

1. Install Python 3.11 or newer and enable **Add Python to PATH**.
2. Open Command Prompt inside this folder.
3. Run `py -m pip install -r requirements.txt`.
4. Run `py -m unittest -v`.
5. Start with `py app.py`.

## Usage

Encrypt: select an image, choose a cipher, save the `.imc` file, then save its generated `.key` separately.

Decrypt: select the `.imc` file and matching `.key`, then choose an output name. The original extension is restored automatically.

Never upload or commit real `.key` files. Losing the key makes recovery impossible. Anyone who obtains both files can decrypt the image.

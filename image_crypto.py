"""Authenticated, lossless image-file encryption helpers."""
import base64
import os
from pathlib import Path
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from PIL import Image

MAGIC=b"IMCRYPT1"
ALGORITHMS={"AES-256-GCM":1,"ChaCha20-Poly1305":2}
ALGORITHM_NAMES={value:name for name,value in ALGORITHMS.items()}
SUPPORTED={".png",".jpg",".jpeg",".webp",".gif",".bmp"}

class ImageCryptoError(Exception): pass

def _validate_image(path):
    path=Path(path)
    if path.suffix.lower() not in SUPPORTED: raise ImageCryptoError("Unsupported image type. Use PNG, JPG, JPEG, WebP, GIF or BMP.")
    try:
        with Image.open(path) as image: image.verify()
    except Exception as exc: raise ImageCryptoError("The selected file is not a valid supported image.") from exc

def _cipher(name,key):
    if len(key)!=32: raise ImageCryptoError("The key must contain exactly 32 bytes.")
    if name=="AES-256-GCM": return AESGCM(key)
    if name=="ChaCha20-Poly1305": return ChaCha20Poly1305(key)
    raise ImageCryptoError("Unsupported encryption algorithm.")

def save_key(key,path):
    target=Path(path);target.write_text("IMCRYPT-KEY-V1:"+base64.urlsafe_b64encode(key).decode("ascii"),encoding="ascii")
    try: os.chmod(target,0o600)
    except OSError: pass

def load_key(path):
    try:
        text=Path(path).read_text(encoding="ascii").strip()
        if not text.startswith("IMCRYPT-KEY-V1:"): raise ValueError
        key=base64.urlsafe_b64decode(text.split(":",1)[1].encode("ascii"))
        if len(key)!=32: raise ValueError
        return key
    except (OSError,ValueError) as exc: raise ImageCryptoError("Invalid or unreadable key file.") from exc

def encrypt_image(source,encrypted_output,key_output,algorithm="AES-256-GCM"):
    source=Path(source);_validate_image(source)
    algorithm_id=ALGORITHMS.get(algorithm)
    if algorithm_id is None: raise ImageCryptoError("Unsupported encryption algorithm.")
    extension=source.suffix.lower().encode("ascii");key=os.urandom(32);nonce=os.urandom(12)
    aad=MAGIC+bytes([algorithm_id])+extension
    ciphertext=_cipher(algorithm,key).encrypt(nonce,source.read_bytes(),aad)
    Path(encrypted_output).write_bytes(MAGIC+bytes([algorithm_id,len(extension),len(nonce)])+extension+nonce+ciphertext)
    save_key(key,key_output)

def decrypt_image(encrypted_source,key_source,output):
    try:
        payload=Path(encrypted_source).read_bytes()
        if len(payload)<12 or payload[:8]!=MAGIC: raise ImageCryptoError("Invalid encrypted image format.")
        algorithm_id,ext_len,nonce_len=payload[8],payload[9],payload[10];cursor=11
        extension=payload[cursor:cursor+ext_len];cursor+=ext_len
        nonce=payload[cursor:cursor+nonce_len];cursor+=nonce_len;ciphertext=payload[cursor:]
        algorithm=ALGORITHM_NAMES.get(algorithm_id)
        if algorithm is None or nonce_len!=12 or not ciphertext: raise ImageCryptoError("Invalid encrypted image metadata.")
        ext=extension.decode("ascii")
        if ext not in SUPPORTED: raise ImageCryptoError("Invalid original image extension.")
        plaintext=_cipher(algorithm,load_key(key_source)).decrypt(nonce,ciphertext,MAGIC+bytes([algorithm_id])+extension)
        target=Path(output)
        if target.suffix.lower()!=ext: target=target.with_suffix(ext)
        target.write_bytes(plaintext);_validate_image(target);return str(target)
    except InvalidTag as exc: raise ImageCryptoError("Decryption failed: wrong key or modified encrypted file.") from exc
    except OSError as exc: raise ImageCryptoError("Unable to read or write the selected file.") from exc

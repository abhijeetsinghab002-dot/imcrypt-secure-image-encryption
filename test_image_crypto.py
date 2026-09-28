import tempfile,unittest
from pathlib import Path
from PIL import Image
from image_crypto import ImageCryptoError,decrypt_image,encrypt_image
class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.folder=Path(self.temp.name);self.source=self.folder/"sample.png";Image.new("RGB",(12,12),(32,120,210)).save(self.source)
    def tearDown(self):self.temp.cleanup()
    def round_trip(self,algorithm):
        encrypted,key,output=self.folder/"sample.imc",self.folder/"sample.key",self.folder/"restored";encrypt_image(self.source,encrypted,key,algorithm);restored=Path(decrypt_image(encrypted,key,output));self.assertEqual(self.source.read_bytes(),restored.read_bytes())
    def test_aes_gcm_round_trip_is_exact(self):self.round_trip("AES-256-GCM")
    def test_chacha20_round_trip_is_exact(self):self.round_trip("ChaCha20-Poly1305")
    def test_same_image_produces_unique_ciphertext(self):
        one,two=self.folder/"one.imc",self.folder/"two.imc";encrypt_image(self.source,one,self.folder/"one.key");encrypt_image(self.source,two,self.folder/"two.key");self.assertNotEqual(one.read_bytes(),two.read_bytes())
    def test_modified_ciphertext_is_rejected(self):
        encrypted,key=self.folder/"sample.imc",self.folder/"sample.key";encrypt_image(self.source,encrypted,key);data=bytearray(encrypted.read_bytes());data[-1]^=1;encrypted.write_bytes(data)
        with self.assertRaises(ImageCryptoError):decrypt_image(encrypted,key,self.folder/"restored")
if __name__=="__main__":unittest.main()

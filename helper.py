from Crypto.Cipher import DES3
from Crypto.Hash import MD5
from Crypto.Util.Padding import unpad
import base64
import logging
from datetime import date

key = "ABCDEFGHIJKLMÃ‘OPQRSTUVWXYZabcdefghijklmnÃ±opqrstuvwxyz"

log = "/var/log/calculaVentaPromedio/calculaVentaPromedio-{0}.log".format(date.today())
logging.basicConfig(
    filename=log,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Helper():

    @staticmethod
    def decrypt_text(text_code):
        # Convertir la clave a un hash MD5
        md5_hash = MD5.new()
        md5_hash.update(key.encode('utf-8'))
        key_array = md5_hash.digest()
        
        # Configurar el cifrador 3DES
        tdes = DES3.new(key_array, DES3.MODE_ECB)
        
        # Convertir el texto encriptado de base64 a bytes
        arr_code = base64.b64decode(text_code)
        
        # Desencriptar el texto
        arr_result = tdes.decrypt(arr_code)
        
        # Eliminar el padding
        arr_result = unpad(arr_result, DES3.block_size)
        
        # Convertir bytes a string
        return arr_result.decode('utf-8')
    
    @staticmethod
    def log(message):
        logging.info(message)
        print(message)

    @staticmethod
    def error(message):
        logging.error(message)
        print(message)

from Crypto.Cipher import AES
from flask import url_for
from itsdangerous import URLSafeSerializer
import base64
import config
import hashlib
import json

class SecurityUtils(object):
    """

        Some of this is redundant. Future TODOs.

    """
    
    MASTER_KEY = config.SECRET_KEY

    def decrypt(self, cipher_text):
        dec_secret = AES.new(self.MASTER_KEY[:32])
        raw_decrypted = dec_secret.decrypt(base64.b64decode(cipher_text))
        clear_val = raw_decrypted.rstrip("\0")
        return clear_val   

    def encrypt(self, clear_text):
        enc_secret = AES.new(self.MASTER_KEY[:32])
        tag_string = (str(clear_text) +
                      (AES.block_size -
                       len(str(clear_text)) % AES.block_size) * "\0")
        cipher_text = base64.b64encode(enc_secret.encrypt(tag_string))
        return cipher_text 

    def get_serializer(self, secret_key=None):
        if secret_key is None:
            secret_key = self.MASTER_KEY
        return URLSafeSerializer(secret_key)           

    def json_decrypt(self, cipher_text):
        return json.loads(self.decrypt(cipher_text))

    def json_encrypt(self, clear_text):
        return self.encrypt(json.dumps(clear_text))
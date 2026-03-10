from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
import base64
import hashlib

class SignatureService:
    def generate_keys(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()
        
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        pem_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return pem_private, pem_public

    def sign_pdf(self, pdf_path: str, private_key_pem: bytes) -> str:
        # Load private key
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None
        )
        
        # Read PDF content to hash
        with open(pdf_path, "rb") as f:
            data = f.read()
            
        # Sign
        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode('utf-8')

    def verify_signature(self, pdf_path: str, signature_b64: str, public_key_pem: bytes) -> bool:
        try:
            public_key = serialization.load_pem_public_key(public_key_pem)
            signature = base64.b64decode(signature_b64)
            
            with open(pdf_path, "rb") as f:
                data = f.read()
                
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False
        except Exception as e:
            print(f"Verification error: {e}")
            return False


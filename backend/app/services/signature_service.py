from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
import base64


class SignatureService:
    """
    Dịch vụ ký số thực sự (RSA-PSS + SHA-256).
    Private key do người dùng tự giữ ở máy của họ.
    Server chỉ lưu public key và chữ ký (signature).
    """

    def verify_signature(self, data: bytes, signature_b64: str, public_key_pem: bytes) -> bool:
        """
        Xác thực chữ ký RSA-PSS.
        - data: nội dung gốc (bytes)
        - signature_b64: chữ ký base64 từ client
        - public_key_pem: public key PEM (bytes)
        """
        try:
            public_key = serialization.load_pem_public_key(public_key_pem)
            signature = base64.b64decode(signature_b64)

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

    def verify_signature_from_file(self, pdf_path: str, signature_b64: str, public_key_pem: bytes) -> bool:
        """
        Xác thực chữ ký với dữ liệu đọc từ file PDF.
        """
        with open(pdf_path, "rb") as f:
            data = f.read()
        return self.verify_signature(data, signature_b64, public_key_pem)

import base64
from tinyec import registry, ec as tec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils
import secrets
import math

curve = registry.get_curve('secp384r1')

def blind(point, value):
    return point * value

def blindEval(point, value):
    return point * value

def unblind(point, value):
    return point * pow(value, -1, curve.field.n)

def get_signature(message):
    with open("keys/private_key.pem", "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    return private_key.sign(message.encode(), ec.ECDSA(hashes.SHA384()))

def verify_signature(signature, message):
    with open("keys/public_key.pem", "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    try:
        public_key.verify(signature, message.encode(), ec.ECDSA(hashes.SHA384()))
        return True
    except:
        return False

def serialize_point_uncompressed(point):
    x_bytes = point.x.to_bytes((int(math.log2(curve.field.p)) + 7) // 8, byteorder='big')
    y_bytes = point.y.to_bytes((int(math.log2(curve.field.p)) + 7) // 8, byteorder='big')

    return base64.b64encode(b'\x04' + x_bytes + y_bytes).decode()

def unserialize_point_uncompressed(point):
    point_bytes = base64.b64decode(point)

    if point_bytes[0] != 0x04:
        raise ValueError("Only uncompressed points are supported.")

    coordinate_size = (len(point_bytes) - 1) // 2
    x_bytes = point_bytes[1:1 + coordinate_size]
    y_bytes = point_bytes[1 + coordinate_size:]

    x = int.from_bytes(x_bytes, byteorder='big')
    y = int.from_bytes(y_bytes, byteorder='big')

    point = tec.Point(curve, x, y)

    if (not point.on_curve):
        raise ValueError("Point not on curve")

    return tec.Point(curve, x, y)

def generate_secure_user_id():
    while True:
        user_id = secrets.randbelow(curve.field.n)
        if user_id != 0:
            return hex(user_id)
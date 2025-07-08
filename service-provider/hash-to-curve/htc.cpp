#include <iostream>
#include <string>
#include <openssl/ec.h>
#include <openssl/bn.h>
#include <openssl/evp.h>
#include <vector>


std::string SerializeECPoint(const EC_GROUP* group, const EC_POINT* point) {
  BN_CTX* ctx = BN_CTX_new();
  size_t len = EC_POINT_point2oct(group, point,
                                  POINT_CONVERSION_UNCOMPRESSED,
                                  nullptr, 0, ctx);

  std::vector<uint8_t> buffer(len);
  EC_POINT_point2oct(group, point,
                     POINT_CONVERSION_UNCOMPRESSED,
                     buffer.data(), buffer.size(), ctx);

  int out_len = 4 * ((len + 2) / 3);
  std::string out(out_len, '\0');

  int encoded_len = EVP_EncodeBlock(reinterpret_cast<unsigned char*>(&out[0]), buffer.data(), len);
  out.resize(encoded_len);

  BN_CTX_free(ctx);
  return out;
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: ./htc <input_string>" << std::endl;
        return 1;
    }

    std::string input(argv[1]);

    const EC_GROUP* group = EC_group_p384();
    EC_POINT* hash = EC_POINT_new(group);
    const uint8_t dst[] = "bison";
    const uint8_t* msg = reinterpret_cast<const uint8_t*>(input.c_str());
  
    EC_hash_to_curve_p384_xmd_sha384_sswu(group, hash,
                                          dst, sizeof(dst) - 1,
                                          msg, input.size());
    
    std::cout << SerializeECPoint(group, hash) << std::endl;

    return 0;
}

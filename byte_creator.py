import json, struct
def encrypt(request):
    request = json.dumps(request)
    key = 171
    plainbytes = request.encode()
    buffer = bytearray(struct.pack(">I", len(plainbytes)))
    for plainbyte in plainbytes:
        cypherbyte = key ^ plainbyte
        key = cypherbyte
        buffer.append(cypherbyte)
    return bytes(buffer)

request = {'smartlife.iot.smartbulb.lightingservice': {'get_light_state':{}}}
print(encrypt(request))
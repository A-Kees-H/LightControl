import json, socket, struct, pickle, time
from pprint import *
import binascii



colourmatrix = {"blue":{"hue":round(244*(256/360)), "saturation":100}, "red":{"hue":round(358*(256/360)), "saturation":100}, "purple":{"hue":round(277*(256/360)), "saturation":100}, "green":{"hue":round(114*(256/360)), "saturation":100}, "dark green":{"hue":round(114*(256/360)), "saturation":100, "brightness":55}}

class Connect:
    def __init__(s, host=None):
        if host is not None:
            s.connect(host)
        else:
            s.get_bulb_ips()
        try:
            s.request_dict = pickle.load(open("encrypted_requests.pkl", "rb"))
        except:
            s.request_dict = s.create_encrypted_request_file()
        

    def create_encrypted_request_file(s):
        encrypted_requests = {}
        for brightness in range(256):
            encrypted_requests[f"b{brightness}"] = s.encrypt(json.dumps({'smartlife.iot.smartbulb.lightingservice':{'transition_light_state':{'brightness': brightness,'on_off':1,'ignore_default':1}}}))
        encrypted_requests["on"] = s.encrypt(json.dumps({'smartlife.iot.smartbulb.lightingservice':{'transition_light_state':{'on_off':1,'ignore_default':1}}}))
        encrypted_requests["off"] = s.encrypt(json.dumps({'smartlife.iot.smartbulb.lightingservice':{'transition_light_state':{'on_off':0,'ignore_default':1}}}))
        encrypted_requests["get"] = s.encrypt(json.dumps({'smartlife.iot.smartbulb.lightingservice':{'get_light_state':{}}}))
        encrypted_requests["reboot"] = s.encrypt(json.dumps({'system':{'reboot':{"delay":1}}}))
        with open('encrypted_requests.pkl', 'wb') as f:
            pickle.dump(encrypted_requests, f, protocol=pickle.HIGHEST_PROTOCOL)
        return encrypted_requests

    def connect(s, host):
        for attempts in range(6):
            try:
                s.socket = socket.create_connection((host, 9999), 2) #(ip, port), €€out
                return   
            except Exception as e:
                print(f"tried {attempts + 1} times")
                print(e)
                if attempts == 0:
                    host = s.ip_tester()
        raise Exception("5 attempts to connect made with no success. The light is probably off or you're not connected to wifi")
                
    @staticmethod
    def encrypt(request):
        key = 171
        plainbytes = request.encode()
        buffer = bytearray(struct.pack(">I", len(plainbytes)))
        for plainbyte in plainbytes:
            cypherbyte = key ^ plainbyte
            key = cypherbyte
            buffer.append(cypherbyte)
        return bytes(buffer)

    @staticmethod
    def decrypt(cyphertext):
        key = 171
        buffer = []
        for cypherbyte in cyphertext:
            plainbyte = key ^ cypherbyte
            key = cypherbyte
            buffer.append(plainbyte)      
        plaintext = bytes(buffer)
        return plaintext.decode()

    def query(s, request):
        s.socket.send(s.encrypt(json.dumps(request)))
        return json.loads(s.decrypt(s.socket.recv(4096)[4:]))

    def direct_query(s, request):
        s.socket.send(request)
        return json.loads(s.decrypt(s.socket.recv(4096)[4:]))

    def off(s):
        s.direct_query(s.request_dict["off"])

    def on(s):
        s.direct_query(s.request_dict["on"])

    def get_brightness(s):
        return s.get_light_state()["brightness"]
    
    def get_warmth(s):
        return s.get_light_state()["color_temp"]

    def get_hsv(s):
        state = s.get_light_state()
        print(state)
        return state["hue"], state["saturation"], state["brightness"]

    def get_on_or_off(s):
        return 'on_off' in s.get_light_state().keys()

    def set_on_or_off(s, on_or_off):
        s.direct_query(s.request_dict[{1 : "on", 0 : "off"}[on_or_off]])

    def set_brightness(s, brightness):
        s.direct_query(s.request_dict[f"b{brightness}"])

    def set_warmth(s, warmth):
        s.query({'smartlife.iot.smartbulb.lightingservice':{'transition_light_state':{'color_temp':warmth}}})

    def set_hsv(s, h, s_, b):
        s.set_hue(h)
        s.set_saturation(s_)
        s.set_brightness(b)

    def set_hue(s, hue):
        s.query({'smartlife.iot.smartbulb.lightingservice':{'transition_light_state':{'hue':hue}}})

    def set_saturation(s, saturation):
        s.query({'smartlife.iot.smartbulb.lightingservice':{'transition_light_state':{'saturation':saturation}}})

    def get_light_state(s):
        data = s.direct_query(s.request_dict["get"])['smartlife.iot.smartbulb.lightingservice']['get_light_state']
        if 'dft_on_state' in data.keys():
            return data['dft_on_state']
        else:
            return data

    def set_light_state(s, cmd, values=[]):
        tls = {'smartlife.iot.smartbulb.lightingservice':{'transition_light_state':{}}}
        if isinstance(cmd, tuple) or isinstance(cmd, list):
            for i, key in enumerate(cmd):
                tls['smartlife.iot.smartbulb.lightingservice']['transition_light_state'][key] = values[i]
        else:
            if cmd in colourmatrix:
                tls['smartlife.iot.smartbulb.lightingservice']['transition_light_state'] = colourmatrix[cmd]
            elif cmd == "on":
                bulb.on()
        print(tls)
        return s.query(tls)

    def get_sysinfo(s):
        s.socket.send(s.encrypt({'system':{'get_sysinfo':{}}}))
        return json.loads(s.decrypt(s.socket.recv(4096)[4:] + s.socket.recv(4096)))

    def ip_tester(s):
        s.get_bulb_ips()
        input()
        for y in range(256):
            for x in range(256):
                try:
                    test_ip = f"192.168.{y}.{x}"
                    print(f"testing IP: {test_ip}")
                    s.socket = socket.create_connection(test_ip, 9999)
                    print(f"IP is {test_ip}")
                    return test_ip
                except:
                    pass
        raise(Exception("no IP found -- make sure your VPN isn't on"))

    def get_bulb_ips(s):
        rc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        rc_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        rc_sock.bind(('0.0.0.0', 0))

        bc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bc_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        bc_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        #print(s.encrypt(json.dumps({'system':{'get_sysinfo':None}}))[4:], ("255.255.255.255", 9999))
        for i in range(3):
            bc_sock.sendto(s.encrypt(json.dumps({'system':{'get_sysinfo':{}}}))[4:], ("255.255.255.255", 9999))
            bc_sock.sendto(binascii.unhexlify("020000010000000000000000463cb5d3"), ("255.255.255.255", 20002))
        rc_sock.settimeout(2)
        response_data, _ = rc_sock.recvfrom(1024)
        print(response_data.decode())


    def receive_udp_response(s, port):
        # Create a UDP socket
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind the socket to a specific port
        udp_socket.bind(('0.0.0.0', port))

        try:
            # Set a timeout for the socket (adjust as needed)
            udp_socket.settimeout(1)
            while True:
                # Receive data from any address
                data, address = udp_socket.recvfrom(1024)
                # Print the received data
                print(f"Received data from {address}: {data.decode()}")

            # Parse the received data as needed

        except socket.timeout:
            print("No response received within the timeout.")

        finally:
            # Close the socket
            udp_socket.close()

    def reboot(s):
        return s.direct_query(s.request_dict[f"reboot"])

    def close(s):
        s.socket.close()


if __name__ == "__main__":
    bulb = Connect()
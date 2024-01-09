sporadically over the last year I've been working on hacking my tp-link smart lightbulb with python. I find this is a great thing to work on because it's pretty easy, has very few barriers to entry and has immediate real-life results

first I found a library (python-kasa) that somewhat worked but was extremely unstable and borderline impossible to debug. I won't go too far into why, but in short: asyncio. also this was a while ago and before I started writing documentation, so I don't remember it too well

later the library maintainer informed me that this was a fork of an older library - pyHS100 - unmangled by a half-baked attempt at asynchrony. this library consistently worked, but was slow, much slower than the proprietary app for the bulb. I reasoned that my PC is no less capable than my iPhone, so I set about fixing it

so, in iterations, I've extracted the core functionality of pyHS100's smartbulb protocol, each iteration getting closer and closer to the minimum code I need to control the light, and a better understanding of what's going on. I eventually discovered that the inefficiency was largely a result of reconnecting for every single request, so if you just keep the socket open and send requests to it, it becomes significantly faster

in this process, I've come to understand the core functionality:
	you create a request in the format of a dictionary
	i.e. 
	{'smartlife.iot.smartbulb.lightingservice':{<type of request>:{<light_attribute>:<value>}}}
	where:
	<type of request> is either "transition_light_state" if you want to alter the light, or "get_light_state" if you want to get its current attributes and values; 
	<light_attribute> is one of "on_off", "hue", "saturation", "color_temp", "brightness", "mode" or "err_code", although I don't know what the last two do[1]. 
	<value> is either 0 or 1 for on_off, a number from 0 to 255 for the next four, and then I don't know for the other two. 

	you convert this dictionary to a string (i.e. how it would be stored in a json file) using json.dumps [ request = json.dumps(request) ], convert it to bytes with the str.encode method [request.encode() ], then encrypt it:

	essentially you create a byte array with 3 empty bytes in it and then a Z, (which I don't really understand[2]) using bytearray(struct.pack(">I"), len(encoded_request)). then you XOR the first byte of the encoded request with 171 (171 ^ byte) and append that to an array, then you XOR that previous result with the next byte from the request and append that, and that with the next, etc until you've reached the end. [3]

	once you've created this stream of encoded bytes, you then send them to a socket at port 9999 of whatever is your bulb's IP (usually in the range 192.168.0-1.100-250)

	if you're changing something about the bulb, then great, that's it. but if you're reading the state of the bulb, then you need to read from the socket. there's nothing hugely complex about this. you run socket.recv(4096) on the same socket and then decrypt the data using the inverse of the cypher

	basically since xor is invertable this works by just doing the same operation in the same order on the encrypted data

	you then have your data, which will be structure in the form of a dictionary

and that's it. it's actually very simple once you know it, but I'm indebted to whoever figured it out in the first place. - the comments of the pyHS100 module using them credit Lubomir Stroetmann and Tobias Esser for the encryption and decryption algorithms, so kudos to them and the creators of pyHS100

Optimisation:
as previously mentioned, I discovered that the delay on repeated requests was a result of opening and closing the socket connection every time you make a query, and fixed this by opening the connection at start-up and closing at program end

my next stab at optimisation was to pre-generate the final bytes requests. knowing that there are only so many possible requests (2 + 256 + 256 + 256 + 256 + 1 = 1027) for on_off, hue, saturation, brightness, color_temp, get_light_state respectively, you can cut out the encryption times by pre-generating the encrypted requests and storing them locally. you could do the same for decryption, but I can't be arsed

I haven't tested how much time this saves, if any at all, but I suspect that it may be a little slower for single requests, but faster for a series of them, because loading a 32kb pkl file[4] into memory probably takes longer than the original encryption algorithm, but accessing a value in a dictionary likely takes less time than the cypher does

if it is slower, I'd like to test the average of how many requests it takes for it to catch up

ESP32:
after I'd understood all this and rewritten it a few dozen times, I decided I wanted to run it from an esp device. because python is my main language and I'm too lazy to learn more than the basics of C, I chose to run it on micropython

after a huge amount of hassle with serial port interpreters (I literally installed 5 of them) that just did not work, reddit user u/mu__rray - absolute hero of the year - suggested I use pyserial in a specific way (rts and dtr turned off) that either wasn't possible or didn't work with the other serials. this worked ... barely. it's glitchy but I could get enough access to the python REPL to connect the thing to the internet and activate webrepl

anyway, back to light control. I looked into socket access with micropython and it's slightly different in a completely unnecessary - and I'd argue extremely stupid - way to normal python, but not very complicated in that. so I reimplemented my light control code with this micropython module. it didn't work. and then in a slightly different way. it didn't work. and then in a slightly different way. it didn't work. I went on with this a fair bit, had no luck, then moved house and lost interest for about half a year, which takes me to now, where I tried again with the ol' throwing everything at the wall technique. I set up a for loop to run 10 times with 4 different varieties of code. strangely enough, the first code to work was exactly the code I'd tried 6 months ago, now working. so I set up a simple button for my esp32 and now I can turn the light on and off with the mere click of a switch. how futuristic

[1] - my guess would be that "mode" has some relation to bulb set-up when it runs a temporary wifi network you connect your phone to so the app can connect the device to your wifi, and I flat out don't care what err_code is, but it's probably the code of whatever error it had last

[2] - it looks like this: bytearray(b'\x00\x00\x00Z')

[3] - considering XOR is analogous to +, this seems to me like it's basically a fibonacci sequence operated on a stream with 171 in position one and each byte of the request in order after that 

	the practical result is that you can't decode the sequence if any elements from the beginning are missing, but it's okay to lose a few from the end. I'm not actually sure why its encrypted in the first place, so the logic of this escapes me. maybe some of the engineers felt it would be an interesting thing to do, or maybe there are less mundane uses of tp-link devices and they've just reused the protocol as good practice. that sounds about right. --- correction, no, it's almost certainly so that if the signal is corrupted, it will be 100% broken rather than just a tiny bit broken. it's a crude equivalent of a checksum

[4] - I would have used json, but it won't accept bytes for whatever reason. maybe something related to that old hacking thing where you try and escape the entry box? forgotten what its called

h = 240
w = 320

for c in range(int(h/16)):
    for i in range(int(w/16)-1):
        print('0,0.', end="")
    print('0,0\n', end="")

print("\n\n\n")

default = "0,0"
separator = "."

for c in range(int(h/16)):
    print(separator.join([default] * int(w/16)) + '\n', end="")

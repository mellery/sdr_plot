with open('invalid.txt') as f:
    lines = f.read().splitlines()
    url = 'https://www.qrzcq.com/call/'
    for line in lines:
        if line.split()[7][0] is not '<':
            print(url+line.split()[7])

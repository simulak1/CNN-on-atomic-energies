def wout(string):
    with open("OUT",'a') as f:
        f.write(string+'\n')

def witer(string):
    with open("ITER",'a') as f:
        f.write(string+'\n')

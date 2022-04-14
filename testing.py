import time
from epics import caget, caput, camonitor, PV
from numpy.random import rand

prefix = 'RELAY:'
#prefix = '5trap:relay:'

test_pvs = [
        'test_i1',
        'test_f1',
        'test_c2',
        'test_i3',
        'test_f3',
        'test_c3',
        'test_I3',
        'test_F3',
        'test_C3',
]

time_out = 0.1
counter = 0
while True:
    
    for pvname in test_pvs:
        dtype = pvname.rsplit('_', 1)[1]
        count = int(dtype[1:])
        if dtype.isupper():
            values = rand(1)*10
        else:
            values = rand(count)*10
        print(values)

        dtype = dtype[0]
        if dtype.lower().endswith(('i', 'c')):
            values = values.astype(int)
        if dtype.lower() == 'c':
            values += 100
            string = ''
            for v in values:
                string += chr(v)
            values = string
        
        print(pvname, 'put value return', values, end=' ')
        print(caput(prefix+pvname, values, timeout=time_out))

        time.sleep(0.1)
 
        if dtype.lower() == 'c':
            print(pvname, 'get return', caget(prefix+pvname, as_string=True, timeout=time_out))
            print(pvname, 'get return', caget(prefix+pvname, timeout=time_out))
        else:
            print(pvname, 'get return', caget(prefix+pvname, timeout=time_out))
    
    time.sleep(1)

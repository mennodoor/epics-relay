#!/bin/python3

import sys
import re
import logging
logging.basicConfig(filename='relay.log', level=logging.ERROR)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

from pcaspy import *

prefix = 'RELAY:'


##################################################################
# The name structure of a dynamicly created pv should be like this:
#
# <prefix>:<name>_<dtype><count>
# 
# the count gives the number of elements in this PVs array, single
# PV is obviously count=1, Spectrum of 5000 bins is count=5000,
# an array of 100 bufferd values for a time-plot is count=100
#
# following dtypes are available:
# f : float
# i : int
# c : char
# X (capital letter of prior dtypes) : a right appending buffer
##################################################################


# fixed pvs for listing and deletion
static_pvdb = {
    "pvlist": { 'type': 'char', 'count': 16383, 'value': "" },
    "delpv":  { 'type': 'char', 'count': 254,   'value': "" }
}

dynamic_pvdb = {}


class RelayDriver(Driver): 
    """
    The RelayDriver handles writing to existing pvs, including the pvlist, and allows for pv deletion
    via the delpv pv. Dynamicly created pvs are writen via default setParam(). Read is not overloaded.
    """
    #global dynamic_pvdb

    def __init__(self):
        Driver.__init__(self)
        logging.debug('Driver init complete.')

    def delPV(self, reason: str):
        '''
        This method deletes all entries off a given pv name in the manager dictionaries, the driver dictionary and
        deletes the SimplePV object itself.

        :param reason: Name of the PV to be removed
        :type reason: str
        :return: Bool
        :rtype: bool
        '''
        basename = str(reason)
        fullname = prefix + basename
        try:
            if fullname in dynamic_pvdb:
                logging.debug('delPV: '+basename)
                dynamic_pvdb.pop(fullname)
                self.pvDB.pop(reason)
                driver.manager.pvs[self.port].pop(reason)
                pv = driver.manager.pvf.pop(prefix + reason)
                del pv
                self.updatepvlist()
                return True
            else:
                return False
        except Exception as e:
            logging.error('ERROR: delPv raised exception:\n'+str(e))
            return False

    def update_pvlist(self):
        '''
        Reads the dynamic_pvdb database and creates a string listing all pv names and updates the pv 'pvlist' with
        that created list.
        '''
        try:
            pvlist = ""
            for key, item in dynamic_pvdb.items():
                pvlist += str(key) + ","
            self.setParam('pvlist', pvlist[:-1])
            self.updatePV('pvlist')
        except Exception as e:
            logging.error('ERROR: update_pvlist raised exception:\n'+str(e))
        return

    def append_buffer(self, reason, value):
        '''
        Appending a buffer pv with new value and losing the most left if neccessarry.
        '''
        try:
            pvinfo = self.getParamInfo(reason)
            count = pvinfo['count']
            dtype = pvinfo['type']
            buffer = self.getParam(reason)
            if not isinstance(buffer, list) and not isinstance(buffer, str):
                buffer = [buffer]
            if len(buffer) == count:
                buffer = buffer[1:]
            if dtype == 2: # 2 is char
                buffer += value
            else:
                buffer.append(value)
            self.setParam(reason, buffer)
            self.updatePV(reason)
        except:
            logging.error('ERROR: append_buffer raised exception:\n'+str(e))

    def write(self, reason: str, value):
        '''
        Just for reacting on the delpv case. Otherwise it would not be neccessary.
        '''
        logging.debug('write:\t' + reason +'\t'+ str(value) +'\t'+ str(type(value)) )
        status = True
        try:
            fullname = prefix + reason
            if reason == "delpv":
                status = self.delPV(value)
                if status: self.setParam(reason, value)
            elif fullname in dynamic_pvdb:
                # if its a buffer, handle it differently
                if reason.rsplit('_', 1)[1][0].isupper():
                    self.append_buffer(reason, value)
                else:
                    self.setParam(reason, value)
            else:
                status = False
        except Exception as e:
            logging.error('ERROR: write query raised exception:\nreason: '+str(reason)+' value: '+str(value)+'\n\t'+str(e) )
            status == False
        if status:
            status = self.getParam(reason)
        return status


class DynamicServer(SimpleServer):
    '''
    This SimpleServer derivate allows to create PVs on the fly, pvExistTest is overloaded to send a 'fake'
    acknowledgement for non-existing pvs if the pv name fits the prefix and suffix rules. pvAttach is overloaded
    to create the needed pv on the fly. If this has happend for a specific pvname, the existing pv is handled by
    the server in the default way.
    '''
    def __init__(self):
        SimpleServer.__init__(self)
        # please read the implementation of the pcaspy DriverManager for more information regarding this port
        self.port = "default" 
        logging.debug('Server init complete.')

    def pvExistTest(self, context, addr, fullname):
        '''
        This is overloaded to already return an "OK" if the prefix and the suffix is fine. Otherwise the orignal
        function will manage the response.
        '''
        try:
            suffix_correct = re.search(r'_[ifcIFC]\d+$', fullname)
            if fullname.startswith(prefix) and suffix_correct:
                return cas.pverExistsHere
            else: # if the prefix is not fine, just let the SimpleServer function handle the response
                return SimpleServer.pvExistTest(self, context, addr, fullname)
        except Exception as e:
            logging.error('ERROR: pvExistTest raised exception:\n'+str(e))
            return SimpleServer.pvExistTest(self, context, addr, fullname)

    def create_PVInfo(self, basename):
        '''
        Create a PVInfo object based on the suffix of the fullname.
        '''

        # default stats
        info = {
            "type" : "float",
            "count" : 1,
            "value" : 0
        }
        
        # configure PV stats
        count = int(dtype[1:])
        info['count'] = count
        dtype = basename.rsplit("_", 1)[1]
        if dtype[0].lower() == "f":
            info['type'] = 'float'
        elif dtype[0].lower() == "i":
            info['type'] = 'int'
        elif dtype[0].lower() == "c":
            info['type'] = 'char'
            info['value'] = ''
            if count <= 1: # char 1 does not work, its a pcaspy bug
                count = 2
        if dtype[0].isupper() and count == 1:
            raise ValueError('Buffer with length 1 makes no sense')

        # create PVInfo and SimplePV object
        logging.debug('dynamic, pvinfo'+str(info))
        pvinfo = PVInfo(info)
        pvinfo.reason = basename
        pvinfo.name = prefix + basename
        
        return pvinfo
                    

    def add_new_pv(self, fullname):
        ''' 
        Adds new SimplePV object to appropriate databases, making it accessable for the driver.
        '''
        # pv-name without the prefix
        basename = fullname[len(prefix):]

        # create PVInfo and SimplePV objects
        pvinfo = self.create_PVInfo(basename)
        pv = SimplePV(fullname, pvinfo)

        # add PV to dynamic database
        dynamic_pvdb[fullname] = pv

        # add the PV to the manager dictionaries
        driver.manager.pvf[pvinfo.name] = pv
        driver.manager.pvs[self.port][basename] = pv

        # add the PV to the drivers pvDB
        # please read the implementation of the pcaspy Driver/DriverManager to clarify
        data = driver.Data()
        data.value = pv.info.value
        relaydriver.pvDB[basename] = data
        
        return None

    def pvAttach(self, context, fullname):
        '''
        Manages the automatic creation and/or return of SimplePV objects from the database.
        
        The object 'driver' is actually from the pcaspy module, its imported as part of the global objects. 
        Please read the documentation/implementation of the pcaspy Driver/DriverManager to clarify.
        '''
        logging.debug('handling pv request, fullname: '+str(fullname))

        # check if name is in static_pvdb, if so just use the Mother-class pvAttach (SimpleServer)
        if fullname[len(prefix):] in static_pvdb:
            logging.debug('static pv requested')
            ##if debug: print("static, return SimpleServer.pvAttach of", fullname, fullname[len(prefix):])
            return SimpleServer.pvAttach(self, context, fullname)

        # check if name starts with relay servers prefix (check if it belongs here)
        elif fullname.startswith(prefix):
            # if PV does not exist already, create it:
            if fullname not in dynamic_pvdb:
                logging.debug('new dynamic pv requested')
                try:
                    self.add_new_pv(fullname)

                except Exception as e:
                    # something went wrong, let Mother class handle response
                    logging.error('ERROR: pvAttach raised exception:\n'+str(e))
                    return SimpleServer.pvAttach(self, context, fullname)
            
            logging.debug('return dynamic pv')
            return dynamic_pvdb[fullname]

        else:
            # not our pv, let Mother class handle response
            logging.debug('not our pv...')
            return SimpleServer.pvAttach(self, context, fullname)

if __name__ == '__main__':
    try:
        server = DynamicServer()
        server.createPV(prefix, static_pvdb)
        relaydriver = RelayDriver()
        print('Running...\n')
        # process CA transactions
        while True:
            server.process(0.001)
    except:
        raise

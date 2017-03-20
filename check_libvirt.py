#!/usr/bin/python
import time
import libvirt
import os,sys


def get_baseinfo(tag, uuid):
    conn = libvirt.open("qemu:///system")
    domain = conn.lookupByUUIDString(uuid)

    '''domain.info()
        state: the running state, one of virDomainState
        maxMem: the maximum in KBytes allowed
        memory: the memory in KBytes used by the domain
        nrVirtCpu: the number of virtual CPUs for the domain
        cpuTime: the CPU time used in nanoseconds
    '''

    '''refer to http://libvirt.org/html/libvirt-libvirt-domain.html#virDomainState 
       virDomainState 
       VIR_DOMAIN_NOSTATE     = 0 : no state
       VIR_DOMAIN_RUNNING     = 1 : the domain is running
       VIR_DOMAIN_BLOCKED     = 2 : the domain is blocked on resource
       VIR_DOMAIN_PAUSED      = 3 : the domain is paused by user
       VIR_DOMAIN_SHUTDOWN    = 4 : the domain is being shut down
       VIR_DOMAIN_SHUTOFF     = 5 : the domain is shut off
       VIR_DOMAIN_CRASHED     = 6 : the domain is crashed
       VIR_DOMAIN_PMSUSPENDED = 7 : the domain is suspended by guest power management
       VIR_DOMAIN_LAST        = 8 : NB: this enmu value will increase over time as new events aree added to the 
                                    libvirt API. It reflects the last state supported by this version of ther libvirt API.
    '''
    tags = ['state', 'maxMem', 'memory', 'nrVirtCpu', 'cpuTime']
    d = {}
    for index in range(0, len(tags)):
        d[tags[index]] = domain.info()[index]
    print d[tag]
    conn.close()

def get_cpuinfo(tag, uuid):
    conn = libvirt.open("qemu:///system")
    if tag == 'utilzation':
        domain = conn.lookupByUUIDString(uuid)
        t1 = time.time()
        #cpuTime
        c1 = int (domain.info()[4])
        time.sleep(1);
        t2 = time.time();
        c2 = int (domain.info()[4])
        #nrVirtcpu
        c_nums = int (domain.info()[3])
        usage = (c2-c1)*100/((t2-t1)*c_nums*1e9)
        print "%f" % (usage) 
    conn.close() 

def get_netinfo(tag, uuid):
    '''ifaceinfo:
       rx_bytes, rx_packets, rx_errs, rx_drop, tx_bytes, tx_packets, tx_errs, tx_drop
    '''
    tags = ['rx_bytes', 'rx_packets', 'rx_errs', 'rx_drop', 'tx_bytes', 'tx_packets', 'tx_errs', 'tx_drop']
    if tag not in tags:
        return

    from xml.etree import ElementTree
    conn = libvirt.open("qemu:///system")
    domain = conn.lookupByUUIDString(uuid)
    tree = ElementTree.fromstring(domain.XMLDesc())
    ifaces = tree.findall('devices/interface/target')
    d = {}
    for i in ifaces:
        iface = i.get('dev')
        ifaceinfo = domain.interfaceStats(iface)
        for index in range(0, len(tags)):
            if tags[index] not in d:
                d[tags[index]] = 0
            d[tags[index]] = d[tags[index]] + ifaceinfo[index]
    print d[tag]
    conn.close()

def get_diskinfo(tag, uuid):
    tags = ['utilzation', 'rd_req', 'rd_bytes', 'wr_req', 'wr_bytes']
    if tag not in tags:
        return
    from xml.etree import ElementTree
    conn = libvirt.open("qemu:///system")
    domain = conn.lookupByUUIDString(uuid)
    tree = ElementTree.fromstring(domain.XMLDesc())
    devices = tree.findall('devices/disk/target')

    numlist = [0] * 8
    for d in devices:
        device = d.get('dev')
        try:
            devinfo = domain.blockInfo(device)
            '''
                struct virDomainBlockInfo {
                    long long capacity(total) : logical size in bytes of the image (how much storage the guest will see)
                    long long allocation      : host storage in bytes occupied by the image (such as hightest allocated extent 
                                      if there are no holes, similar to 'du')
                    long long physical(used)  : host physical size in bytes of the image container (last offset, similar to 'ls')
                }
            '''

            devstats = domain.blockStats(device)
            '''
                struct virDomainBlockStatsStruct {
                    long long rd_req   : number of read requests
                    long long rd_bytes : number of read bytes
                    long long wr_req   : number of written bytes
                    long long wr_bytes : number of written bytes
                    long long errs     : In Xen this returns the mysterious 'oo_req'. 
                }
            '''
            for i in range(0, 8):
                numlist[i] = numlist[i] + (list(devinfo) + list(devstats))[i]
         
        except libvirt.libvirtError:
            pass
    conn.close()
    
    if tag == 'utilzation':
        print numlist[2]/numlist[0]
    elif tag == 'rd_req':
        print numlist[3]
    elif tag == 'rd_bytes':
        print numlist[4]
    elif tag == 'wr_req':
        print numlist[5]
    elif tag == 'wr_bytes':
        print numlist[6]

def get_meminfo(tag, uuid):
    if tag <> 'utilzation':
        return
    conn = libvirt.open("qemu:///system")
    domain = conn.lookupByUUIDString(uuid)
    domain.setMemoryStatsPeriod(10)
    meminfo = domain.memoryStats()
    #free_mem = float(meminfo['unused'])
    #total_mem = float(meminfo['available'])
    #util_mem = ((total_mem-free_mem) / total_mem)*100
    print float(meminfo['rss']) / meminfo['actual']
    conn.close()

if __name__ == "__main__":
    
    tag1 = sys.argv[1]
    tag2 = sys.argv[2]
    uuid = sys.argv[3]

    if tag1 == 'base':
        get_baseinfo(tag2, uuid)
    elif tag1 == 'cpu':
        get_cpuinfo(tag2, uuid)
    elif tag1 == 'net':
        get_netinfo(tag2, uuid)
    elif tag1 == 'disk':
        get_diskinfo(tag2, uuid)
    elif tag1 == 'mem':
        get_meminfo(tag2, uuid)

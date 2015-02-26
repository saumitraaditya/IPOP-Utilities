#! /usr/bin/env python
import re
import time
import sys
import os
import copy
import json

PARAMS = {}

METRICS = {}

Desc_Skel = {}

peers = []
METRICS_CACHE_MAX = 5

descriptors = []


# Where to get the stats from
net_stats_file = "/home/user/ipop-14.07.01_ubuntu14/"


def create_desc(skel, prop):
    d = skel.copy()
    for k,v in prop.iteritems():
        d[k] = v
    return d

def metric_init(params):
    global descriptors
    global Desc_Skel

#    print INTERFACES
    time_max = 60

    Desc_Skel = {
        'name'        : 'XXX',
        'call_back'   : get_xmpp_time,
        'time_max'    : 60,
        'value_type'  : 'float',
        'format'      : '%.0f',
        'units'       : '/s',
        'slope'       : 'both', # zero|positive|negative|both
        'description' : 'XXX',
        'groups'      : 'IPOP-PEERS',
    }
    
    update_descriptors()
    return descriptors

    
def update_descriptors():
    #this is how you add metrics
    global descriptors
    print("UPDATE DESCRIPTOR")
    global peers
    global Desc_Skel
    global METRICS
    
    data_file = net_stats_file + "peer_list_ganglia.json"
    with open(data_file, 'r') as inf:
        for line in inf:
            data = json.loads(line)
        # Keep count of online links.
        descriptors.append(create_desc(Desc_Skel, {
        "name"        : "peer_ipop_links",
        "units"       : "links",
        "call_back"   : get_count,
        "description" : "number of active links",
        'groups'      : 'IPOP-NODE'
        }))
    for node in data:
        if str(node) not in peers:
            peers.append(str(node))
            test = str(node)
            
            #this chunk is needed to find all of the delta values
            METRICS["peer_bytes_recv_-"+test] = 0  
            METRICS["peer_bytes_recv_-"+test+"_time"] = time.time()
            METRICS["peer_bytes_recv_-"+test+"_delta"] = 0
            METRICS["peer_bytes_sent_-"+test] = 0
            METRICS["peer_bytes_sent_-"+test+"_time"] = time.time()
            METRICS["peer_bytes_sent_-"+test+"_delta"] = 0
            try:
                METRICS["peer_bytes_recv_-"+test] += data["stats"][0]["recv_total_bytes"]
                METRICS["peer_bytes_sent_-"+test] += data["stats"][0]["sent_total_bytes"]
            except:
                pass
            
            descriptors.append(create_desc(Desc_Skel, {
            "name"        : "peer_bytes_recv_-" + test,
            "units"       : "bytes/sec",
            "call_back"   : get_recv_total_bytes,
            "description" : "bytes recvd per second",
            }))
            descriptors.append(create_desc(Desc_Skel, {
            "name"        : "peer_bytes_sent_-"+ test,
            "units"       : "bytes/sec",
            "call_back"   : get_sent_total_bytes,
            "description" : "bytes sent per second",
            }))
            descriptors.append(create_desc(Desc_Skel, {
            "name"        : "peer_rtt_-"+ test,
            "units"       : "jumps",
            "call_back"   : get_rtt,
            "description" : "Routing transit time",
            }))
            descriptors.append(create_desc(Desc_Skel, {
            "name"        : "peer_xmpp_time_-"+ test,
            "units"       : "seconds",
            "call_back"   : get_xmpp_time,
            "description" : "XMPP time",
            }))
            descriptors.append(create_desc(Desc_Skel, {
            "name"        : "peer_status_-"+ test,
            "units"       : "On/Off",
            "call_back"   : get_status,
            "description" : "On or Off",
            }))
            descriptors.append(create_desc(Desc_Skel, {
            "name"        : "peer_conn_age_-"+ test,
            "units"       : "seconds",        
            "call_back"   : get_conn_age,
            "description" : "age of ipop link in seconds",
            }))
           
    return descriptors        


def metric_cleanup():
    '''Clean up the metric module.'''
    pass
    

def get_xmpp_time(name):
    data_file =  net_stats_file + name.split("-")[1]+"_ganglia_data.json"
    with open(data_file, 'r') as inf:
        for line in inf:
            data = json.loads(line)

    if ("peer_xmpp_time_-"+ data["ip4"]) == name:
        return data["xmpp_time"]
    return 0

def get_recv_total_bytes(name):
    global METRICS
    if (time.time() - METRICS[name+"_time"]) > METRICS_CACHE_MAX:

        output = 0
        data_file =  net_stats_file + name.split("-")[1]+"_ganglia_data.json"
        with open(data_file, 'r') as inf:
            for line in inf:
                data = json.loads(line)


        if ("peer_bytes_recv_-"+ data["ip4"]) == name:
            try:
                output = output + data["stats"][0]["recv_total_bytes"]
            except:
                pass

        METRICS[name+"_delta"] = (output - METRICS[name])/(time.time() - METRICS[name+"_time"])
        METRICS[name] = output
        METRICS[name+"_time"] = time.time()
    return METRICS[name+"_delta"]

	

def get_sent_total_bytes(name):
    global METRICS
    if (time.time() - METRICS[name+"_time"]) > METRICS_CACHE_MAX:
        output = 0
        data_file =  net_stats_file + name.split("-")[1] + "_ganglia_data.json"
        with open(data_file, 'r') as inf:
            for line in inf:
                data = json.loads(line)


        if ("peer_bytes_sent_-"+ data["ip4"]) == name:
            try:
                output = output + data["stats"][0]["sent_total_bytes"]
            except:
                pass

        METRICS[name+"_delta"] = (output - METRICS[name])/(time.time() - METRICS[name+"_time"])
        METRICS[name] = output
        METRICS[name+"_time"] = time.time()
    return METRICS[name+"_delta"]

def get_rtt(name):
    data_file =  net_stats_file + name.split("-")[1] + "_ganglia_data.json"
    with open(data_file, 'r') as inf:
        for line in inf:
            data = json.loads(line)


    try:
        if ("peer_rtt_-" + data["ip4"]) == name:
            if data["stats"][0]["best_conn"]:
                return data["stats"][0]["rtt"]
    except:
        pass
    return 0

def get_status(name):

    data_file =  net_stats_file + name.split("-")[1] + "_ganglia_data.json"
    with open(data_file, 'r') as inf:
        for line in inf:
            data = json.loads(line)


    if ("peer_status_-"+data["ip4"]) == name:
        if data["status"] == "online":
            return 1
    return 0
    
def get_count(name):
    data_file =  net_stats_file + "peer_list_ganglia.json"
    try:
        with open(data_file, 'r') as inf:
            for line in inf:
                data = json.loads(line)
        num_links = float(len(data))
        return num_links
    except:
        return 0
        
def get_conn_age(name):
    data_file =  net_stats_file + name.split("-")[1] + "_ganglia_data.json"
    with open(data_file, 'r') as inf:
        for line in inf:
            data = json.loads(line)
            
    if ("peer_conn_age_-"+data["ip4"]) == name:
        if data["status"] == "online":
            return data["last_time"]
    return 0



#for testing only
if __name__ == '__main__':
    
    params = {}
    metric_init(params)
    while True:
        for d in descriptors:
            print d
            v = d['call_back'](d['name'])
            print ('value for %s is ' + d['format']) % (d['name'], v)
            time.sleep(5)



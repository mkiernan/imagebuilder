#!/usr/bin/python3

import json
import socket
#import urllib2
import urllib.request as urllib2
import time

metadata_url = "http://169.254.169.254/metadata/scheduledevents?api-version=2019-08-01"
this_host = socket.gethostname()


def get_scheduled_events():
    req = urllib2.Request(metadata_url)
    req.add_header('Metadata', 'true')
    resp = urllib2.urlopen(req)
    data = json.loads(resp.read())
    return data


def handle_scheduled_events(data):
    for evt in data['Events']:
        eventid = evt['EventId']
        status = evt['EventStatus']
        resources = evt['Resources']
        eventtype = evt['EventType']
        resourcetype = evt['ResourceType']
        notbefore = evt['NotBefore'].replace(" ", "_")
        description = evt['Description']
        eventSource = evt['EventSource']
        if this_host in resources:
            print("+ Scheduled Event. This host " + this_host +
                " is scheduled for " + eventtype + 
                " by " + eventSource + 
                " with description " + description +
                " not before " + notbefore)
            # Add logic for handling events here
            if eventtype == "Preempt":
                print("**** EVICTION SCHEDULED *****")
                # dump calcs / cleanup /checkpoint / save state

def main():
    while True: 
        data = get_scheduled_events()
        handle_scheduled_events(data)
        time.sleep(1)


if __name__ == '__main__':
    main()

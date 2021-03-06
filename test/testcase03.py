#!/usr/bin/python
# -*- coding: utf8 -*-
#
# By Maximilian Krueger
# [maximilian.krueger@fau.de]

import sys
import time

sys.path.append('../')

import forgeosi

rhino1 = "http://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Diceros_bicornis.jpg/800px-Diceros_bicornis.jpg"
rhino2 = "https://upload.wikimedia.org/wikipedia/commons/b/b9/D%C3%BCrer_-_Rhinoceros.jpg"

vm1 = "ubuntu-lts-base"
vm2 = "ubuntu-lts-base"
vm3 = "windows-7-base"
vms = "xubuntu-lts-base"

def run(vm, output, verbose, run):
    """testcase 3

    Runs 3 virtual machines, using one as server and 2 as clients, interacting
    via networt. Uses vms defined above and not the parameter
    """
    vboxcfg = forgeosi.VboxConfig()
    vboxcfg.get_nat_network(run)
    vbox_c1 = forgeosi.Vbox(basename=vm1, clonename="testrun"+run+"client1")
    if verbose:
        print "vm1 created"
    time.sleep(10)
    vbox_c2 = forgeosi.Vbox(basename=vm2, clonename="testrun"+run+"client2")
    if verbose:
        print "vm2 created"
    time.sleep(10)
    vbox_c3 = forgeosi.Vbox(basename=vm3, clonename="testrun"+run+"client3")
    if verbose:
        print "vm1 created"
    time.sleep(10)
    vbox_s = forgeosi.Vbox(basename=vms, clonename="testrun"+run+"server")
    if verbose:
        print "vms created"
    time.sleep(10)
    p_c1 = vbox_c1.start(session_type=forgeosi.SessionType.gui, wait=False)
    p_c2 = vbox_c2.start(session_type=forgeosi.SessionType.gui, wait=False)
    vbox_s.start(session_type=forgeosi.SessionType.gui, wait=True)
    vbox_c3.start(session_type=forgeosi.SessionType.gui, wait=True)
    p_c1.wait_for_completion()
    p_c2.wait_for_completion()

    if verbose:
        print "all machines booted"
    time.sleep(60)

    vbox_c1.create_guest_session()
    vbox_c2.create_guest_session()
    vbox_c3.create_guest_session()
    vbox_s.create_guest_session()
    if verbose:
        print "all guest_sessions created"
    vbox_c1.add_to_nat_network(run)
    vbox_c2.add_to_nat_network(run)
    vbox_c3.add_to_nat_network(run)
    vbox_s.add_to_nat_network(run)
    vbox_s.start_network_trace(path=output+"/server.pcap")
    vbox_c1.start_network_trace(path=output+"/client1.pcap")
    time.sleep(60)
    ip_server = vbox_s.get_ip()
    ip_client1 = vbox_c1.get_ip()
    if verbose:
        print "ip server: "+str(ip_server)
        print "ip client1: "+str(ip_client1)

    vbox_s.os.make_dir("/home/default/server")

    if verbose:
        print "downloading files to server"
    time.sleep(10)
    vbox_s.os.download_file(rhino1, "/home/default/server/rhino1.jpg")
    time.sleep(10)
    vbox_s.os.download_file(rhino2, "/home/default/server/rhino2.jpg")
    time.sleep(10)
    #install ssh-server for using scp later
    vbox_c1.os.run_shell_cmd("""sudo apt-get install openssh-server
sleep_hack
12345
sleep_hack
y
""", gui=True)
    time.sleep(10)

    if verbose:
        print "starting webserver"
    vbox_s.os.serve_directory("~/server", port=8080)
    time.sleep(10)

    vbox_c1.os.open_browser(ip_server+":8080/rhino1.jpg")
    vbox_c2.os.open_browser(ip_server+":8080/rhino2.jpg")
    vbox_c3.os.open_browser("http://"+ip_server+":8080/rhino2.jpg",
                            method=forgeosi.RunMethod.run)
    if verbose:
        print "all webbrowsers opened"
    time.sleep(30)
    vbox_c1.os.make_dir("~/rhinopix")
    time.sleep(10)
    vbox_c1.os.download_file(ip_server+":8080/rhino1.jpg",
                             "~/rhinopix/rhino1.jpg")
    time.sleep(30)
    # client 2 gets one picture form client 1 via scp
    vbox_c2.os.run_shell_cmd(
"""cd
scp default@"""+ip_client1+""":~/rhinopix/rhino1.jpg .
sleep_hack
yes
sleep_hack
12345
""", gui=True)

    vbox_s.stop_network_trace()
    vbox_s.stop(confirm=forgeosi.StopConfirm.xfce)
    vbox_c1.stop_network_trace()
    vbox_c1.stop()
    vbox_c2.stop()
    vbox_c3.stop()

    if verbose:
        print "machines stopped"
    vbox_c1.log.write_xml_log(output+"/log_c1.xml")
    vbox_c2.log.write_xml_log(output+"/log_c2.xml")
    vbox_c3.log.write_xml_log(output+"/log_c3.xml")
    vbox_s.log.write_xml_log(output+"/log_s.xml")
    vbox_c1.export(path=output+"/disk_c1.img", raw=True)
    vbox_c2.export(path=output+"/disk_c2.img", raw=True)
    vbox_c3.export(path=output+"/disk_c3.img", raw=True)
    vbox_s.export(path=output+"/disk_s.img", raw=True)

    vbox_c1.cleanup_and_delete()
    vbox_c2.cleanup_and_delete()
    vbox_c3.cleanup_and_delete()
    vbox_s.cleanup_and_delete()

#!/usr/bin/env python2
import subprocess
import argparse
import random
import shutil
import string
import stat
import os

CHALS = [(1,"CHALLENGE_1"), (2,"CHALLENGE_2"), (3,"CHALLENGE_3")]
CHAL_PREFIX = "../challenge_binaries"
BASE_PREFIX = ".."
IMAGE_DIRNAME_FMT = "t%dc%d"
PORT_FMT = "5%s%d"
ADDRESS_FMT = "10.99.1%s.1"
LINE_FMT = 'adduser t%d --home /home/t%d --shell /usr/local/bin/firejail --disabled-password --gecos ""\necho -e "%s\\n%s" | passwd t%d\n\ncp t%d_instructions.txt /home/t%d/instructions.txt\n'
INSTRUCTIONS_FMT = '%s: nc %s %s\n'

DOCKERFILE_FMT = """
FROM ubuntu 
MAINTAINER Andrew Ruef
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update
RUN apt-get install -y netcat-traditional
ADD %s /CHALLENGE
ADD WRAPPER.sh /WRAPPER.sh
EXPOSE %s
CMD ["/WRAPPER.sh", "%s"]
"""

def buildimage(team, challenge):
#set up the directory
    challenge_id,challenge_name = challenge
    port = PORT_FMT % (str(team).zfill(3), challenge_id)
    address = ADDRESS_FMT % (str(team).zfill(2))
    dirname = IMAGE_DIRNAME_FMT % (team, challenge_id)
    os.mkdir(dirname)
    shutil.copyfile("%s/%s" % (CHAL_PREFIX, challenge_name), "%s/%s" % (dirname, challenge_name))
    shutil.copyfile("%s/%s" % (BASE_PREFIX, "WRAPPER.sh"), "%s/%s" % (dirname, "WRAPPER.sh"))
    st = os.stat("%s/%s" % (dirname, "WRAPPER.sh"))
    os.chmod("%s/%s" % (dirname, "WRAPPER.sh"), st.st_mode | stat.S_IEXEC)
    st = os.stat("%s/%s" % (dirname, challenge_name))
    os.chmod("%s/%s" % (dirname, challenge_name), st.st_mode | stat.S_IEXEC)
    df = open("%s/%s" % (dirname, "Dockerfile"), 'w')
    df.write(DOCKERFILE_FMT % (challenge_name, port, port))
    df.close()
#build with a call to docker
    subprocess.call(["docker", "build", "-t", dirname, dirname])
#write out the command to start an instance of this container 
    s = open("init.sh", 'a')
    s.write("\ndocker run -p %s:%s:%s/tcp --name %s_instance -t %s &" % (address, port, port, dirname, dirname))
    s.close()

    s = open("t%d_instructions.txt" % (team), 'a')
    s.write(INSTRUCTIONS_FMT % (challenge_name, address, port))
    s.close()

    s = open("users.sh", 'a')
    s.write("cp %s/%s /home/t%d/%s\n" % (CHAL_PREFIX, challenge_name, team, challenge_name))
    s.close()
    return

def main(args):
    team = int(args.team)
    address = ADDRESS_FMT % (str(team).zfill(2))
    s = open("iface.sh", 'a')
    s.write("\nbrctl addbr br%s\nifconfig br%s %s/24\n" % (str(team), str(team), address))
    s.close()
    pw = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
    s = open("users.sh", 'a')
    s.write(LINE_FMT % (team, team, pw, pw, team, team, team))
    s.close()
    s = open("users.txt", 'a')
    s.write("t%d : %s\n" % (team, pw))
    s.close()
    s = open("login_append", 'a')
    s.write("t%d:--noprofile --net=br%d\n" % (team, team))
    s.close()
    for c in CHALS:
        buildimage(team, c)
    return

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('team')
    args = p.parse_args()
    main(args)

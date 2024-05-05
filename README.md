**gbash - Gen-AI based linux shell**

Learning all the bash commands can sometimes be a pain for someone new. 
- Wouldn't it be nice if we could use Gemini to translate natural language into something linux would understand ?
- This project is a very tiny proof of concept
- It takes instructions in natural language and converts it into something which could be run on linux
- **Note** : This is really a _Proof-of-concept_. It will run commands Gemini tells it to, so please do not run on product infrastructure.

<pre>
To use this please set the environment variable API_KEY to your Gemini API key.
You can find your Gemini key at https://aistudio.google.com/app/apikey

Setup
   API_KEY='API KEY HERE'
   export API_KEY

- Once done you can do this to setup
   python3 gbash.py "Please count the total number of processes on this system"
</pre>

<pre>
$ python3 gbash.py "Please check and tell if the webserver on this server is operating correctly. "
========
FINAL_SCRIPT
#!/bin/bash
service apache2 status
========
● apache2.service - The Apache HTTP Server
     Loaded: loaded (/usr/lib/systemd/system/apache2.service; enabled; preset: enabled)
     Active: active (running) since Sun 2024-05-05 00:27:58 UTC; 36min ago
       Docs: https://httpd.apache.org/docs/2.4/
   Main PID: 4313 (apache2)
      Tasks: 55 (limit: 4687)
     Memory: 6.5M (peak: 6.9M)
        CPU: 246ms
     CGroup: /system.slice/apache2.service
             ├─4313 /usr/sbin/apache2 -k start
             ├─4316 /usr/sbin/apache2 -k start
             └─4317 /usr/sbin/apache2 -k start

May 05 00:27:58 desktop3.us-central1-a.c.m0nitor.internal systemd[1]: Starting apache2.service - The Apache HTTP Server...
May 05 00:27:58 desktop3.us-central1-a.c.m0nitor.internal systemd[1]: Started apache2.service - The Apache HTTP Server.
</pre>

<pre>
$ python3 gbash.py "please tell me how much disk and memory storage I have on this server."
========
FINAL_SCRIPT
#!/bin/bash
df -h
free -h
========
Filesystem      Size  Used Avail Use% Mounted on
/dev/root        19G  3.1G   16G  17% /
tmpfs           2.0G     0  2.0G   0% /dev/shm
tmpfs           783M  964K  782M   1% /run
tmpfs           5.0M     0  5.0M   0% /run/lock
efivarfs         56K   24K   27K  48% /sys/firmware/efi/efivars
/dev/sda16      881M   61M  759M   8% /boot
/dev/sda15      105M  6.1M   99M   6% /boot/efi
tmpfs           392M   12K  392M   1% /run/user/1001
               total        used        free      shared  buff/cache   available
Mem:           3.8Gi       453Mi       3.3Gi       1.3Mi       303Mi       3.4Gi
Swap:             0B          0B          0B
</pre>

<pre>
$ python3 gbash.py "find the largest log file by size under /var/log directory"
the largest file under /var/log directory is /var/log/lastlog
</pre>

<pre>
$ python3 gbash.py "who were the last 10 unique users on this syetm ?"
========
FINAL_SCRIPT
#!/bin/bash
last | cut -d" " -f1 | sort -u | tail -10
========

reboot
royans
wtmp
</pre>

<pre>
$ python3 gbash.py "show all the tcp6 ports listenning on this server"
========
FINAL_SCRIPT
#!/bin/bash
netstat -6an | grep LISTEN
========
tcp6       0      0 :::22                   :::*                    LISTEN     
tcp6       0      0 :::80                   :::*                    LISTEN   
</pre>





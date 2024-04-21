**gbash - Gen-AI based linux shell**

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
$ python3 gbash.py "find the largest file under /var/log directory"
the largest file under /var/log directory is /var/log/lastlog
</pre>

<pre>
python3 gbash.py "who were the last 10 unique users on this syetm ?"
reboot
royans
wtmp
</pre>

<pre>
$ python3 gbash.py "show all the tcp6 ports listenning on this server"
(Not all processes could be identified, non-owned process info
 will not be shown, you would have to be root to see it all.)
tcp6       0      0 :::80                   :::*                    LISTEN      -                   
tcp6       0      0 :::22                   :::*                    LISTEN      -                   
tcp6       0      0 :::443                  :::*                    LISTEN      -                   
tcp6       0      0 :::631                  :::*                    LISTEN      -  
</pre>





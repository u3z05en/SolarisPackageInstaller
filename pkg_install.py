#!/usr/bin/env python
"""
Interactivly installs all Solaris packages in a directory with -local endings. Will GUNZIP .gz files and rezip afterwards. Provides uninstall support on subsequent runs.
Copyright (c) 2012 u3z05en
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

-> v1.0 - May-18-2012 - u3z05en - Script created.
"""

import sys, os, logging, subprocess, glob, socket, string, re

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_NAME = os.path.basename(os.path.realpath(__file__))
PID_FILE = os.path.join(BASE_DIR, '.pid')
PID_NUM = os.getpid()
LOG_FILE = sys.argv[0] + '.log'

logging.basicConfig(filename = LOG_FILE, format = '%(asctime)s,%(name)s,%(levelname)s,%(message)s', datefmt = '%d/%m/%Y,%H:%M:%S', level = logging.DEBUG)

def log_this(log_string, severity):
    """Logs a string to the logging destinations"""
    logging.info(log_string)
    print log_string

def leave_now(code):
    """EXIT : Due to error"""
    os.remove(PID_FILE)
    msg = BASE_NAME + ' Exited (' + str(code) + ')';log_this(msg.center(45, '-'), 'info')
    sys.exit(code)

def main():
    """Launch primary logic"""
    #INITIATE
    msg = BASE_NAME + ' Initiated';log_this(msg.center(45, '-'), 'info')
    log_this('Platform: ' + sys.platform + ' -> Host: ' + socket.gethostname() + ' ' + os.uname()[3] + ' -> Python: ' + sys.version, 'info')

    #PID PROCESSING
    if os.path.isfile(PID_FILE) == True:
        old_instance = open(PID_FILE).readlines()[0].strip()
        os.remove(PID_FILE)
        if int(old_instance) != PID_NUM:
            try:
                os.kill(int(old_instance), 9)
                log_this('Old PID file found and killed. Old PID: ' + old_instance + ' Cur PID: ' + str(PID_NUM), 'warn')
            except:
                log_this('Old PID file found, process was not running. Old PID: ' + old_instance + ' Cur PID: ' + str(PID_NUM), 'warn')
        else:
            log_this('PID file contains current PID, something is very wrong!', 'crit')
            leave_now(1)
    pid_gate = open(PID_FILE, 'wb')
    pid_gate.write(str(PID_NUM))
    pid_gate.close()

    #UNINSTALL FILE
    uninstall_file = sys.argv[0] + '.uninstall'
    if os.path.isfile(uninstall_file) == True:
        log_this('Previous uninstall file found.', 'info')
        del msg; msg = 'An uninstall file was found, (c)ontinue, (e)xit or (u)ninstall: '
        Continue = raw_input(msg)
        while Continue != 'c' and Continue != 'C':
            if Continue == 'e' or Continue == 'E':
                leave_now(0)
            elif Continue == 'u' or Continue == 'U':
                for package_name in open(uninstall_file):
                    subprocess.call(['pkgrm', package_name.strip()])
                log_this('All Uninstall Packages Processed', 'info')
                leave_now(0)
            else:
                Continue = raw_input(msg)
    if os.path.isfile(uninstall_file) == True:
        os.remove(uninstall_file)
    uninstall_file_gate = open(uninstall_file, 'ab+')

    #GUNZIP ALL .GZ FILES
    for zipped_package in glob.glob(BASE_DIR + '/*.gz'):
        subprocess.call(['gunzip', zipped_package])
    log_this('All Packages Unzipped', 'info')

    #INSTALL PACKAGES
    for package in glob.glob(BASE_DIR + '/*-local'):
        subprocess.call(['pkgadd', '-d', package])
        package_info = subprocess.Popen(['pkginfo', '-d', package], stdout = subprocess.PIPE, stderr = subprocess.STDOUT).communicate()[0]
        package_descriptor = string.join(re.findall(r' .*? ', string.join(re.findall(r'^.*? .*? ', package_info)))).strip()
        if subprocess.call('pkginfo |grep ' + package_descriptor, shell = True) == 0:
            uninstall_file_gate.write(package_descriptor + '\n')
            log_this('-- ' + package_descriptor + ' is installed', 'info')
        else:
            log_this('-- ' + package_descriptor + ' is NOT installed', 'info')
    log_this('All Packages Processed', 'info')

    #GZIP ALL FILES AGAIN
    for unzipped_package in glob.glob(BASE_DIR + '/*-local'):
        subprocess.call(['gzip', unzipped_package])
    log_this('All Packages Rezipped', 'info')

    uninstall_file_gate.close()
    leave_now(0)

if __name__ == '__main__':
    main()

import sys
import psutil
import platform
import time
import json
import os
import socket

uname=platform.uname()
m = psutil.virtual_memory()
sys_name = uname[0]
host_name = uname[1]
release = uname[2]
cpu_count = psutil.cpu_count()
mem_size = m.total
with open('/proc/cpuinfo') as f:
    for line in f:
        if line.startswith('model name'):
            cpu_model = line.split(':')[1].strip().split()
            cpu_model = cpu_model[0] + ' ' + cpu_model[2] + ' ' + cpu_model[-1]
            break

def get_readable(size):
    unit = ('B', 'KB', 'MB', 'GB', 'TB', 'PB')
    i = 0
    while i < len(unit) and size > 1024:
        size /= 1024
        i += 1
    return '%.2f %s' % (size, unit[i])


def get_readable_time(seconds):
    unit = ('s', 'min', 'h', 'day')
    val =  (60, 60, 24)
    k = []
    i = 0
    while i < len(val) and seconds >= val[i]:
        k.append(seconds%val[i])
        seconds //= val[i]
        i += 1
    if seconds > 0:
        k.append(seconds)
    if not k: return '0'
    r = ''
    for i in range(len(k)):
        if k[i] > 0:
            r = '%d %s,' % (k[i], unit[i]) + r 
    return r


def get_profile():
    return '%s %s,%s (%d core), Mem size %s' % (sys_name, release, cpu_model, cpu_count, get_readable(mem_size))


def get_status():
    return 'MemFree %d, MemUsed %.2f %%, Cup %f %%, Up Time %s' % (m.free, m.used/mem_size*100, psutil.cpu_percent(), get_readable_time(time.time() - psutil.boot_time()))


def check_ps(tasks):
    td = {}
    r = []
    rs = ''
    for i, t in enumerate(tasks):
        td[t[1]] = i
    for pid in psutil.pids():
        try:
            p = psutil.Process(pid)
        except psutil.NoSuchProcess:
            continue
        name = p.name()
        cmdline = ' '.join(p.cmdline())
        if cmdline in td and tasks[td[cmdline]][0] == p.cwd():
                idx = td[cmdline]
                #r[idx].append({'pid': pid, 'name': name, 'cwd': p.cwd(), 'cmdline': cmdline, 'uptime': get_readable_time(time.time() - p.create_time())})
                r.append({'pid': pid, 'name': name, 'cwd': p.cwd(), 'cmdline': cmdline, 'uptime': get_readable_time(time.time() - p.create_time())})
                if len(rs) != 0: rs += '\r'
                rs += f'{pid} {name} {get_readable_time(time.time() - p.create_time())}\t{p.cwd()}\t{cmdline}'
    return rs
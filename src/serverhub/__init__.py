from . import sysinfo
import socket
import getopt
import time
import sys
import ssl
import os


task_list = []


def get_line(s):
    buf = b''
    while True:
        ch = s.recv(1)
        if not ch or ch == b'\n':
            return buf.decode()
        buf += ch


def scan_process():
    pid = os.listdir('/proc/')
    for p in pid:
        if p.isnumeric():
            with open(os.path.join('/proc', p, 'cmdline')) as f:
                cmd = f.read()
            print(p, cmd)


base_dir = os.path.dirname(os.path.realpath(__file__))


def start_listen(port, cert, pem, ca):
    # 生成SSL上下文
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    # 加载服务器所用证书和私钥
    context.load_cert_chain(cert, pem)
    context.load_verify_locations(ca)
    context.verify_mode = ssl.CERT_REQUIRED
    # 监听端口
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        sock.bind(('0.0.0.0', port))
        sock.listen(5)
        print ('start listen...')
        with context.wrap_socket(sock, server_side=True) as ssock:
            while True:
                client_socket, addr = ssock.accept()
                print(f"client {addr}")
                request = get_line(client_socket)
                print(request)
                if request == 'get profile':
                    msg = sysinfo.get_profile()
                    client_socket.send(msg.encode())
                elif request == 'get state':
                    msg = sysinfo.get_status()
                    client_socket.send(msg.encode())
                elif request == 'get process':
                    request = get_line(client_socket)
                    print(request)
                    task_list = []
                    for x in request.split('\r'):
                        x = x.split('\t')
                        if x[0].endswith('/'): 
                            x[0] = x[0][:-1]
                        task_list.append([x[0], x[1]])
                    msg = sysinfo.check_ps(task_list)
                    if msg:
                        client_socket.send(msg.encode())
                client_socket.close()


def make_root_cert(path, name, days=365):
    key = os.path.join(path, '%s.pem' % name)
    cert = os.path.join(path, '%s.crt' % name)
    if 0 == os.system(f'openssl req -newkey rsa:1024 -nodes -keyout {key} -x509 -subj "/CN={name}" -days {days} -out {cert}'):
        print("成功！")
        print("私钥： ", key, "\n证书: ", cert)
    else:
        print("失败！")

def make_signed_cert(path, name, ca, cap, days=365):
    key = os.path.join(path, '%s.pem' % name)
    key_java = os.path.join(path, '%s.java.pem' % name)
    cert = os.path.join(path, '%s.crt' % name)
    csr = os.path.join(path, str(time.time()) + '.csr')
    r = os.system(f'openssl genrsa -out {key} 1024')
    if r != 0:
        print("生成私钥失败！")
        return
    
    r = os.system(f'openssl req -new -key {key} -out {csr} -subj "/CN={name}"')
    if r != 0:
        print("生成 csr 失败！")
        os.remove(key)
        print("删除 {key}")
        return
    
    r = os.system(f'openssl x509  -req -days {days} -in {csr} -CA {ca} -CAkey {cap}  -CAcreateserial -out {cert}')
    
    os.remove(csr)
    print(f"删除 {csr}")
    if r != 0:
        print('签名证书失败！')
        os.remove(key)
        print(f"删除 {key}")
    print(f'openssl pkcs8 -topk8 -inform PEM -in {cert} -outform PEM -nocrypt > {key_java}')
    r = os.system(f'openssl pkcs8 -topk8 -inform PEM -in {key} -outform PEM -nocrypt > {key_java}')
    if r != 0:
        print('证书格式转换失败！')
    else:
        print('成功！')
    
def show_useage():
    print ('Usage: serverhub -r|-s|-c  [-p <port>] [-d <days>] [-t <target path>]')
    print ('    -s                start server')
    print ('    -p <port>         default is 12345')
    print ('    -t <target dir>   ')
    print ('    -r                make a root cert')
    print ('    -d <days>         default is 365')
    print ('    -c <cert path>    make a cert for client, or used with -s to set cert path')
    
    print ('Examples:')
    print ('    serverhub -r')
    print ('         make a root cert and pem to ~/.serverhub/, you can input a name for it by stdin')
    print ('    serverhub -c ~/.serverhub/ca')
    print ('         make a cert signed with ~/.serverhub/ca.cert')
    print ('    serverhub -s -p 8000 -c ~/.serverhub/server')
    print ('         start server at 0.0.0.0:8000, use ~/.serverhub/server.cert and ~/.serverhub/server.pem')
    


def main():
    home = os.path.expanduser('~')
    try:
        opts, _ = getopt.getopt(sys.argv[1:],"rd:p:c:k:st:",[])
    except getopt.GetoptError as e:
        print(e)
        show_useage()
        sys.exit(2)
    fr = 0
    root_cert = 'ca'
    path = os.path.join(home, '.serverhub')
    fserver = 0
    fcert = 0
    port = 12345
    days = 365
    cert = os.path.join(path, 'server')
    for opt, arg in opts:
        if opt == '-r':
            fr = 1
        if opt == '-s':
            fserver = 1
        if opt == '-c':
            fcert = 1
            root_cert = arg
        if opt == '-p':
            port = int(arg)
        if opt == '-t':
            path = arg
        if opt == '-d':
            days = int(arg)
    if fserver:
        start_listen(port, root_cert + '.crt', root_cert + '.pem', os.path.join(path, 'ca.crt'))
        exit()
    if fcert:
        name = input('input cert name(default client):')
        if not name: name = 'client'
        print('path:', path)
        if not os.path.exists(path):
            os.mkdir(path)
        make_signed_cert(path, name, root_cert + '.crt', root_cert + '.pem', days)
        exit()
    if fr:
        name = input('input cert name(default ca):')
        if not name: name = 'ca'
        print('path:', path)
        if not os.path.exists(path):
            os.mkdir(path)
        make_root_cert(path, name, days)
        exit()
    show_useage()


main()
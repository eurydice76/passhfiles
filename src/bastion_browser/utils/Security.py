import io
import logging

import paramiko

def checkAndGetSSHKey(keyfile,keytype,password):
    """
    """

    if keytype == 'RSA':
        paramikoKeyModule = paramiko.RSAKey
    elif keytype == 'ECDSA':
        paramikoKeyModule = paramiko.ECDSAKey
    elif keytype == 'ED25519':
        paramikoKeyModule = paramiko.Ed25519Key
    else:
        logging.error('Unknown key type')
        return False, None

    try:
        f = open(keyfile,'r')
        s = f.read()
        f.close()
        keyfile = io.StringIO(s)
        key = paramikoKeyModule.from_private_key(keyfile,password=password)
    except Exception as e:
        logging.error(str(e))
        return (False, None)
    else:
        return (True,key)

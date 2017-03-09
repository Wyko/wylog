'''
Created on Mar 4, 2017

@author: Wyko
'''

from datetime import datetime
import os, traceback, time, sys


# Variables for logging
CRITICAL = 1
C = 1
ALERT = 2
A = 2
HIGH = 3
H = 3
NORMAL = 4
N = 4

# Debuging levels
INFORMATIONAL = 5
I = 5
DEBUG = 6
D = 6

# Stores current verbosity level
VERBOSITY= 6


# Where the log is stored
LOG_PATH= os.path.dirname(__file__) + '/runtime/'

        
def log(msg, **kwargs):
    """Writes a message to the log.
    
    Args:
        msg (string): The message to write.
        
    Optional Args:
        ip (string): The IP address.
        proc (string): The process which caused the log entry
        log_path (string): Where to save the file
        print_out (Boolean): If True, copies the message to console
        v (Integer): Verbosity level. Logs with verbosity above the global 
            verbosity level will not be printed out.  
            v= 1: Critical alerts
            v= 2: Non-critical alerts
            v= 3: High level info
            v= 4: Common info
            v= 5-6: Debug level info
            
        error (Exception): 
        
    Returns:
        Boolean: True if write was successful, False otherwise.
    """ 
    
    v = kwargs.get('v', 4)
    proc= kwargs.get('proc', '')
    ip= kwargs.get('ip', '') 
    error=  kwargs.get('error')
    print_out= kwargs.get('print_out', True)
    log_path = kwargs.get('log_path')
    process_debug_messages= kwargs.get('process_debug_messages', True)
    
    # Skip debug messages (unless turned on)
    if (v >= 5) and (process_debug_messages is False): return False 
    
    if log_path is None: log_path= LOG_PATH
    
    msg= str(msg)
    
    time_format = '%Y-%m-%d %H:%M:%S'

    # Set the prefix for the log entry
    if v >=3: info_str = '#' + str(v)
    if v ==2: info_str = '? '
    if v ==1: info_str = '! '

    msg = info_str + ' ' + msg
    
    try:
        output = '{_proc:20}, {_msg}, {_time}, {_ip:15}, {_error}'.format(
                    _time= datetime.now().strftime(time_format),
                    _proc= str(proc),
                    _msg = msg.replace(',', ';'),
                    _ip = str(ip),
                    _error = str(error)
                    )
    except Exception as e:
        pass
    
#     # Debugging: Filter specific messages
#     if 'main.' in proc:  
    # Print the message to console            
    try: 
        if v <=  VERBOSITY and print_out: print('{:<35.35}: {}'.format(proc, msg))
    except Exception as e:
        pass
    
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    
    # Open the error log
    f = open('{}log.txt'.format(log_path), 'a')
    
    if f and not f.closed:
        f.write(output + '\n')
        f.close()
        return True
    
    else: return False
        

class log_snip(object):
    def __init__(self, proc):
        self.proc = proc
        
    def __enter__(self):
        log('Entering snippet [{}]'.format(self.proc),
            proc= self.proc, v= D)
        self.start = time.time()
        
    def __exit__(self,ty,val,tb):
        end = time.time()
        
        if ty is None:
            log('Finished snippet [{}] after [{:.3f}] without error'.format(
                self.proc, end-self.start), proc= self.proc, v= D)
            
        else:
            log('Finished snippet [{}] after [{:.3f}] seconds with [{}] error. Traceback: [{}]'.format(
                self.proc, end-self.start, ty.__name__, traceback.format_tb(tb)),
                proc= self.proc, v= D)

def logf(f, **kwargs):
    parent= kwargs.get('parent', '__________')
    
    # Take a decorated method and log it.
    def wrapped_f(*args, **kwargs):
        log('Starting method [{}]'.format(f.__name__),
            proc= '{0}.{1}'.format(parent, f.__name__),
            v= DEBUG)
        start = time.time()
        
        # Run the decorated function
        try: result= f(*args, **kwargs)
        
        # On exception, log it and re-raise
        except Exception as e:
            tb = sys.exc_info()[2]
            log('Finished method [{}] after [{:.3f}] seconds with [{}] Error: [{}] Traceback: [{}]'.format(
                f.__name__, time.time()- start, type(e).__name__, str(e), traceback.format_tb(tb)),
                proc= '{0}.{1}'.format(parent, f.__name__),
                v= ALERT)
            raise
        else:
            log('Finished method [{}] after [{:.3f}] seconds'.format(
                f.__name__, time.time()- start),
                proc= '{0}.{1}'.format(parent, f.__name__),
                v= DEBUG)
            return result
    return wrapped_f
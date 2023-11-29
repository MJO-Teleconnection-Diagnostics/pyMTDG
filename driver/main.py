from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
import threading
import time
import yaml

def worker_thread(thread_num,path):
    print(f"Thread {thread_num} started")
    try:
        with open(path) as f:
            exec(f.read())
        print(f"Thread {thread_num} finished")
    except Exception as e:
        print('--------error----------')
        print()
        print(e)
        print()
        print('--------error----------')
    #ret = subprocess.Popen(command,  shell=True)
    #ret.communicate()
    

if __name__ == "__main__":
    threads = []
    config_file='config.yml'
    with open(config_file,'r') as file:
        try:
            dictionary = yaml.safe_load(file)
            selected = dictionary['selected']
            
        except yaml.YAMLError as e:
            print(e)
    diagnostics_paths = ["../T2m_composites/t2m_composites.py", "../T2m_composites/t2m_composites.py", "../T2m_composites/t2m_composites.py",
                             "../T2m_composites/t2m_composites.py",
                             "../T2m_composites/t2m_composites.py",
                             "../T2m_composites/t2m_composites.py",
                             "../T2m_composites/t2m_composites.py",
                             "../T2m_composites/t2m_composites.py",
                             "../T2m_composites/t2m_composites.py",
                             "../T2m_composites/t2m_composites.py",
                             "../T2m_composites/t2m_composites.py",
                             "../T2m_composites/t2m_composites.py"]

    try:
        # Create and start child threads
        for i in selected:
            thread = threading.Thread(target=worker_thread, args=(i,diagnostics_paths[i],))
            thread.start()
            time.sleep(5)
            threads.append(thread)

        # Wait for all child threads to complete
        for thread in threads:
            thread.join()

        # All child threads have completed
        print('All done')
    except Exception as e:
        print('--------Main error----------')
        print()
        print(e)
        print()
        print('--------Main error----------')

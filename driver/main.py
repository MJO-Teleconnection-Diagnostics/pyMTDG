from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
import threading
import time
import yaml
        
'''class Worker(QRunnable,QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    def __init__(self, path, selected):
        super().__init__()
        self.path = path
        self.selected = selected
        
    def run(self):
        """Long-running task."""
        try:
            print('Hey')
            with open(self.path) as f:
                exec(f.read())
            ret = subprocess.Popen(command,  shell=True)
            ret.communicate()

        except Exception as e:
            print(f"Error in worker: {e}")
        finally:
            print('successful')
            self.finished.emit()
            
def main_function(selected):
    threadpool = QThreadPool()
    threads=[]
    for i in selected:
        worker = Worker(diagnostics_paths[i],selected)
        #self.worker.started.connect(self.worker.run)
        worker.finished.connect(isFinished)
        #self.worker.finished.connect(self.thread.quit)
        worker.finished.connect(worker.deleteLater)
        #self.worker.finished.connect(self.thread.deleteLater)
        #self.worker.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        threadpool.start(worker)
        threads.append(worker)'''



def worker_thread(thread_num,path):
    print(f"Thread {thread_num} started")
    print('Hey')
    with open(path) as f:
        exec(f.read())
    #ret = subprocess.Popen(command,  shell=True)
    #ret.communicate()
    print(f"Thread {thread_num} finished")

if __name__ == "__main__":
    threads = []
    config_file='config.yml'
    with open(config_file,'r') as file:
        try:
            dictionary = yaml.safe_load(file)
            selected = dictionary['selected']
        except yaml.YAMLError as e:
            print(e)

    selected=[1,2]
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


    # Create and start child threads
    for i in selected:
        thread = threading.Thread(target=worker_thread, args=(i,diagnostics_paths[i],))
        thread.start()
        threads.append(thread)

    # Wait for all child threads to complete
    for thread in threads:
        thread.join()

    # All child threads have completed
    print('All done')

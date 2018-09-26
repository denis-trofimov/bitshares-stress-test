import multiprocessing

num_procs = 4
def do_work(message):
  print ("work",message ,"completed")

def worker():
  for item in iter( q.get, None ):
    do_work(item)
    q.task_done()
  q.task_done()

q = multiprocessing.JoinableQueue()
procs = []
for i in range(num_procs):
  procs.append( multiprocessing.Process(target=worker) )
  procs[-1].daemon = True
  procs[-1].start()

source = ['hi','there','how','are','you','doing']
for item in source:
  q.put(item)

q.join()

for p in procs:
  q.put( None )

q.join()

for p in procs:
  p.join()

print ("Finished everything....")
print ("num active children:", multiprocessing.active_children())

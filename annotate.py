__version__ = '0.1'
#!/usr/local/bin/python3
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import sys
from prettytable import PrettyTable

config.load_kube_config()

def print_help():
    print('I need the namespace(s) as an argument')

if len(sys.argv) <= 1:
    print (f'bad arguments: {str(sys.argv[1:])}')
    print_help()
    exit(1)

namespaces = sys.argv[1:]
table =  PrettyTable(['Namespace', 'Pod','Volume-Name','PVC'])

v1 = client.CoreV1Api()
print ('Pods with Persistant Volume Cliams to be annotated:', end = '')
for n in namespaces:
    print ("")
    ret = v1.list_namespaced_pod(n,watch=False)
    for i in ret.items:
        for v in i.spec.volumes:
            if v.persistent_volume_claim:
                table.add_row([n,i.metadata.name,v.name,v.persistent_volume_claim.claim_name])

print (table)
confirm = input('proceed?[Y/n]:')

if confirm != 'Y':
    exit(0)

for p in table:
    p.border=False
    p.header=False
    pod = p.get_string(fields=["Pod"]).strip()
    ns = p.get_string(fields=["Namespace"]).strip()
    pvc = p.get_string(fields=["PVC"]).strip()
    volume = p.get_string(fields=["Volume-Name"]).strip()
    body = {"metadata": {"annotations": {"backup.velero.io/backup-volumes": volume }}}
    print(f'Annotating {pod} ', end = '')
    try:
        v1.patch_namespaced_pod(pod,ns,body)
        print (' Done')
    except ApiException as e:
        print (" AAHH something went wrong!")
        exit(1)
exit (0)
# todo: if a pvc have more than 1 pod, then the las for p int table should handle this.

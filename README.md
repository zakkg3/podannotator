# podannotator
Annotates all volumes (with a PVC), in all pods, in a given list of namepsaces to be backed up by velero/restic.

Namespace 1
        -- Pod 1
                -- Volume 1 (N1P1V1)
                -- Volume 2 (N1P1V2)
        -- Pod 2
                -- Volume 1 (N1P2V1)
                -- Volume 2 (N1P2V2)
Namespace 2
        -- Etc.

Note: All pods within a given namespace will be backed up, if they have a PVC.  (Ignoring PVC's would include secrets.)  There is currently no requirement to be able to exclude volumes from backups.  See @todo in class if this is ever in scope.

# Usage  

python3 annotator.py namespace1,namespace2


# What it does


## Initial position display

Initially, a table will be created showing the start position of all of the volumes within all of the pods within the provided namespace(s).

For example, if I issued the following command: python3 annotate.py raffia,logstash,vault,nagios

+-----------+--------------------------+---------------------------+---------------------------+-------------+
| Namespace |           Pod            |        Volume-Name        |            PVC            | Annotations |
+-----------+--------------------------+---------------------------+---------------------------+-------------+
|  logstash | logstash-ccc4d98c9-k89sd | pipeline-logstashshared-0 | pipeline-logstashshared-0 |     None    |
|  logstash | logstash-ccc4d98c9-k89sd |      logstash-1-data      |      logstash-1-data      |     None    |
|  logstash | logstash-ccc4d98c9-k89sd |     logstash-1-config     |     logstash-1-config     |     None    |
|  logstash |     logstashshared-0     |          pipeline         | pipeline-logstashshared-0 |     None    |
|   nagios  | nagios-7f6f997894-dxt5n  |       nagios-configs      |       nagios-configs      |     None    |
|   nagios  | nagios-7f6f997894-dxt5n  |       nagios-servers      |       nagios-servers      |     None    |
|   nagios  | nagios-7f6f997894-dxt5n  |    nagios-last-servers    |    nagios-last-servers    |     None    |
+-----------+--------------------------+---------------------------+---------------------------+-------------+


## Pod Map object

A "pod map" will then be generated based on the kubernetes API call which returns all of the objects within the specified NS.  

A pod_map is a *JSON-like* object which is in the following format:

{'logstash': {'logstash-ccc4d98c9-k89sd': ['pipeline-logstashshared-0', 'logstash-1-data', 'logstash-1-config'], 'logstashshared-0': ['pipeline']}, 'nagios': {'nagios-7f6f997894-dxt5n': ['nagios-configs', 'nagios-servers', 'nagios-last-servers']}}

The reason for re-mapping the return from the API call is that this makes life much simpler later when we want to tie all volumes to their respective parent pods, otherwise we need to keep looping in and out of the API call repeatedly, which is more requests, and all takes additional time.  If this needs to be extended to include more data, this can be done by extending the get_pod_map method within the Annotate class.


## Human readable preview

A human-readable preview will be shown next.  This is a legacy from a prompt that was shown (but this would cause issues with pipelining the script) so has been removed for now (Annotate.py line 46-48).  It could be added back in later if required, but for now, it was decided to leave the human-readable list in place for simpler review during pipelining.


## Final position display

+-----------+--------------------------+---------------------------+---------------------------+----------------------------------------------------------------------------------------------------+
| Namespace |           Pod            |        Volume-Name        |            PVC            |                                            Annotations                                             |
+-----------+--------------------------+---------------------------+---------------------------+----------------------------------------------------------------------------------------------------+
|  logstash | logstash-ccc4d98c9-k89sd | pipeline-logstashshared-0 | pipeline-logstashshared-0 | {'backup.velero.io/backup-volumes': 'pipeline-logstashshared-0,logstash-1-data,logstash-1-config'} |
|  logstash | logstash-ccc4d98c9-k89sd |      logstash-1-data      |      logstash-1-data      | {'backup.velero.io/backup-volumes': 'pipeline-logstashshared-0,logstash-1-data,logstash-1-config'} |
|  logstash | logstash-ccc4d98c9-k89sd |     logstash-1-config     |     logstash-1-config     | {'backup.velero.io/backup-volumes': 'pipeline-logstashshared-0,logstash-1-data,logstash-1-config'} |
|  logstash |     logstashshared-0     |          pipeline         | pipeline-logstashshared-0 |                          {'backup.velero.io/backup-volumes': 'pipeline'}                           |
|   nagios  | nagios-7f6f997894-dxt5n  |       nagios-configs      |       nagios-configs      |      {'backup.velero.io/backup-volumes': 'nagios-configs,nagios-servers,nagios-last-servers'}      |
|   nagios  | nagios-7f6f997894-dxt5n  |       nagios-servers      |       nagios-servers      |      {'backup.velero.io/backup-volumes': 'nagios-configs,nagios-servers,nagios-last-servers'}      |
|   nagios  | nagios-7f6f997894-dxt5n  |    nagios-last-servers    |    nagios-last-servers    |      {'backup.velero.io/backup-volumes': 'nagios-configs,nagios-servers,nagios-last-servers'}      |
+-----------+--------------------------+---------------------------+---------------------------+----------------------------------------------------------------------------------------------------+

It will annotate all the pods (for the provided namespace(s)) with persist volume claims with the annotation: `backup.velero.io/backup-volumes: volume(s)-name-to-backup`

So now you can backup the namespace with velero/restic and this pvc will be backed up as well. :)


# Linear output:

For the above example, during execution, you would also see the data shown below to highlight what has been annotated:

```
Annotating namespace: logstash
Pod [logstash-ccc4d98c9-k89sd] done. Added the following volumes for backup: pipeline-logstashshared-0,logstash-1-data,logstash-1-config
Pod [logstashshared-0] done. Added the following volumes for backup: pipeline

Annotating namespace: nagios
Pod [nagios-7f6f997894-dxt5n] done. Added the following volumes for backup: nagios-configs,nagios-servers,nagios-last-servers
```
# podannotator
Annotate pods with PVC in a given list of namepsaces to be backed up by velero/restic


# Usage  

        annotator namespace1 namespace2


# what it does?

It will annotate all the pods with persist volume claims with the anotation: `backup.velero.io/backup-volumes: volume-name-to-backup`
So now you can backup the namespace with velero/restic and this pvc will be backed up aswell. :)


# Output:


```
python3 annotate.py gitlab
Pods with Persistant Volume Cliams to be annotated:
+-----------+------------------------------------+-------------+---------------------------+
| Namespace |                Pod                 | Volume-Name |            PVC            |
+-----------+------------------------------------+-------------+---------------------------+
|   gitlab  |          gitlab-gitaly-0           |  repo-data  | repo-data-gitlab-gitaly-0 |
|   gitlab  |   gitlab-minio-75567fcbb6-sxtkd    |    export   |        gitlab-minio       |
|   gitlab  | gitlab-postgresql-66d8d9574b-s7wrc |     data    |     gitlab-postgresql     |
|   gitlab  |   gitlab-redis-7668c4d476-c94rb    | gitlab-data |        gitlab-redis       |
+-----------+------------------------------------+-------------+---------------------------+
proceed?[Y/n]:
Annotating gitlab-gitaly-0  Done
Annotating gitlab-minio-75567fcbb6-sxtkd  Done
Annotating gitlab-postgresql-66d8d9574b-s7wrc  Done
Annotating gitlab-redis-7668c4d476-c94rb  Done
```

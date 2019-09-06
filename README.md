# podannotator
Annotate pods with PVC in a given list of namepsaces to be backed up by velero/restic


# Usage  

        annotator namespace1 namespace2


# what it does?

It will annotate all the pods with persist volume claims with the anotation: `backup.velero.io/backup-volumes: volume-name-to-backup`
So now you can backup the namespace with velero/restic and this pvc will be backed up aswell. :)

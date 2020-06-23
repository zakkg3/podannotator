__version__ = '0.1'
#!/usr/local/bin/python3
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import sys
from prettytable import PrettyTable

config.load_kube_config()

class Annotate:
    # @todo: include a mechanism to exclude volumes from automatic annotation.  We can do this by passing a json object in the format of our pod_map
    # @todo: incluce a parameter to allow the stripping of previous included annotations

    # entrypoint method for annotations
    def main(self):
        if len(sys.argv) <= 1:
            print(f'bad arguments: {str(sys.argv[1:])}')
            self.print_help()
            exit(1)

        # we have to split this since arg1 is actually a string that looks like a list!
        # @todo: We want to replace this with a proper library which allows handling of user arguments in an elegant way
        # @todo: this will allow us to specify things like --dryrun and not do anything in case we want to run it manually and inspect the pod_map object
        if len(sys.argv) <= 2:
            self.args = sys.argv[0]
            print(str(self.args))
            self.namespaces = list(sys.argv[1].split(","))

        # print a table to show what annotations each pod starts with
        print("\nStarting position of pods and volumes is as per below (input)")
        start_table = self.build_table()
        print(start_table)

        # build an object which contains all of our data in a format we can actually use
        self.pod_map = self.get_pod_map()
        print("\n--------------------------------------------------------------------------------------------------------------------------------------------------")
        print("Pod map built:")
        print("--------------------------------------------------------------------------------------------------------------------------------------------------")
        print(str(self.pod_map))
        print("--------------------------------------------------------------------------------------------------------------------------------------------------\n")

        # show the user a preview of what they're about to do @todo: add an option to disable this
        preview = self.get_preview()
        print("\nCompleting this action would add the following annotations to namespaces as per the preview below: \n\n" + str(preview))

        prompt for annotation confirmation
        confirm = input('proceed?[Y/n]:')
        if confirm != 'Y':
        exit(0)

        self.annotate_pods()  # this is where the magic happens

        # generate an output table
        print("\nEnd position of pods and volumes is as per below (output)")
        end_table = self.build_table()
        print(end_table)
        exit(0)

    # build a json object which maps out the namespaces passed as args, the pods they contain, and the volumes within the pods.
    # @return pod_map
    def get_pod_map(self):

        pod_map = dict()

        for namespace in self.namespaces:  # loop through our namespace list and create an inner object per namespace specified, handle multiples
            # print("namespace: " + namespace) # debug comment
            pod_map[namespace] = {}
            v1 = client.CoreV1Api()  # we want a new instance per namespace
            ret = v1.list_namespaced_pod(namespace, watch=False)  # go get it

            for item in ret.items:  # for each entry (pod in the namespace object)
                pod_map[namespace][item.metadata.name] = []  # add the pod(s) to the object
                # print("item: " + str(item)) # this contains everything about the item

                for volume in item.spec.volumes:  # get all our volumes for this pod
                    if volume.persistent_volume_claim:
                        pod_map[namespace][item.metadata.name].append(volume.name)  # add any volumes to our pod object
                        # print("volume.name: " + str(volume.name))  # debug comment

        return pod_map

    # build a pretty table to allow us to show our start and end positions
    # @return table
    def build_table(self):
        v1 = client.CoreV1Api()  # we want a new instance per namespace

        table = PrettyTable(['Namespace', 'Pod', 'Volume-Name', 'PVC', 'Annotations'])

        for n in self.namespaces:
            ret = v1.list_namespaced_pod(n, watch=False)
            for i in ret.items:
                for v in i.spec.volumes:
                    if v.persistent_volume_claim:
                        table.add_row([n, i.metadata.name, v.name, v.persistent_volume_claim.claim_name, i.metadata.annotations])

        return table

    # entry method for building all pods, calls annotate pod.
    # actual annotation is done in the child function
    def annotate_pods(self):
        v1 = client.CoreV1Api()  # we want a new instance per namespace
        for namespace in self.pod_map:
            self.annotate_pod(namespace, v1)  # annotate the pod with whatever volumes we find

    # the actual annotation happens here per pod
    # does not return anything, but will raise an exception if something goes wrong
    def annotate_pod(self, namespace, v1):

        print("\nAnnotating namespace: " + str(namespace))

        for pod in self.pod_map[namespace]:

            volume_list = self.get_volume_list(namespace, pod)

            # currently, we don't care about existing annotations, since they'll be blank after build anyway
            # @todo - we may want to extend this later to allow for previous annotations

            # the format we want is below per pod, this should be based on our pod_map which is built based on all volumes per pod in the k8s object
            # {'backup.velero.io/backup-volumes': 'raffia-config,raffia-domains,raffia-var,raffia-home'}
            body = {"metadata": {"annotations": {"backup.velero.io/backup-volumes": volume_list}}}

            # now annotate the pod
            try:
                v1.patch_namespaced_pod(pod, namespace, body)
                print("Pod [" + pod + "] done. Added the following volumes for backup: " + str(volume_list))
            except ApiException as e:
                print("AAHH something went wrong! Could not annotate pod (" + str(self.pod_map[namespace][pod]) + ").")
                exit(1)

    # get a list of all volumes for a specific pod within a namespace
    # @return volume_list
    def get_volume_list(self, namespace, pod):

        # for pod in pod_map[namespace]:
        volume_list = ""  # create a new list per pod
        for volume in self.pod_map[namespace][pod]:
            volume_list += volume + ","  # format calls for comma separation (no space)

        volume_list = volume_list[:-1]  # strip the last comma off the complete volume_list
        return volume_list

    # get human readable preview of what will happen when we run this
    # @return preview
    def get_preview(self):
        preview = ""
        for namespace in self.pod_map:
            preview += "    Namespace: " + namespace + "\n"
            for pod in self.pod_map[namespace]:
                preview += "        Pod: " + pod + "\n"
                for volume in self.pod_map[namespace][pod]:
                    #if volume.persistent_volume_claim:
                    preview += "            Volume: " + volume + "\n"
        return preview

    # print an error message if no namespace is provided as an argument
    def print_help(self):
        print('I need the namespace(s) as an argument')
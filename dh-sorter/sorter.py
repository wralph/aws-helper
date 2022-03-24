class EC2Instance:
    def __init__(self, type, vCPU):
        self.type = type
        self.family = self.__family()
        self.vCPU = vCPU

    def __family(self):
        return self.type.rsplit(".")[0]

class CapacityProvider:
    def getCapacity(self, type):
        if type == "r5" or type == "r5b":
           return 96


class DedicatedHost:    
    def __init__(self, type):
        self.type = type
        self.usage = 0
        self.vCPU = CapacityProvider().getCapacity(type)
        self.instances = []

    # adds an instance to a host. returns False if instance has no capacity
    def addInstance(self, instance):
        if instance.vCPU <= self.__balance():
            self.usage = self.usage + instance.vCPU
            self.instances.append(instance)
            return True
        else:
            return False

    def printUsage(self):
        print("type: " + self.type)
        print("usage: " + str(self.usage))
        print("--instances--")
        for i in self.instances:
            print(i.type)
        print("--------------")

    def __balance(self):
        return self.vCPU - self.usage

class HostSorter:
    def __init__(self):
        self.instances = [] # instance list
        self.hosts = {}
    
    # add all instances first
    def addInstance(self, instance):
        self.instances.append(instance)

    # execute placements
    def placeInstances(self):
        self.__sortInstances() # sort biggest vCPU to smallest
        for i in self.instances:
            self.__placeInstance(i)

    def printUsage(self):
        for hostFamily in self.hosts.values():
            for h in hostFamily:
                h.printUsage()
    
    def __sortFunc(self, n):
        return n.vCPU

    def __sortInstances(self):
        self.instances.sort(key = self.__sortFunc, reverse=True)
        return -1
    
    def __placeInstance(self, instance):
        # initialize instance family if needed
        if instance.family not in self.hosts:
            self.hosts[instance.family] = []

        # get available hosts in the instance family
        instanceHosts = self.hosts[instance.family]
        self.__placeInstanceOnHost(instanceHosts, instance)
    
    def __placeInstanceOnHost(self, instanceHosts, instance):
        placed = False

        # try to place instance on an existing host
        for host in instanceHosts:
            if host.addInstance(instance) == True:
                placed = True
                continue

        # if no existing host, place instance on a new host
        if placed is False:
            newHost = DedicatedHost(instance.family)
            instanceHosts.append(newHost)
            newHost.addInstance(instance)

    def printUsage(self):
        for hostFamily in self.hosts.values():
            for h in hostFamily:
                h.printUsage()


r5_2xl = EC2Instance("r5.2xlarge", 8)
r5_12xl = EC2Instance("r5.12xlarge", 48)
r5b_2xl = EC2Instance("r5b.8xlarge", 8)
r5b_12xl = EC2Instance("r5b.12xlarge", 48)

x = HostSorter()
x.addInstance(r5_2xl)
x.addInstance(r5_12xl)
x.addInstance(r5_12xl)
x.addInstance(r5_12xl)

x.addInstance(r5b_2xl)
x.addInstance(r5b_12xl)
x.addInstance(r5b_12xl)
x.addInstance(r5b_12xl)

x.placeInstances()
x.printUsage()
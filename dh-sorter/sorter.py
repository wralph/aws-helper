import imp
with open('.config/t3blocks.py', 'rb') as fp:
    t3blocks = imp.load_module('.config', fp, '.config/__init__.py', ('.py', 'rb', imp.PY_SOURCE))  

class EC2Instance:
    def __init__(self, type, vCPU):
        self.type = type
        self.family = self.__family()
        self.size = self.__size()
        self.vCPU = vCPU

    def __family(self):
        return self.type.rsplit(".")[0]

    def __size(self):
        return self.type.rsplit(".")[1]

class CapacityProvider:
    def getCapacity(self, type):
        if type == "r5" or type == "r5b":
           return 96

class Block:
    def __init__(self, type):
        self.type = type
        self.usage = 0
        self.vCPU = 0 # to be initialized by inherited class
        self.instances = []

    # adds an instance to a block. returns False if block has no capacity
    def addInstance(self, instance):
        if instance.vCPU <= self.__balance():
            self.usage = self.usage + instance.vCPU
            self.instances.append(instance)
            return True
        else:
            return False

    def printUsage(self):
        print("Block --------------")
        print("type: " + self.type)
        print("usage: " + str(self.usage))
        print("--instances--")
        for i in self.instances:
            print(i.type)
        print("--------------")

    def __balance(self):
        return self.vCPU - self.usage

class DedicatedHost(Block):    
    def __init__(self, type):
        super().__init__(type)
        self.vCPU = CapacityProvider().getCapacity(type)

class T3DedicatedHost(DedicatedHost):
    def __init__(self, type):
        super().__init__(type)
        self.blocks = []
    
    # get values from config

    # add an instance to a T3 host. Bucketing must be respected
    def addInstance(self, instance):
        # try to place instance on an existing block
        for block in self.blocks:
            if block.addInstance(instance) == True:
                return True

        # if no existing block, place instance on a new block if possible on existing DH
        if self.__blockCapacityAvailable(instance.size) == True:
            block = Block(instance.family)
            block.vCPU = self.__getBlockCapacity(instance.size)
            self.blocks.append(block)
            block.addInstance(instance)
            return True
        
        return False

    def printUsage(self):
        print("T3 Host --------------")
        for block in self.blocks:
            block.printUsage()
        print("--------------")

    def __blockCapacityAvailable(self, size):
        # TODO needs to check the current blocks whether anotheron can be added
        return True

    def __getBlockCapacity(self, size):
        # TODO: implement
        return 8

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
        # try to place instance on an existing host
        for host in instanceHosts:
            if host.addInstance(instance) == True:
                return

        # if no existing host, place instance on a new host
        if instance.family == "t3":
            newHost = T3DedicatedHost(instance.family)
        else:
            newHost = DedicatedHost(instance.family)
        instanceHosts.append(newHost)
        newHost.addInstance(instance)


    def printUsage(self):
        for hostFamily in self.hosts.values():
            for h in hostFamily:
                h.printUsage()
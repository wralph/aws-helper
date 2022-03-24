import unittest
from sorter import EC2Instance 
from sorter import HostSorter 

class TestDedicatedHosts(unittest.TestCase):
    def setUp(self):
        self.r5_2xl = EC2Instance("r5.2xlarge", 8)
        self.r5_12xl = EC2Instance("r5.12xlarge", 48)
        self.r5b_2xl = EC2Instance("r5b.8xlarge", 8)
        self.r5b_12xl = EC2Instance("r5b.12xlarge", 48)

    def test_1r5_host(self):
        x = HostSorter()
        x.addInstance(self.r5_12xl)
        x.addInstance(self.r5_12xl)
        x.placeInstances()
        self.assertEqual(len(x.hosts["r5"]), 1, "Should be 1 host")

    def test_2r5_host(self):
        x = HostSorter()
        x.addInstance(self.r5_12xl)
        x.addInstance(self.r5_12xl)
        x.addInstance(self.r5_12xl)
        x.placeInstances()
        self.assertEqual(len(x.hosts["r5"]), 2, "Should be 1 host")

    def test_6r5_host(self):
        x = HostSorter()
        x.addInstance(self.r5_12xl)
        x.addInstance(self.r5_12xl)
        x.addInstance(self.r5_12xl)
        x.addInstance(self.r5_12xl)
        x.addInstance(self.r5_12xl)
        x.addInstance(self.r5_12xl)
        x.addInstance(self.r5_12xl)
        x.addInstance(self.r5_12xl)
        x.addInstance(self.r5_12xl)
        x.addInstance(self.r5_12xl)
        x.addInstance(self.r5_12xl)        
        x.placeInstances()
        self.assertEqual(len(x.hosts["r5"]), 6, "Should be 6 hosts")

class TestT3DedicatedHosts(unittest.TestCase):
    def setUp(self):
        self.t3_xl = EC2Instance("t3.xlarge", 4)

    def test_1t3_host(self):
        x = HostSorter()
        x.addInstance(self.t3_xl)
        x.placeInstances()
        self.assertEqual(len(x.hosts["t3"]), 1, "Should be 1 hosts")


if __name__ == '__main__':
    unittest.main()
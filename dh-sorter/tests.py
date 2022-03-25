import unittest
from sorter import EC2Instance 
from sorter import HostSorter 

region = "eu-central-1"

class TestDedicatedHosts(unittest.TestCase):
    def setUp(self):
        self.r5_2xl = EC2Instance("r5.2xlarge", 8)
        self.r5_12xl = EC2Instance("r5.12xlarge", 48)
        self.r5b_2xl = EC2Instance("r5b.8xlarge", 8)
        self.r5b_12xl = EC2Instance("r5b.12xlarge", 48)

    def test_1r5_host(self):
        x = HostSorter(region)
        x.addInstance(self.r5_12xl)
        x.addInstance(self.r5_12xl)
        x.placeInstances()
        self.assertEqual(len(x.hosts["r5"]), 1, "Should be 1 host")

    def test_2r5_host(self):
        x = HostSorter(region)
        for i in range(3):
            x.addInstance(self.r5_12xl)
        x.placeInstances()
        self.assertEqual(len(x.hosts["r5"]), 2, "Should be 1 host")

    def test_6r5_host(self):
        x = HostSorter(region)
        for i in range(11):
            x.addInstance(self.r5_12xl)
        x.placeInstances()
        self.assertEqual(len(x.hosts["r5"]), 6, "Should be 6 hosts")

    def test_mixed_hosts(self):
        x = HostSorter(region)
        for i in range(5):
            x.addInstance(self.r5_12xl)
        for i in range(5):
            x.addInstance(self.r5b_12xl)
        x.placeInstances()
        self.assertEqual(len(x.hosts["r5"]), 3, "Should be 3 r5 hosts")
        self.assertEqual(len(x.hosts["r5b"]), 3, "Should be 3 r5b hosts")

class TestT3DedicatedHosts(unittest.TestCase):
    def setUp(self):
        self.t3_xl = EC2Instance("t3.xlarge", 4)
        self.t3_2xl = EC2Instance("t3.2xlarge", 8)
        self.t3_medium = EC2Instance("t3.medium", 2)
        self.t3_small = EC2Instance("t3.small", 2)
        self.t3_micro = EC2Instance("t3.micro", 2)
        self.t3_nano = EC2Instance("t3.nano", 2)

    def test_1t3_host(self):
        x = HostSorter(region)
        x.addInstance(self.t3_xl)
        x.placeInstances()
        self.assertEqual(len(x.hosts["t3"]), 1, "Should be 1 hosts")

    def test_1mixedt3_host(self):
        x = HostSorter(region)
        for i in range(16):
            x.addInstance(self.t3_nano)
        for i in range(40):
            x.addInstance(self.t3_micro)
        for i in range(40):
            x.addInstance(self.t3_small)
        for i in range(20):
            x.addInstance(self.t3_2xl)
        x.placeInstances()
        self.assertEqual(len(x.hosts["t3"]), 1, "Should be 1 hosts")

    def test_1mixedt3_host2(self):
        x = HostSorter(region)
        for i in range(104):
            x.addInstance(self.t3_micro)
        for i in range(40):
            x.addInstance(self.t3_small)
        for i in range(16):
            x.addInstance(self.t3_medium)
        for i in range(16):
            x.addInstance(self.t3_2xl)
        x.placeInstances()
        self.assertEqual(len(x.hosts["t3"]), 1, "Should be 1 hosts")

    def test_1mixedt3_host3(self):
        x = HostSorter(region)
        for i in range(64):
            x.addInstance(self.t3_micro)
        for i in range(12):
            x.addInstance(self.t3_xl)
        for i in range(16):
            x.addInstance(self.t3_2xl)
        x.placeInstances()
        self.assertEqual(len(x.hosts["t3"]), 1, "Should be 1 hosts")

    def test_2mixedt3_host(self):
        x = HostSorter(region)
        for i in range(16):
            x.addInstance(self.t3_nano)
        for i in range(40):
            x.addInstance(self.t3_micro)
        for i in range(40):
            x.addInstance(self.t3_small)
        for i in range(22):
            x.addInstance(self.t3_2xl)
        x.placeInstances()
        self.assertEqual(len(x.hosts["t3"]), 2, "Should be 2 hosts")

    def test_2mixedt3_host2(self):
        x = HostSorter(region)
        for i in range(48):
            x.addInstance(self.t3_2xl)
        x.placeInstances()
        self.assertEqual(len(x.hosts["t3"]), 2, "Should be 2 hosts")


if __name__ == '__main__':
    unittest.main()
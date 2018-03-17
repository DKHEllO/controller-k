# coding=utf-8

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.node import RemoteController


class MyTopo(Topo):
    def __init__(self):
        super(MyTopo, self).__init__()

        core = self.addSwitch('s1')

        host_1 = self.addHost('h1')
        host_2 = self.addHost('h2')
        host_3 = self.addHost('h3')

        self.addLink(core, host_3)
        self.addLink(core, host_1)
        self.addLink(core, host_2)


def run_flow():
    topo = MyTopo()
    net = Mininet(topo=topo, controller=lambda name: RemoteController(name,ip='127.0.0.1'))
    net.start()
    net.pingAll()
    net.iperf(seconds=20)


if __name__ == '__main__':
    setLogLevel('info')
    run_flow()
# What is MechOS
The Mechatronics Operating System (MechOS) is an easy to use networking framework intended for creating modular software architectures for robotics and distributed computing systems. MechOS is entirely built in Python 3 and only requires the standard libraries already installed with Python 3...it is super easy to get started!

## Motivation Behind MechOS

The motivation to create MechOS stemmed from the difficultly of creating modular and dynamically developing robotic systems. The ability to run on most operating systems (such as Linux, Windows, and MacOS),  support multi-machine distribution, and work entirely with Python 3 makes MechOS reliable and easy to use for both simple and complex distributed systems. 

Since robotic related systems tend to be complex and have many processes working simultaneously, MechOS was developed to abstract processes (such as getting sensor data or driving and actuator) by encouraging a node-graph based software architectures. These node-graph architectures are supported through MechOS's "node" process communication design as well as the Publisher/Subscriber based communication system between processes.

## Installation

If you already have python on your system, you can download this repository and install its package by running:

```python
python setup.py install
```

## Getting Started

To get started using MechOS, please checkout the the [examples](MechOS/examples). It is suggested to start with the [simple_pub_sub tutorial](MechOS/examples/simple_pub_sub).

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xml.etree.ElementTree as ET
from multiprocessing import Process

class Parameter_Server:
    '''
    An xmlrpc server running the MechOS parameter server. This class allows one
    to set and get parameters to a specified xml file.
    '''
    def __init__(self, ip=None, port=None):
        '''
        Initialize Parameter server for XMLRPCServer.

        Parameters:
            ip: The ip address to host the XMLRPCServer. Default "http://127.0.0.101"
            port: The port to host the XMLRPCServer. Default 8000

        Returns:
            N/A
        '''
        if ip == None:
            ip = "127.0.0.101"

        if port == None:
            port = 8000
        self.server = SimpleXMLRPCServer((ip, port))
        self.xml_file = None

        self.server.register_function(self.use_parameter_database)
        self.server.register_function(self.set_param)
        self.server.register_function(self.get_param)

    def use_parameter_database(self, xml_file):
        '''
        Sets the xml file to use for the parameter server to store and retreive
        data from.

        Parameters:
            xml_file: The xml file to save and get parameters from.

        Returns:
            true
        '''


        self.xml_file = xml_file
        return True

    def set_param(self, param_path, parameter):
        '''
        Set a parameter in the the xml file database. If the parameter path already
        exist, then update its content with the new parameters. If the parameter
        path does not exist, create the parameter path and add the parameter value.

        Parameter:
            param_path: The parameter path tree to set the given parameter. Note:
                        each level name should be spaced by a '/'.
                        Example 'PID/roll_pid/p'
            parameter: The string representation of the parameter you want to set.

        Returns:
            N/A
        '''
        try:
            #Get xml data tree
            tree = ET.parse(self.xml_file)
            tree_head_previous = tree.getroot()

            #split parameter path into individual components
            param_path_list = param_path.split('/')

            #Search through param path and set parameters
            for level, param_tag in enumerate(param_path_list):
                tree_head = tree_head_previous.findall(param_tag)

                #If the parameter does not exist, create the path and set parameter
                if len(tree_head) == 0:
                    #Generate the new path
                    sub_element = tree_head_previous
                    for sub_element_name in param_path_list[level:]:
                        sub_element = ET.SubElement(sub_element, sub_element_name)
                        sub_element.text = parameter

                        tree.write(self.xml_file)
                        return True

                    else:
                        tree_head_previous = tree_head[0]
                        #Set parameter
                    tree_head[0].text = parameter
                    tree.write(self.xml_file)
                    return True
        except Exception as e:
            print("Could not set parameter path", param_path, "with parameter", paramter, ":", e)
            return False

    def get_param(self, param_path):
        '''
        Get the parameter from the given parameter_path. If the parameter does not
        exist, through an error.

        Parameters:
            param_path: The parameter path tree to set the given parameter.

        Returns:
            N/A
        '''
        try:
            tree = ET.parse(self.xml_file)
            tree_head = tree.getroot()

            param_path = param_path.split('/')

            #Search for parameter in parameter path.
            for level, param_tag in enumerate(param_path):
                tree_head = tree_head.findall(param_tag)

                tree_head = tree_head[0]
            parameter = tree_head.text
            return parameter
        except Exception as e:
            print("Could not get parameter", param_path, ". Parameter path may not exsist:", e)
            return False
    def run(self):
        '''
        Run the xml rpc parameter server.

        Parameter:
            N/A

        Returns:
            N/A
        '''
        self.server.serve_forever()

from configparser import *


class Config():
    def __init__(self, ini_file_path):
        """
        :param ini_file_path: ini 文件的路径
        """
        self.config = ConfigParser()  # 实例化
        self.config.read(ini_file_path, encoding="utf-8")

    def get_section(self):
        """
        文件中 [baseconf] 这个就是节点，该方法是获取文件中所有节点，并生成列表
        :return: 返回内容-->> ['baseconf', 'concurrent']
        """
        sections = self.config.sections()
        return sections

    def get_option(self, section_name):
        """
        文件中 host,port... 这个就是选项，该方法是获取文件中某个节点中所有的选项，并生成列表
        :param section_name: 节点名称
        :return: section_name="baseconf" 返回内容-->> ['host', 'port', 'user', 'password', 'db_name']
        """
        option = self.config.options(section_name)
        return option

    def get_items(self, section_name):
        """
        该方法是获取文件中某个节点中的所有选项及对应的值
        :param section_name: 节点名称
        :return: section_name="baseconf" 返回内容-->> [('host', '127.0.0.1'), ('port', '11223')........]
        """
        option_items = self.config.items(section_name)
        return option_items

    def get_value(self, section_name, option_name):
        """
        该方法是获取文件中对应节点中对应选项的值
        :param section_name: 节点名称
        :param option_name: 选项名称
        :return: section_name="baseconf"，option_name='host' 返回内容-->> '127.0.0.1'
        """
        data_msg = self.config.get(section_name, option_name)
        return data_msg

    def set_value(self, section_name, option_name, value):
        """
        设置相关的值
        :param section_name: 节点名称
        :param option_name: 选项名称
        :param value: 选项对应的值
        :return:
        """
        self.config.set(section_name, option_name, value)
        # 举例： config.set("baseconf", 'host', 192.168.1.1)

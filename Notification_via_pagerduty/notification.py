import argparse
import yaml
import os
import operator

from pdpyras import EventsAPISession
#from unittest.mock import MagicMock
import json


def parse_arguments():
      notif_parse = argparse.ArgumentParser()
      # Add the arguments to the notification parser
      notif_parse.add_argument("-s", "--status-code", required=True, help="predefined error code") # required=True means the argument is mandatory
      notif_parse.add_argument("-n1", "--notify1", required=True, help="predefined destination where a message needs to be routed (which group to notify)")
      notif_parse.add_argument("-n2", "--notify2", required=False, help="predefined destination where a message needs to be routed (which group to notify)")
      notif_parse.add_argument("-c", "--context-file", required=False, help="this file provides some context(in key-value  format) of what was being worked on when the error was     thrown from a module")
      global args_dict, l, file_path
      args_dict = vars(notif_parse.parse_args())
      print(f'arguments: {args_dict}\n')
      #file_path="/home/ammallar/.cookiecutters/cookiecutter-pypackage/notification/notification"
      #file_path="/var/tmp/work_dir/notif_tool/notification/notification"
      filepath=os.path.dirname(os.path.abspath(__file__))
      l = os.listdir(file_path)
 

class notification_base(object):

     summary = ''
     proj_val = ''
     notif_file_dict = {}
 
     def lookup_error_msg(self):
         
         for yaml_lookup in l:
             if yaml_lookup.endswith('.yml') and yaml_lookup.startswith('error'):
                 status_code = args_dict['status_code'].split('-')[1]
                 print(f"error status_code: {status_code}\n")
                 with open(os.path.join(file_path, yaml_lookup)) as e:
                     error_file_dict = yaml.safe_load(e)
                     ## add the message, cause, and action to the 'summary' in pagerduty
                     message = error_file_dict['default'][int(status_code)]['message']
                     cause = error_file_dict['default'][int(status_code)]['cause']
                     action = error_file_dict['default'][int(status_code)]['action']
                     ##criticality = error_file_dict['default'][int(status_code)]['criticality']
                     notification_base.summary = f'message: {message}. cause: {cause}. action: {action}.'
                     
             if yaml_lookup.endswith('.yml') and yaml_lookup.startswith('project'):
                 with open(os.path.join(file_path, yaml_lookup)) as p:
                     proj_file_dict = yaml.safe_load(p)
                     k = list(proj_file_dict.keys())
                     for notification_base.proj_val in k:
                         if notification_base.proj_val in args_dict['status_code']:
                             print(f"project: {notification_base.proj_val}\n")


     def lookup_notification_group(self):
         
         for yaml_lookup in l:
             if yaml_lookup.endswith('.yml') and yaml_lookup.startswith('notification'):
                 with open(os.path.join(file_path, yaml_lookup)) as n:
                     notification_base.notif_file_dict = yaml.safe_load(n)
                     nk = list(notification_base.notif_file_dict.values())
                     self.l_nk = list(nk[0].keys())
                     
       
     def lookup_notification_type(self):
         
         if args_dict['notify1'] in self.l_nk:
             print("integration key1: ", notification_base.notif_file_dict['NotificationKeys'][ notification_base.notif_file_dict['Groups'][args_dict['notify1']]['notification_key'] ]['integration_key'])
             notif_type1 = notification_base.notif_file_dict['NotificationKeys'][ notification_base.notif_file_dict['Groups'][args_dict['notify1']]['notification_key'] ]['type']
             print(f'notif type1: {notif_type1}\n')
 
         if args_dict['notify2'] in self.l_nk:
             print("integration key2: ", notification_base.notif_file_dict['NotificationKeys'][ notification_base.notif_file_dict['Groups'][args_dict['notify2']]['notification_key'] ]['integration_key'])
             notif_type2 = notification_base.notif_file_dict['NotificationKeys'][ notification_base.notif_file_dict['Groups'][args_dict['notify2']]['notification_key'] ]['type']
             print(f'notif type2: {notif_type2}\n')



class pagerduty_notif(notification_base):

     context_items = {}
     severity = ''
     payload = {}
     routing_key1 = ''
     routing_key2 = ''
 
     def lookup_yaml_details(self):
         
         parse_arguments()
         self.lookup_error_msg()
         self.lookup_notification_group()
         self.lookup_notification_type()


     def process_context(self):
         for context_lookup in l:
             if 'context' in context_lookup:
                 if args_dict['context_file'] == None:
                     pagerduty_notif.context_items = {}
                     with open(os.path.join(file_path, context_lookup)) as c:
                         for line in c.readlines():
                             key, value = line.rstrip("\n").split("=")
                             pagerduty_notif.context_items[key] = value

                         ## this context_items will be added to the 'custom_details' in pagerduty ##
                         print("context_items: ", pagerduty_notif.context_items)

                     self.set_severity_routingkey()
                     print('severity: ', pagerduty_notif.severity)
                     self.create_payload()
                     print('payload: ', pagerduty_notif.payload)

                     self.send_notification()

                     ## temporary code for send_notification ##
                     """
                     dedup_key = '123'
                     sendnotif_mock = MagicMock()
                     sendnotif_mock.method.return_value = dedup_key
                     ##assert(sendnotif_mock.method() != '123'), "SEND NOTIFICATION IS UNSUCCESSFUL"
                     msg_ok = "SEND NOTIFICATION IS SUCCESSFUL"
                     msg_not_ok = "SEND NOTIFICATION IS UNSUCCESSFUL"
                     if sendnotif_mock.method() == '123':
                         print(msg_ok)
                     else:
                         print(msg_not_ok)
                     """

                 else:
                     with open(os.path.join(file_path, args_dict['context_file']), 'w') as cf:
                        with open(os.path.join(file_path, 'key_values.json')) as rcf:
                            keys_values = json.load(rcf)
                            key_list = list(keys_values['context'].keys())
                            value_list = list(keys_values['context'].values())
                            pagerduty_notif.context_items = {}
                            for idx in range(0, len(key_list)):
                                pagerduty_notif.context_items[key_list[idx]] = value_list[idx]
                            print("context_items: ", pagerduty_notif.context_items)

                            for key, value in sorted(pagerduty_notif.context_items.items(), key=operator.itemgetter(1)):
                                print(key, value)
                                cf.write(f'{key}={value}\n')

                     self.set_severity_routingkey()
                     print('severity: ', pagerduty_notif.severity)
                     self.create_payload()
                     print('payload: ', pagerduty_notif.payload)

                     self.send_notification()

                     ## temporary code for send_notification ##
                     """
                     dedup_key = '123'
                     sendnotif_mock = MagicMock()
                     sendnotif_mock.method.return_value = dedup_key
                     ##assert(sendnotif_mock.method() != '123'), "SEND NOTIFICATION IS UNSUCCESSFUL"
                     msg_ok = "SEND NOTIFICATION IS SUCCESSFUL"
                     msg_not_ok = "SEND NOTIFICATION IS UNSUCCESSFUL"
                     if sendnotif_mock.method() == '123':
                         print(msg_ok)
                     else:
                         print(msg_not_ok)
                    """


     def create_payload(self):
         
         pagerduty_notif.payload = { 'summary': notification_base.summary, 
                     'project': notification_base.proj_val, 
                     'severity': pagerduty_notif.severity, 
                     'custom_detail': pagerduty_notif.context_items 
                   }


     def set_severity_routingkey(self):
         
         pagerduty_notif.severity = 'critical'
         pagerduty_notif.routing_key1 = notification_base.notif_file_dict['NotificationKeys'][notification_base.notif_file_dict['Groups'][args_dict['notify1']]['notification_key']]['integration_key']
         pagerduty_notif.routing_key2 = notification_base.notif_file_dict['NotificationKeys'][notification_base.notif_file_dict['Groups'][args_dict['notify2']]['notification_key']]['integration_key']


     def send_notification(self):
         
         session1 = EventsAPISession(pagerduty_notif.routing_key1)
         dedup_key1 = session1.trigger(pagerduty_notif.payload['summary'], notification_base.proj_val, severity=pagerduty_notif.severity, custom_details=pagerduty_notif.payload['custom_detail'], images=[])
         print("dedup_key1: ", dedup_key1)

         session2 = EventsAPISession(pagerduty_notif.routing_key2)
         dedup_key2 = session2.trigger(pagerduty_notif.payload['summary'], notification_base.proj_val, severity=pagerduty_notif.severity, custom_details=pagerduty_notif.payload['custom_detail'], images=[])
         print("dedup_key2: ", dedup_key2)
         return dedup_key1, dedup_key2
        


class ocean_notif(notification_base):

     def lookup_yaml_details(self):
         pass
         
         
     def process_context(self):
         pass


     def create_payload(self):
         pass


     def set_severity_routingkey(self):
         pass


     def send_notification(self):
         pass


p = pagerduty_notif()
p.lookup_yaml_details()
p.process_context()

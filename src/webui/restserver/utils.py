'''
Created on Aug 19, 2011

@author: mmornati
'''
from django.utils import simplejson as json
import logging
from celery.execute import send_task
from webui.platforms.platforms import platforms
from webui.platforms.abstracts import UpdatePlatform
from webui.widgets.loading import registry
from webui import settings
from webui.core import KermitMcoResponse, KermitMcoContent

logger = logging.getLogger(__name__)

FILTERS_NO_LIST = ['compound']

class Actions(object):

    def refresh_dashboard(self, user):
        logger.info("Getting all Widgets from database")
        try: 
            registry.reset_cache()
            widgets_list = registry.refresh_widgets()
            for widget in widgets_list:
                retrieved = registry.get_widget(widget['name'])
                retrieved.db_reference = widget

            json_data = json.dumps({'UUID': None, 'taskname': None})
            return json_data
        except Exception, err:
            logger.error('ERROR: ' + str(err))
                
    def refresh_server_basic_info(self, user):
        logger.info("Calling Refresh Basic Info")
        try: 
            result = send_task("webui.servers.tasks.server_basic_info", [user])    
            json_data = json.dumps({'UUID': result.task_id, 'taskname':"webui.servers.tasks.server_basic_info"})
            return json_data
        except Exception, err:
            logger.error('ERROR: ' + str(err))
        
    def refresh_server_inventory(self, user):
        logger.info("Calling Refresh Inventory")
        try: 
            updates_defined = platforms.extract(UpdatePlatform)
            result = send_task("webui.servers.tasks.server_inventory", [user, updates_defined])    
            json_data = json.dumps({'UUID': result.task_id, 'taskname':"webui.servers.tasks.server_inventory"})
            return json_data
        except Exception, err:
            logger.error('ERROR: ' + str(err))
    
    def update_agents(self, user):
        logger.info("Calling Update Agents Info")
        try: 
            result = send_task("webui.agent.tasks.updateagents", [user])    
            json_data = json.dumps({'UUID': result.task_id, 'taskname':"webui.agent.tasks.updateagents"})
            return json_data
        except Exception, err:
            logger.error('ERROR: ' + str(err))
      
    def update_user_groups(self, user):
        logger.info("Calling Refresh User Group")
        if 'a7x_wsgroups' in settings.INSTALLED_APPS:
            try: 
                result = send_task("a7x_wsgroups.tasks.update_groups", [])    
                json_data = json.dumps({'UUID': result.task_id, 'taskname':"a7x_wsgroups.tasks.update_groups"})
                return json_data
            except Exception, err:
                logger.error('ERROR: ' + str(err))
        else:
            logger.warn('Application Groups not installed')
            return json.dumps({'error':"Application Groups not installed"})
        
    def updated_puppet_classes(self, user):
        logger.info("Calling Update Puppet Classes")
        try: 
            result = send_task("webui.puppetclasses.tasks.update_all_puppet_classes", [user])    
            json_data = json.dumps({'UUID': result.task_id, 'taskname':"webui.puppetclasses.tasks.update_all_puppet_classes"})
            return json_data
        except Exception, err:
            logger.error('ERROR: ' + str(err))
            
    def updated_dyna_groups(self, user):
        logger.info("Calling Update Dyna Groups")
        try: 
            result = send_task("webui.dynamicgroups.tasks.update_dyna_group", [user])    
            json_data = json.dumps({'UUID': result.task_id, 'taskname':"webui.dynamicgroups.tasks.update_dyna_group"})
            return json_data
        except Exception, err:
            logger.error('ERROR: ' + str(err))
             
    
def convert_response(response):
    kmr = None
    if response:
        kmr = KermitMcoResponse(response.status)
    return kmr

def convert_content(content):
    content_list = []
    logger.info(content)
    try:
        json_content = json.loads(content)
        for msg in json_content:
            content_list.append(KermitMcoContent(msg['data'], msg['statuscode'], msg['sender'], msg['statusmsg']))
    except:
        logger.error("Cannot convert content to a json object! Response error. Check Kermit-RestMCO log")
        
    return content_list

def convert_filters_to_hash(filters):
    filters_dict = {}
    logger.debug("Passed Filters: %s" % filters)
    if filters:
        params_list = filters.split(";")
        for current_param in params_list:
            values = current_param.split("=")
            if not values[0] in filters_dict:
                if values[0] not in FILTERS_NO_LIST:
                    filters_dict[values[0]] = []
                else:
                    filters_dict[values[0]] = ""
            #Fix to allow '=' chars in filter values
            if len(values)>2:
                to_apply = '='.join(values[1:])
            else:
                to_apply = values[1]
        
            if values[0] not in FILTERS_NO_LIST:
                filters_dict[values[0]].append(to_apply)
            else:
                filters_dict[values[0]] = to_apply
        
    logger.debug("Filters: %s" % filters_dict)
    return filters_dict
        
def convert_parameters_to_hash(params):
    params_dict = {}
    if params:
        params_list = params.split(";")
        for current_param in params_list:
            values = current_param.split("=")
            if not values[0] in params_dict:
                #Quick and Dirty fix for Boolean
                #TODO: Send parameter type with any params. If not provided is String by default
                if values[1]=="True":
                    to_assign = True
                elif values[1]=="False":
                    to_assign = False
                else:
                    to_assign=values[1]
                #end fix    
                
                params_dict[values[0]] = to_assign
        
    logger.debug("Parameters: %s" % params_dict)
    return params_dict
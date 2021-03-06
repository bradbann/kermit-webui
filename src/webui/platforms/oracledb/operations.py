'''
Created on Nov 8, 2011

@author: mmornati
'''
from webui.abstracts import ContextOperation
from webui import settings
from webui.core import kermit_modules
from guardian.shortcuts import get_objects_for_user
from webui.agent.models import Agent, Action

class OracleDBxecuteContextMenu(ContextOperation):
    
    def get_operations(self):
        context_menu_ops = []
        context_menu_ops.append(
            {"name":"execute_sql",
             "description":"Execute SQL",
             "javascript":"getSqlExecutionForm('%s', 'oracledb', 'deploy-dialog', 'execute_sql', '$$filterlist$$')" % settings.BASE_URL,
             "server_operation":"",
             })
        return context_menu_ops
    
    def get_type(self):
        return 'OracleDB'
    
    def get_visible(self, server):
        agent = server.agents.filter(name='oracledb')
        classes = server.puppet_classes.filter(name='odb')
        return len(agent)==1 and len(classes)==1
    
    def get_enabled(self, user):
        if not user.is_superuser:
            agents = get_objects_for_user(user, 'use_agent', Agent).filter(enabled=True, name="oracledb")
            if len(agents)==1:
                action = get_objects_for_user(user, 'use_action', Action).filter(agent=agents[0], name="execute_sql")
                return action and len(action)==1
            else:
                return False
        else:
            return True
    
    
class OracleCloneDatabaseContextMenu(ContextOperation):
    
    def get_operations(self):
        context_menu_ops = []
        context_menu_ops.append(
            {"name":"clone_database",
             "description":"Clone Database",
             "javascript":"getForm('%s', 'oracledb', 'deploy-dialog', 'clonedatabase', '$$filterlist$$')" % settings.BASE_URL,
             "server_operation":"",
             })
        return context_menu_ops
    
    def get_type(self):
        return 'OracleDB'
    
    def get_visible(self, server):
        agent = server.agents.filter(name='oracledb')
        classes = server.puppet_classes.filter(name='odb')
        return len(agent)==1 and len(classes)==1
    
    def get_enabled(self, user):
        if not user.is_superuser:
            agents = get_objects_for_user(user, 'use_agent', Agent).filter(enabled=True, name="oracledb")
            if len(agents)==1:
                action = get_objects_for_user(user, 'use_action', Action).filter(agent=agents[0], name="export_database")
                return action and len(action)==1
            else:
                return False
        else:
            return True
    
    
kermit_modules.register(OracleDBxecuteContextMenu)
kermit_modules.register(OracleCloneDatabaseContextMenu)
import logging
from webui import settings
from django.template.context import RequestContext
from django.shortcuts import render_to_response
from communication import read_server_info
from webui.platforms.utils import convert_keys_names, extract_servers,\
    read_file_log
from django.contrib.auth.decorators import login_required
from guardian.decorators import permission_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from webui.platforms.weblogic.utils import get_apps_list, extract_instances_name
from django.utils import simplejson as json
from webui.platforms.weblogic.forms import DeployForm, LogForm, InstanceForm
from webui.restserver.communication import callRestServer

logger = logging.getLogger(__name__)

@login_required()
def instanceInventory(request, hostname, resource_name):
    server_info = read_server_info(hostname)
    if server_info:
        selected_instance = None
        for instance in server_info["instances"]:
            if instance['name'] == resource_name:
                selected_instance = instance
                break
        convert_keys_names(selected_instance)
        if 'java_ver' in server_info:
            java_version = server_info["java_ver"]
        else: 
            java_version = ""
        return render_to_response('platforms/weblogic/instance.html', {"base_url": settings.BASE_URL, "static_url":settings.STATIC_URL,"hostname":hostname, "instance": selected_instance, "java_version": java_version}, context_instance=RequestContext(request))
    else:
        return render_to_response('platforms/weblogic/instance.html', {"base_url": settings.BASE_URL, "static_url":settings.STATIC_URL, "hostname": hostname}, context_instance=RequestContext(request))

@login_required()
def datasourceInventory(request, hostname, resource_name):
    server_info = read_server_info(hostname)
    if server_info:
        selected_datasource = None
        for datasource in server_info["datasources"]:
            if datasource['name'] == resource_name:
                selected_datasource = datasource
                break
        convert_keys_names(selected_datasource)
        return render_to_response('platforms/weblogic/datasource.html', {"base_url": settings.BASE_URL, "static_url":settings.STATIC_URL,"hostname":hostname, "datasource": datasource}, context_instance=RequestContext(request))
    else:
        return render_to_response('platforms/weblogic/datasource.html', {"base_url": settings.BASE_URL, "static_url":settings.STATIC_URL, "hostname": hostname}, context_instance=RequestContext(request))

@login_required()
def consoleInventory(request, hostname, resource_name):
    server_info = read_server_info(hostname)
    if server_info:
        db_console = server_info["console"]
        convert_keys_names(db_console)
        return render_to_response('platforms/weblogic/console.html', {"base_url": settings.BASE_URL, "static_url":settings.STATIC_URL,"hostname":hostname, "console": db_console}, context_instance=RequestContext(request))
    else:
        return render_to_response('platforms/weblogic/console.html', {"base_url": settings.BASE_URL, "static_url":settings.STATIC_URL, "hostname": hostname}, context_instance=RequestContext(request))

@login_required()
def nodeManagerInventory(request, hostname, resource_name):
    server_info = read_server_info(hostname)
    if server_info:
        #TODO: Modify and add managing of more than one nodemanager
        db_nodemanager = server_info["nodemanagers"][0]
        convert_keys_names(db_nodemanager)
        return render_to_response('platforms/weblogic/nodemanager.html', {"base_url": settings.BASE_URL, "static_url":settings.STATIC_URL,"hostname":hostname, "nodemanager": db_nodemanager}, context_instance=RequestContext(request))
    else:
        return render_to_response('platforms/weblogic/nodemanager.html', {"base_url": settings.BASE_URL, "static_url":settings.STATIC_URL, "hostname": hostname}, context_instance=RequestContext(request))

@login_required()
def applicationInventory(request, hostname, resource_name):
    server_info = read_server_info(hostname)
    if server_info:
        selected_app = None
        for app in server_info["applilist"]:
            if app['name'] == resource_name:
                selected_app = app
                break
        convert_keys_names(selected_app)
        return render_to_response('platforms/weblogic/application.html', {"base_url": settings.BASE_URL, "static_url":settings.STATIC_URL,"hostname":hostname, "application": selected_app}, context_instance=RequestContext(request))
    else:
        return render_to_response('platforms/weblogic/application.html', {"base_url": settings.BASE_URL, "static_url":settings.STATIC_URL, "hostname": hostname}, context_instance=RequestContext(request))


@login_required()
@permission_required('agent.call_mcollective', return_403=True)
def get_app_list(request, filters, type):
    return HttpResponse(get_apps_list(request.user, filters, type))

@login_required()
@permission_required('agent.call_mcollective', return_403=True)
def get_instance_list(request, filters):
    servers = extract_servers(filters, request.user)
    instances = []
    for server in servers:
        instances.extend(extract_instances_name(server.hostname))
    return HttpResponse(json.dumps({"errors":"", "instances":instances}))
    
@login_required()
@permission_required('agent.call_mcollective', return_403=True)
def get_deploy_form(request, dialog_name, action, filters):
    logger.debug('Rendering form')         
    return render_to_response('platforms/weblogic/deployform.html', {'action':action, 'filters':filters, 'form':DeployForm([]), 'dialog_name': dialog_name, 'base_url':settings.BASE_URL}, context_instance=RequestContext(request))

@login_required()
@permission_required('agent.call_mcollective', return_403=True)
def deploy_app(request, filters, dialog_name, xhr=None):
    if request.method == "POST":
        logger.debug("Recreating form")
        form = DeployForm(request.POST)

        #Check if the <xhr> var had something passed to it.
        if xhr == "xhr":
            #TODO: Try to use dynamic form validation
            clean = form.is_valid()
            rdict = {'bad':'false', 'filters':filters }
            try:
                appfile = request.POST['applist']
                app_type = request.POST['types']
                instancename = request.POST['instancename']
                appname = request.POST['appname']
                action = request.POST['action']
            except:
                appname=None
                app_type=None
            if appname and app_type and action:
                logger.debug("Parameters check: OK.")
                logger.debug("Calling MCollective to deploy %s application on %s filtered server" % (appfile, filters))
                response, content = callRestServer(request.user, filters, 'a7xows', action, 'appname=%s;instancename=%s;appfile=%s' %(appname, instancename, appfile), wait_response=True, use_task=True, use_backend_scheduler=True)
                if response.getStatus() == 200:
                    s_resps = []
                    for server_response in content:
                        if server_response.getStatusCode()==0:
                            if server_response.getData() and "data" in server_response.getData():
                                if "status" in server_response.getData()["data"]:
                                    s_resps.append({"server": server_response.getSender(), "response":server_response.getData()["data"]["status"]})
                                else:
                                    s_resps.append({"server": server_response.getSender(), "response":server_response.getData()["data"]["statusmsg"]})
                            else:
                                s_resps.append({"server": server_response.getSender(), "response":server_response.getStatusMessage()})
                        else:
                            s_resps.append({"server": server_response.getSender(), "message":server_response.getStatusMessage()})
                    rdict.update({"result":s_resps})
                else:
                    rdict.update({"result": "KO", "message": "Error communicating with server"})
                
                rdict.update({'dialog_name':dialog_name})
                # And send it off.
            else:
                rdict.update({'bad':'true'})
                d = {}
                # This was painful, but I can't find a better way to extract the error messages:
                for e in form.errors.iteritems():
                    d.update({e[0]:unicode(e[1])}) # e[0] is the id, unicode(e[1]) is the error HTML.
                # Bung all that into the dict
                rdict.update({'errs': d })
                # Make a json whatsit to send back.
                
            return HttpResponse(json.dumps(rdict, ensure_ascii=False), mimetype='application/javascript')
        # It's a normal submit - non ajax.
        else:
            if form.is_valid():
                # We don't accept non-ajax requests for the moment
                return HttpResponseRedirect("/")
    else:
        # It's not post so make a new form
        logger.warn("Cannot access this page using GET")
        raise Http404
    
@login_required()
@permission_required('agent.call_mcollective', return_403=True)
def get_log_form(request, dialog_name, action, filters):
    logger.debug('Rendering form')         
    return render_to_response('platforms/weblogic/logform.html', {'action':action, 'filters':filters, 'form':LogForm([]), 'dialog_name': dialog_name, 'base_url':settings.BASE_URL}, context_instance=RequestContext(request))

@login_required()
@permission_required('agent.call_mcollective', return_403=True)
def get_log(request, filters, dialog_name, xhr=None):
    if request.method == "POST":
        logger.debug("Recreating form")
        form = LogForm(request.POST)

        #Check if the <xhr> var had something passed to it.
        if xhr == "xhr":
            #TODO: Try to use dynamic form validation
            clean = form.is_valid()
            rdict = {'bad':'false', 'filters':filters }
            try:
                instancename = request.POST['instancename']
            except:
                instancename=None
            if instancename:
                logger.debug("Parameters check: OK.")
                logger.debug("Calling MCollective to get log on %s filtered server" % (filters))
                response, content = callRestServer(request.user, filters, 'a7xows', 'get_log', 'instancename=%s' % (instancename), wait_response=True, use_task=True, use_backend_scheduler=True)
                if response.getStatus() == 200:
                    s_resps = []
                    for server_response in content:
                        if server_response and server_response.getStatusCode() == 0 and server_response.getData():
                            log_file = None
                            if server_response.getData() and "logfile" in server_response.getData():
                                log_file = server_response.getData()["logfile"]
                            elif server_response.getData() and "data" in server_response.getData() and "logfile" in server_response.getData()["data"]:
                                log_file = server_response.getData()["data"]["logfile"]

                            if log_file:
                                logger.debug("Discovered log for server %s: %s" % (server_response.getSender(), log_file))
                                s_resps.append({"server": server_response.getSender(), "logfile":log_file})
                            else:
                                if server_response.getData() and "statusmsg" in server_response.getData():
                                    s_resps.append({"server": server_response.getSender(), "message":server_response.getData()["statusmsg"]})
                                else:    
                                    s_resps.append({"server": server_response.getSender(), "message":server_response.getStatusMessage()})
                    rdict.update({"result":s_resps})
                else:
                    rdict.update({"result": "KO", "message": "Error communicating with server"})
                
                rdict.update({'dialog_name':dialog_name})
                # And send it off.
            else:
                rdict.update({'bad':'true'})
                d = {}
                # This was painful, but I can't find a better way to extract the error messages:
                for e in form.errors.iteritems():
                    d.update({e[0]:unicode(e[1])}) # e[0] is the id, unicode(e[1]) is the error HTML.
                # Bung all that into the dict
                rdict.update({'errs': d })
                # Make a json whatsit to send back.
                
            return HttpResponse(json.dumps(rdict, ensure_ascii=False), mimetype='application/javascript')
        # It's a normal submit - non ajax.
        else:
            if form.is_valid():
                # We don't accept non-ajax requests for the moment
                return HttpResponseRedirect("/")
    else:
        # It's not post so make a new form
        logger.warn("Cannot access this page using GET")
        raise Http404
    
@login_required()
def get_log_file(request, file_name):
    logger.debug('Get Log file %s' % file_name)         
    log_file_content = read_file_log(file_name)
    return HttpResponse(json.dumps({"logfilecontent":log_file_content}, ensure_ascii=False), mimetype='application/javascript')

@login_required()
@permission_required('agent.call_mcollective', return_403=True)
def get_form(request, dialog_name, action, filters):
    logger.debug("Rendering %s form" % action)   
    if action == 'createinstance':   
        return render_to_response('platforms/weblogic/instanceform.html', {'action':action, 'filters':filters, 'form':InstanceForm([]), 'dialog_name': dialog_name, 'base_url':settings.BASE_URL}, context_instance=RequestContext(request))
    
@login_required()
@permission_required('agent.call_mcollective', return_403=True)
def create_instance(request, filters, dialog_name, xhr=None):
    if request.method == "POST":
        logger.debug("Recreating form")
        form = InstanceForm(request.POST)

        #Check if the <xhr> var had something passed to it.
        if xhr == "xhr":
            #TODO: Try to use dynamic form validation
            clean = form.is_valid()
            rdict = {'bad':'false', 'filters':filters }
            try:
                instancename = request.POST['instancename']
            except:
                instancename=None
            if instancename:
                logger.debug("Parameters check: OK.")
                logger.debug("Calling MCollective to create instance %s on %s filtered server" % (instancename, filters))
                response, content = callRestServer(request.user, filters, 'a7xows', 'createinstace', 'instancename=%s' %(instancename), wait_response=True, use_task=True, use_backend_scheduler=True)
                if response.getStatus() == 200:
                    s_resps = []
                    for server_response in content:
                        if server_response.getStatusCode()==0:
                            response_message = 'Instance Created'
                            if server_response.getData() and "statusmsg" in server_response.getData() and server_response.getData()["statusmsg"]!='OK':
                                response_message = server_response.getData()["statusmsg"]
                            elif server_response.getStatusMessage() and server_response.getStatusMessage()!='OK':
                                response_message = server_response.getStatusMessage()
                            s_resps.append({"server": server_response.getSender(), "response":response_message})
                        else:
                            s_resps.append({"server": server_response.getSender(), "message":server_response.getStatusMessage()})
                    rdict.update({"result":s_resps})
                else:
                    rdict.update({"result": "KO", "message": "Error communicating with server"})
                
                rdict.update({'dialog_name':dialog_name})
                # And send it off.
            else:
                rdict.update({'bad':'true'})
                d = {}
                # This was painful, but I can't find a better way to extract the error messages:
                for e in form.errors.iteritems():
                    d.update({e[0]:unicode(e[1])}) # e[0] is the id, unicode(e[1]) is the error HTML.
                # Bung all that into the dict
                rdict.update({'errs': d })
                # Make a json whatsit to send back.
                
            return HttpResponse(json.dumps(rdict, ensure_ascii=False), mimetype='application/javascript')
        # It's a normal submit - non ajax.
        else:
            if form.is_valid():
                # We don't accept non-ajax requests for the moment
                return HttpResponseRedirect("/")
    else:
        # It's not post so make a new form
        logger.warn("Cannot access this page using GET")
        raise Http404
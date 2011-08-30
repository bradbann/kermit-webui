function getExecutionForm(execution_dialog_name, agent, action, filters, response_container_name) {
	url = '/agent/action/get_dialog_form/' + agent + '/' + action + '/' + filters + '/' + execution_dialog_name + '/' + response_container_name + '/';
	$.ajax({
		// The link we are accessing.
		url : url,
		// The type of request.
		type : "get",
		// The type of data that is getting returned.
		dataType : "html",
		error : function() {
			//TODO: Show error message
			//$('#loading').hide();
			alert('error');
		},
		beforeSend : function() {
			//$('#loading').show();
		},
		complete : function() {
			//$('#loading').hide();
		},
		success : function(data) {
			if(data != 'None') {
				$("#" + execution_dialog_name).html(data);
				$("#" + execution_dialog_name).dialog({
					modal : true,
					title : agent + '-' + action + ' execution...',
					minHeight : 200,
					minWidth : 500
				});
				$("#" + execution_dialog_name).show();
			} else {
				callMcollective('/restapi/mcollective/' + filters + '/' + agent + '/' + action + '/', response_container_name);
			}

		}
	});
}

function sendRequestToMcollective(url, destination) {
	$("#" + destination).empty();

	$.ajax({
		// The link we are accessing.
		url : url,
		// The type of request.
		type : "get",
		// The type of data that is getting returned.
		dataType : "json",
		error : function() {
			//TODO: Show error message
			$('#loading').hide();
		},
		beforeSend : function() {
			$('#loading').show();
		},
		complete : function() {
			$('#loading').hide();
		},
		success : function(data) {
			$("#" + destination).empty();
			if(data.type == 'json') {
				for(i in data.response) {
					resp = data.response[i];
					content = '<strong>' + resp.sender + '</strong>';
					content += '<ul>';
					content += '<li> Status Code: ' + resp.statuscode + '</li>';
					content += '<li> Status Message: ' + resp.statusmsg + '</li>';
					content += '<li> Data: ' + JSON.stringify(resp.data) + '</li>';
					content += '</ul>';
					$(content).appendTo("#response-container");
				}
			} else if(data.type == 'html') {
				$("#" + destination).html(data.response);
			}
		}
	});
}

function callMcollective(url, destination) {
	sendRequestToMcollective(url, destination)
}

function callMcollectiveWithTemplateRsp(url, destination) {
	sendRequestToMcollective(url, destination)
}